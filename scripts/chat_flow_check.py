#!/usr/bin/env python3
"""
Cross-check chat flow via APIs.

Usage:
  # Use an existing assigned job (auto-detect from GET /jobs)
  python scripts/chat_flow_check.py

  # Or pass job_id and identities explicitly (e.g. from your DB)
  python scripts/chat_flow_check.py --job-id 1 --zan-user-id 1 --zancrew-id 1

  # Custom base URL
  BASE_URL=http://localhost:8000 python scripts/chat_flow_check.py
"""
import argparse
import os
import sys

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
API = f"{BASE_URL}/api/v1"


def main():
    p = argparse.ArgumentParser(description="Chat flow API check")
    p.add_argument("--job-id", type=int, help="Job ID (must have assigned_zancrew_user_id)")
    p.add_argument("--zan-user-id", type=int, help="zan_user.user_id (task owner)")
    p.add_argument("--zancrew-id", type=int, help="zan_crew.zancrew_id (assigned crew)")
    p.add_argument("--base-url", default=BASE_URL, help="API base URL")
    args = p.parse_args()

    base = args.base_url or BASE_URL
    api = f"{base}/api/v1"

    job_id = args.job_id
    user_id = args.zan_user_id
    zancrew_id = args.zancrew_id

    # Resolve job and identities if not all provided
    if job_id is None or user_id is None or zancrew_id is None:
        r = requests.get(f"{api}/jobs", timeout=10)
        r.raise_for_status()
        jobs = r.json()
        assigned = [j for j in jobs if j.get("assigned_zancrew_user_id") is not None]
        if not assigned:
            print("No assigned jobs found. Create a job and set assigned_zancrew_user_id (e.g. via PUT /api/v1/jobs/{id}).")
            print("Example: PUT /api/v1/jobs/1 with body { \"assigned_zancrew_user_id\": 1 }")
            sys.exit(1)
        j = assigned[0]
        job_id = j["job_id"]
        user_id = user_id or j["user_id"]
        zancrew_id = zancrew_id or j["assigned_zancrew_user_id"]
        print(f"Using job_id={job_id}, user_id (zan_user)={user_id}, zancrew_id={zancrew_id}")
    else:
        # Verify job exists and is assigned
        r = requests.get(f"{api}/jobs/{job_id}", timeout=10)
        if r.status_code != 200:
            print(f"Job {job_id} not found or error: {r.status_code} {r.text}")
            sys.exit(1)
        j = r.json()
        if not j.get("assigned_zancrew_user_id"):
            print(f"Job {job_id} has no assigned crew. Assign via PUT /api/v1/jobs/{job_id}")
            sys.exit(1)

    headers_zan_user = {
        "X-Zan-User-Id": str(user_id),
        "X-Zan-Actor-Type": "zan_user",
        "Content-Type": "application/json",
    }
    headers_zan_crew = {
        "X-Zancrew-Id": str(zancrew_id),
        "X-Zan-Actor-Type": "zan_crew",
        "Content-Type": "application/json",
    }

    print("\n--- 1. Get (or create) chat room as zan_user (task owner) ---")
    r = requests.get(f"{api}/chat/jobs/{job_id}/room", headers=headers_zan_user, timeout=10)
    if r.status_code != 200:
        print(f"FAIL: {r.status_code} {r.text}")
        sys.exit(1)
    room = r.json()
    chat_room_id = room["id"]
    print(f"OK: room_id={chat_room_id}, job_id={room['job_id']}, is_read_only={room['is_read_only']}")

    print("\n--- 2. Get same room as zan_crew (assigned crew) ---")
    r = requests.get(f"{api}/chat/jobs/{job_id}/room", headers=headers_zan_crew, timeout=10)
    if r.status_code != 200:
        print(f"FAIL: {r.status_code} {r.text}")
        sys.exit(1)
    print("OK: crew can access room")

    print("\n--- 3. Send message as zan_user ---")
    r = requests.post(
        f"{api}/chat/rooms/{chat_room_id}/messages",
        headers=headers_zan_user,
        json={"content": "Hello from task owner"},
        timeout=10,
    )
    if r.status_code != 201:
        print(f"FAIL: {r.status_code} {r.text}")
        sys.exit(1)
    msg1 = r.json()
    print(f"OK: message id={msg1['id']}, sender_type={msg1['sender_type']}")

    print("\n--- 4. List messages as zan_crew ---")
    r = requests.get(f"{api}/chat/rooms/{chat_room_id}/messages", headers=headers_zan_crew, timeout=10)
    if r.status_code != 200:
        print(f"FAIL: {r.status_code} {r.text}")
        sys.exit(1)
    page = r.json()
    print(f"OK: {len(page['messages'])} message(s), has_more={page['has_more']}")
    for m in page["messages"]:
        print(f"  - [{m['sender_type']}] {m['content'][:50]}")

    print("\n--- 5. Send message as zan_crew ---")
    r = requests.post(
        f"{api}/chat/rooms/{chat_room_id}/messages",
        headers=headers_zan_crew,
        json={"content": "Hi, crew here. On it."},
        timeout=10,
    )
    if r.status_code != 201:
        print(f"FAIL: {r.status_code} {r.text}")
        sys.exit(1)
    msg2 = r.json()
    print(f"OK: message id={msg2['id']}, sender_type={msg2['sender_type']}")

    print("\n--- 6. List messages again as zan_user (cursor optional) ---")
    r = requests.get(
        f"{api}/chat/rooms/{chat_room_id}/messages",
        headers=headers_zan_user,
        params={"limit": 10},
        timeout=10,
    )
    if r.status_code != 200:
        print(f"FAIL: {r.status_code} {r.text}")
        sys.exit(1)
    page = r.json()
    print(f"OK: {len(page['messages'])} message(s)")
    for m in page["messages"]:
        print(f"  - [{m['sender_type']}] {m['content'][:50]}")

    print("\n--- Chat flow check passed ---")


if __name__ == "__main__":
    main()
