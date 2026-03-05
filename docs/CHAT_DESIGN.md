# Zanzo task-based chat – design and operations

## 1. Database schema (summary)

- **chat_rooms**: One row per job (`job_id` unique). Holds `is_read_only` (set when job is closed).
- **chat_participants**: Explicit membership per room with `participant_type` (`zan_user` | `zan_crew`) and either `zan_user_id` or `zancrew_id`. Ready for multiple crew later.
- **chat_messages**: Messages scoped by `chat_room_id`; sender stored as `sender_type` + `sender_zan_user_id` / `sender_zancrew_id`.
- **message_reads** (optional): Read receipts per (message, participant). Trade-offs below.

### Message reads – trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **No read tracking** | Simple, fewer writes, no extra tables | No “read” state in UI |
| **message_reads table** | Per-message read state, “last read” per participant | More writes, more storage; need to decide “read” semantics (e.g. on view vs on scroll) |
| **Last-read cursor per participant** | Single row per participant (e.g. “last_read_message_id”), cheap | Only “read up to here”, not per-message |

Recommendation: start without read receipts; add `message_reads` or a “last read” cursor when product needs it. Schema already has `message_reads` if you want to use it later.

---

## 2. Business rules (enforced on backend)

- **No chat when job is unassigned**  
  Chat room is created only when the job has `assigned_zancrew_user_id`. Room is created lazily on first `GET /api/v1/chat/jobs/{job_id}/room` by a participant.

- **Chat is read-only when job is closed**  
  When `job.status` is set to `closed`, the corresponding `chat_rooms.is_read_only` is set to `true`. Send-message API returns 403 if `is_read_only` is true.

- **Only participants can read/send**  
  Every chat endpoint resolves the current actor (zan_user or zan_crew) and checks membership in `chat_participants` before returning room, messages, or accepting a new message. Non-participants get 403.

- **No direct zan_user ↔ zan_crew chat**  
  All chat is job-scoped; the only way to talk is via a job’s single chat room.

---

## 3. API (FastAPI)

| Method | Path | Purpose |
|--------|------|--------|
| GET | `/api/v1/chat/jobs/{job_id}/room` | Get (or create) chat room for job; 400 if job unassigned, 403 if not participant |
| GET | `/api/v1/chat/rooms/{chat_room_id}/messages?cursor=&limit=` | Cursor-based list of messages (newest first); 403 if not participant |
| POST | `/api/v1/chat/rooms/{chat_room_id}/messages` | Send message; 403 if not participant or room read-only |

**Identity (current placeholder)**  
Requests must identify the actor via headers (replace with JWT + DB lookup in production):

- **Zan user (customer):** `X-Zan-User-Id: <zan_user.user_id>`, `X-Zan-Actor-Type: zan_user`
- **Zan crew:** `X-Zancrew-Id: <zan_crew.zancrew_id>`, `X-Zan-Actor-Type: zan_crew`

---

## 4. Supabase Realtime – subscribing to messages

Chat is job-centric; clients should subscribe by **chat_room_id** (returned from `GET .../room`).

### Enable Realtime on the table

In Supabase Dashboard:

1. **Database → Replication** (or **Realtime**): enable replication for `chat_messages` (and optionally `chat_rooms` if you want “room closed” updates).
2. Or via SQL (as a superuser / in migration):

```sql
alter publication supabase_realtime add table chat_messages;
```

### Subscribe to new messages for a room (client)

Using Supabase JS client (browser or Node):

```js
const channel = supabase
  .channel('chat-room-' + chatRoomId)
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'chat_messages',
      filter: 'chat_room_id=eq.' + chatRoomId,
    },
    (payload) => {
      // payload.new has the new row (id, chat_room_id, sender_type, content, created_at, ...)
      appendMessage(payload.new);
    }
  )
  .subscribe();
```

- Use the **same** `chat_room_id` you got from `GET /api/v1/chat/jobs/{job_id}/room`.
- Unsubscribe when leaving the screen: `supabase.removeChannel(channel)`.

### Best practices

- **One channel per room**  
  Subscribe only to the room the user is viewing; avoid one global “all messages” channel.

- **Auth**  
  Realtime uses the Supabase anon key and RLS. Ensure **Row Level Security (RLS)** on `chat_messages` (and `chat_participants`) so that only participants can read; otherwise anyone with the anon key could listen to any room. Our API already enforces participation; Realtime adds a second layer if you query Supabase from the client.

- **Reconciliation**  
  On reconnect or when opening the room, refetch the last N messages via the API (cursor-based) and then subscribe to Realtime for new inserts. This avoids gaps.

- **Ordering**  
  Messages are ordered by `(created_at, id)`. The API returns newest first; Realtime only sends new rows. Client should append and sort if needed.

---

## 5. Indexing strategy

- **chat_rooms**: Unique index on `job_id` (already in migration).
- **chat_participants**: Indexes on `chat_room_id`, `zan_user_id`, `zancrew_id` (partial where not null) and unique partial indexes so one zan_user / zancrew per room (already in migration).
- **chat_messages**: Index on `(chat_room_id, created_at)` (or `(chat_room_id, id)`) for cursor pagination and Realtime filters (already in migration).

No extra indexes needed for the current API shape.

---

## 6. Avoiding common mistakes

- **Do not** create a chat room on job creation; create it when the job is assigned (we do it lazily on first room fetch).
- **Do not** allow sending when `chat_rooms.is_read_only` is true; the API already blocks this.
- **Do not** trust the client for “who am I?” – resolve actor from JWT/session and check `chat_participants` on every request.
- **Do not** expose a “list all rooms” for a user without scoping to jobs they own or are assigned to; current design only exposes room by `job_id` and then checks participation.

---

## 7. Scaling and future work

- **Attachments**  
  Add an `attachments` JSONB column on `chat_messages` (or a separate `chat_message_attachments` table) and store Supabase Storage paths; generate signed URLs from the API.

- **System messages**  
  Already supported: `sender_type = 'system'`, both sender IDs null. Use for “Job assigned”, “Job closed”, etc. Backend can insert these when job is assigned/closed.

- **Multiple crew per job**  
  Add more rows to `chat_participants` with `participant_type = 'zan_crew'` and different `zancrew_id`s when you support multiple assignees. No schema change required.

- **Push notifications**  
  On insert into `chat_messages`, publish to a queue (e.g. Redis/SQS) and have a worker send push via FCM/APNs. Keep Realtime for live UI and push for background/offline.

- **Rate limiting**  
  Add per-actor or per-room rate limits on send-message to avoid abuse.
