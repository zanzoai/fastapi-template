class UserService:
    def __init__(self, repo):
        self.repo = repo

    def create_user(self, email: str):
        if self.repo.get_by_email(email):
            raise ValueError("User already exists")

        return self.repo.create(email)
