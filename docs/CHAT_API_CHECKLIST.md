# Chat flow – API checklist

Base URL: `http://localhost:8000` (or your `BASE_URL`). All chat routes are under `/api/v1/chat/`.

## Prerequisites

- At least one **job** with `assigned_zancrew_user_id` set (task owner = `user_id`, assigned crew = `assigned_zancrew_user_id`).
- Use real `zan_user.user_id` and `zan_crew.zancrew_id` from your DB for the headers below.

---

## 1. Get (or create) chat room – as task owner (zan_user)

```bash
curl -s -X GET "http://localhost:8000/api/v1/chat/jobs/JOB_ID/room" \
  -H "X-Zan-User-Id: ZAN_USER_ID" \
  -H "X-Zan-Actor-Type: zan_user"
```

- **200**: Returns `{ "id": <chat_room_id>, "job_id": ..., "is_read_only": false, "created_at": "..." }`. Use `id` for message endpoints.
- **400**: Job not assigned.
- **403**: Not a participant (wrong user_id for this job).

---

## 2. Get chat room – as assigned crew (zan_crew)

```bash
curl -s -X GET "http://localhost:8000/api/v1/chat/jobs/JOB_ID/room" \
  -H "X-Zancrew-Id: ZANCREW_ID" \
  -H "X-Zan-Actor-Type: zan_crew"
```

- **200**: Same room payload. Confirms crew can access.

---

## 3. List messages (e.g. as zan_crew)

```bash
curl -s -X GET "http://localhost:8000/api/v1/chat/rooms/CHAT_ROOM_ID/messages?limit=20" \
  -H "X-Zancrew-Id: ZANCREW_ID" \
  -H "X-Zan-Actor-Type: zan_crew"
```

- **200**: `{ "messages": [...], "next_cursor": "..." or null, "has_more": false }`. Use `next_cursor` for older messages.

---

## 4. Send message – as zan_user

```bash
curl -s -X POST "http://localhost:8000/api/v1/chat/rooms/CHAT_ROOM_ID/messages" \
  -H "X-Zan-User-Id: ZAN_USER_ID" \
  -H "X-Zan-Actor-Type: zan_user" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from task owner"}'
```

- **201**: Returns the created message object.
- **403**: Not a participant, or room is read-only (job closed).

---

## 5. Send message – as zan_crew

```bash
curl -s -X POST "http://localhost:8000/api/v1/chat/rooms/CHAT_ROOM_ID/messages" \
  -H "X-Zancrew-Id: ZANCREW_ID" \
  -H "X-Zan-Actor-Type: zan_crew" \
  -H "Content-Type: application/json" \
  -d '{"content": "Crew replying"}'
```

---

## 6. Optional: pagination (older messages)

```bash
curl -s -X GET "http://localhost:8000/api/v1/chat/rooms/CHAT_ROOM_ID/messages?cursor=NEXT_CURSOR&limit=20" \
  -H "X-Zan-User-Id: ZAN_USER_ID" \
  -H "X-Zan-Actor-Type: zan_user"
```

Use the `next_cursor` from the previous list response.

---

## Automated check (script)

From the project root (with server running and at least one assigned job):

```bash
# Auto-pick an assigned job and run full flow
python scripts/chat_flow_check.py

# Or specify job and identities
python scripts/chat_flow_check.py --job-id 1 --zan-user-id 1 --zancrew-id 1

# Different host
BASE_URL=http://localhost:8000 python scripts/chat_flow_check.py
```

Requires: `pip install requests`.
