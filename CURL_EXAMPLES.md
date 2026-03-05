# cURL Examples

Base URL: `http://localhost:8000/api/v1`

---

## Auth

### Send OTP
```bash
curl -X POST http://localhost:8000/api/v1/auth/phone/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

### Verify OTP
```bash
curl -X POST http://localhost:8000/api/v1/auth/phone/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210", "token": "123456"}'
```

### Resend OTP
```bash
curl -X POST http://localhost:8000/api/v1/auth/phone/resend-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

---

## Zan Users

### Create Zan User
```bash
curl -X POST http://localhost:8000/api/v1/zan-users \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  }'
```

### Get All Zan Users
```bash
curl -X GET "http://localhost:8000/api/v1/zan-users?skip=0&limit=10"
```

### Get Zan User by ID
```bash
curl -X GET http://localhost:8000/api/v1/zan-users/1
```

### Get Zan User by Email
```bash
curl -X GET "http://localhost:8000/api/v1/zan-users/email/john@example.com"
```

### Update Zan User
```bash
curl -X PUT http://localhost:8000/api/v1/zan-users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543211",
    "first_name": "Jane",
    "email": "jane@example.com"
  }'
```

### Delete Zan User
```bash
curl -X DELETE http://localhost:8000/api/v1/zan-users/1
```

---

## Zan Crew

### Create Zan Crew
```bash
curl -X POST http://localhost:8000/api/v1/zan-crew \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "city": "Mumbai",
    "state": "Maharashtra"
  }'
```

### Get Zan Crew by Phone
```bash
curl -X GET "http://localhost:8000/api/v1/zan-crew/phone/+919876543210"
```

### Get Zan Crew by ID
```bash
curl -X GET http://localhost:8000/api/v1/zan-crew/1
```

---

## Jobs

### Create Job
```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "task_title": "Cleaning",
    "polished_task": "House cleaning",
    "location_address": "123 Main St",
    "latitude": "12.34",
    "longitude": "56.78",
    "scheduled_at": "2025-03-10T10:00:00",
    "duration_hours": 2,
    "duration_minutes": 0,
    "estimated_cost_pence": 5000,
    "people_required": 1,
    "actions": "clean",
    "tags": "cleaning",
    "payment_mode": "card",
    "payment_status": "pending",
    "currency": "GBP",
    "status": "open",
    "pickup_adress": "123 Main St",
    "pickup_latitude": "12.34",
    "pickup_longitude": "56.78"
  }'
```

### Get All Jobs
```bash
curl -X GET "http://localhost:8000/api/v1/jobs?skip=0&limit=10"
```

---

## Health

```bash
curl -X GET http://localhost:8000/api/v1/health
```

---

## Root

```bash
curl -X GET http://localhost:8000/
```
