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

    def create(self, user_id: int, job_description: str, assigned_amount: int, job_loc: str = None, job_status: str = None):
        job = Job(
            user_id=user_id,
            job_description=job_description,
            assigned_amount=assigned_amount,
            job_loc=job_loc,
            job_status=job_status
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update(self, job_id: int, job_description: str = None, assigned_amount: int = None, job_loc: str = None, job_status: str = None):
        job = self.get_by_id(job_id)
        if not job:
            return None
        
        if job_description is not None:
            job.job_description = job_description
        if assigned_amount is not None:
            job.assigned_amount = assigned_amount
        if job_loc is not None:
            job.job_loc = job_loc
        if job_status is not None:
            job.job_status = job_status
        
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

