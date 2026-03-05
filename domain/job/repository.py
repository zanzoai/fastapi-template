from infrastructure.db.models import Job

class JobRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, job_id: int):
        return self.db.query(Job).filter(Job.job_id == job_id).first()

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Job).offset(skip).limit(limit).all()

    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(Job).filter(Job.user_id == user_id).offset(skip).limit(limit).all()

    def create(self, user_id: int, task_title: str, polished_task: str, location_address: str,
               latitude: str, longitude: str, scheduled_at, duration_hours: int, duration_minutes: int,
               estimated_cost_pence: int, people_required: int, actions: str, tags: str,
               payment_mode: str, payment_status: str, currency: str, pickup_adress: str,
               pickup_latitude: str, pickup_longitude: str, assigned_zancrew_user_id: int = None,
               short_title: str = None, imp_notes: str = None, bucket: str = None,
               chat_room_id: str = None):
        job = Job(
            user_id=user_id,
            task_title=task_title,
            polished_task=polished_task,
            location_address=location_address,
            latitude=latitude,
            longitude=longitude,
            scheduled_at=scheduled_at,
            duration_hours=duration_hours,
            duration_minutes=duration_minutes,
            estimated_cost_pence=estimated_cost_pence,
            people_required=people_required,
            actions=actions,
            tags=tags,
            payment_mode=payment_mode,
            payment_status=payment_status,
            currency=currency,
            pickup_adress=pickup_adress,
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            assigned_zancrew_user_id=assigned_zancrew_user_id,
            short_title=short_title,
            imp_notes=imp_notes,
            bucket=bucket,
            chat_room_id=chat_room_id
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update(self, job_id: int, task_title: str = None, polished_task: str = None,
               location_address: str = None, latitude: str = None, longitude: str = None,
               scheduled_at = None, duration_hours: int = None, duration_minutes: int = None,
               estimated_cost_pence: int = None, assigned_zancrew_user_id: int = None,
               short_title: str = None, people_required: int = None, imp_notes: str = None,
               actions: str = None, tags: str = None, bucket: str = None,
               payment_mode: str = None, payment_status: str = None, currency: str = None,
               chat_room_id: str = None, pickup_adress: str = None,
               pickup_latitude: str = None, pickup_longitude: str = None, status: str = None):
        job = self.get_by_id(job_id)
        if not job:
            return None
        
        if task_title is not None:
            job.task_title = task_title
        if polished_task is not None:
            job.polished_task = polished_task
        if location_address is not None:
            job.location_address = location_address
        if latitude is not None:
            job.latitude = latitude
        if longitude is not None:
            job.longitude = longitude
        if scheduled_at is not None:
            job.scheduled_at = scheduled_at
        if duration_hours is not None:
            job.duration_hours = duration_hours
        if duration_minutes is not None:
            job.duration_minutes = duration_minutes
        if estimated_cost_pence is not None:
            job.estimated_cost_pence = estimated_cost_pence
        if assigned_zancrew_user_id is not None:
            job.assigned_zancrew_user_id = assigned_zancrew_user_id
        if short_title is not None:
            job.short_title = short_title
        if people_required is not None:
            job.people_required = people_required
        if imp_notes is not None:
            job.imp_notes = imp_notes
        if actions is not None:
            job.actions = actions
        if tags is not None:
            job.tags = tags
        if bucket is not None:
            job.bucket = bucket
        if payment_mode is not None:
            job.payment_mode = payment_mode
        if payment_status is not None:
            job.payment_status = payment_status
        if currency is not None:
            job.currency = currency
        if chat_room_id is not None:
            job.chat_room_id = chat_room_id
        if pickup_adress is not None:
            job.pickup_adress = pickup_adress
        if pickup_latitude is not None:
            job.pickup_latitude = pickup_latitude
        if pickup_longitude is not None:
            job.pickup_longitude = pickup_longitude
        if status is not None:
            job.status = status

        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job_id: int):
        job = self.get_by_id(job_id)
        if not job:
            return False
        
        self.db.delete(job)
        self.db.commit()
        return True
