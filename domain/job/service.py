from domain.zan_user.repository import ZanUserRepository
from domain.chat.repository import ChatRoomRepository
from core.cache import (
    cache_get,
    cache_set,
    invalidate_job_cache,
)
from core.config import (
    CACHE_TTL_JOBS_LIST,
    CACHE_TTL_JOB_DETAIL,
    CACHE_TTL_JOBS_BY_USER,
)
from domain.job.schemas import JobResponse

class JobService:
    def __init__(self, repo, zan_user_repo=None, chat_room_repo=None):
        self.repo = repo
        self.zan_user_repo = zan_user_repo
        self.chat_room_repo = chat_room_repo

    def create_job(self, user_id: int, task_title: str, polished_task: str, location_address: str,
                   latitude: str, longitude: str, scheduled_at, duration_hours: int, duration_minutes: int,
                   estimated_cost_pence: int, people_required: int, actions: str, tags: str,
                   payment_mode: str, payment_status: str, currency: str, pickup_adress: str,
                   pickup_latitude: str, pickup_longitude: str, assigned_zancrew_user_id: int = None,
                   short_title: str = None, imp_notes: str = None, bucket: str = None,
                   chat_room_id: str = None):
        # Validate user_id exists in zan_user table
        if self.zan_user_repo:
            zan_user = self.zan_user_repo.get_by_id(user_id)
            if not zan_user:
                raise ValueError(f"User with user_id {user_id} not found in zan_user table")
        
        job = self.repo.create(
            user_id, task_title, polished_task, location_address, latitude, longitude,
            scheduled_at, duration_hours, duration_minutes, estimated_cost_pence,
            people_required, actions, tags, payment_mode, payment_status, currency,
            pickup_adress, pickup_latitude, pickup_longitude, assigned_zancrew_user_id,
            short_title, imp_notes, bucket, chat_room_id
        )
        
        # Invalidate cache after creating a new job
        invalidate_job_cache(user_id=user_id)
        
        return job

    def get_job(self, job_id: int):
        # Try to get from cache first
        cache_key = f"job:detail:{job_id}"
        cached_job = cache_get(cache_key)
        if cached_job is not None:
            # Convert dict back to JobResponse model
            return JobResponse(**cached_job)
        
        job = self.repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        
        # Convert to JobResponse model
        job_response = JobResponse.model_validate(job)
        # Convert to dict for caching
        job_dict = job_response.model_dump()
        cache_set(cache_key, job_dict, CACHE_TTL_JOB_DETAIL)
        
        return job_response

    def get_all_jobs(self, skip: int = 0, limit: int = 100):
        # Try to get from cache first
        cache_key = f"job:list:skip:{skip}:limit:{limit}"
        cached_jobs = cache_get(cache_key)
        if cached_jobs is not None:
            # Convert list of dicts back to JobResponse models
            return [JobResponse(**job_dict) for job_dict in cached_jobs]
        
        jobs = self.repo.get_all(skip, limit)
        
        # Convert to JobResponse models for consistency
        jobs_response = [JobResponse.model_validate(job) for job in jobs]
        # Convert to list of dicts for caching
        jobs_dict = [job.model_dump() for job in jobs_response]
        cache_set(cache_key, jobs_dict, CACHE_TTL_JOBS_LIST)
        
        return jobs_response

    def get_jobs_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        # Validate user_id exists in zan_user table
        if self.zan_user_repo:
            zan_user = self.zan_user_repo.get_by_id(user_id)
            if not zan_user:
                raise ValueError(f"User with user_id {user_id} not found in zan_user table")
        
        # Try to get from cache first
        cache_key = f"job:user:{user_id}:skip:{skip}:limit:{limit}"
        cached_jobs = cache_get(cache_key)
        if cached_jobs is not None:
            # Convert list of dicts back to JobResponse models
            return [JobResponse(**job_dict) for job_dict in cached_jobs]
        
        jobs = self.repo.get_by_user_id(user_id, skip, limit)
        
        # Convert to JobResponse models for consistency
        jobs_response = [JobResponse.model_validate(job) for job in jobs]
        # Convert to list of dicts for caching
        jobs_dict = [job.model_dump() for job in jobs_response]
        cache_set(cache_key, jobs_dict, CACHE_TTL_JOBS_BY_USER)
        
        return jobs_response

    def update_job(self, job_id: int, task_title: str = None, polished_task: str = None,
                   location_address: str = None, latitude: str = None, longitude: str = None,
                   scheduled_at = None, duration_hours: int = None, duration_minutes: int = None,
                   estimated_cost_pence: int = None, assigned_zancrew_user_id: int = None,
                   short_title: str = None, people_required: int = None, imp_notes: str = None,
                   actions: str = None, tags: str = None, bucket: str = None,
                   payment_mode: str = None, payment_status: str = None, currency: str = None,
                   chat_room_id: str = None, pickup_adress: str = None,
                   pickup_latitude: str = None, pickup_longitude: str = None, status: str = None):
        # Get the job first to know the user_id for cache invalidation
        existing_job = self.repo.get_by_id(job_id)
        if not existing_job:
            raise ValueError("Job not found")

        user_id = existing_job.user_id

        job = self.repo.update(
            job_id,
            task_title=task_title,
            polished_task=polished_task,
            location_address=location_address,
            latitude=latitude,
            longitude=longitude,
            scheduled_at=scheduled_at,
            duration_hours=duration_hours,
            duration_minutes=duration_minutes,
            estimated_cost_pence=estimated_cost_pence,
            assigned_zancrew_user_id=assigned_zancrew_user_id,
            short_title=short_title,
            people_required=people_required,
            imp_notes=imp_notes,
            actions=actions,
            tags=tags,
            bucket=bucket,
            payment_mode=payment_mode,
            payment_status=payment_status,
            currency=currency,
            chat_room_id=chat_room_id,
            pickup_adress=pickup_adress,
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            status=status,
        )
        if not job:
            raise ValueError("Job not found")

        # When job is closed, make chat room read-only
        if status == "closed" and self.chat_room_repo:
            room = self.chat_room_repo.get_by_job_id(job_id)
            if room:
                room.is_read_only = True
                self.chat_room_repo.db.commit()

        # Invalidate cache after updating
        invalidate_job_cache(job_id=job_id, user_id=user_id)

        return job

    def delete_job(self, job_id: int):
        # Get the job first to know the user_id for cache invalidation
        existing_job = self.repo.get_by_id(job_id)
        if not existing_job:
            raise ValueError("Job not found")
        
        user_id = existing_job.user_id
        
        success = self.repo.delete(job_id)
        if not success:
            raise ValueError("Job not found")
        
        # Invalidate cache after deleting
        invalidate_job_cache(job_id=job_id, user_id=user_id)
        
        return {"message": "Job deleted successfully"}
