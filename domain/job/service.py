class JobService:
    def __init__(self, repo):
        self.repo = repo

    def create_job(self, user_id: int, job_description: str, assigned_amount: int, job_loc: str = None, job_status: str = None):
        return self.repo.create(user_id, job_description, assigned_amount, job_loc, job_status)

    def get_job(self, job_id: int):
        job = self.repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        return job

    def get_all_jobs(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip, limit)

    def get_jobs_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.repo.get_by_user_id(user_id, skip, limit)

    def update_job(self, job_id: int, job_description: str = None, assigned_amount: int = None, job_loc: str = None, job_status: str = None):
        job = self.repo.update(job_id, job_description, assigned_amount, job_loc, job_status)
        if not job:
            raise ValueError("Job not found")
        return job

    def delete_job(self, job_id: int):
        success = self.repo.delete(job_id)
        if not success:
            raise ValueError("Job not found")
        return {"message": "Job deleted successfully"}

