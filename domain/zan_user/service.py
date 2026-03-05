class ZanUserService:
    def __init__(self, repo, zan_crew_repo=None):
        self.repo = repo
        self.zan_crew_repo = zan_crew_repo

    def create_zan_user(self, phone: str, first_name: str = None, last_name: str = None,
                       email: str = None, address: str = None, is_zancrew: str = "false", zancrew_id: int = None):
        # Phone must be unique
        if self.repo.get_by_phone(phone):
            raise ValueError("User with this phone number already exists")
        # Email must be unique when provided (optional)
        if email and self.repo.get_by_email(email):
            raise ValueError("User with this email already exists")

        return self.repo.create(phone, first_name, last_name, email, address, is_zancrew, zancrew_id)

    def get_zan_user(self, user_id: int):
        zan_user = self.repo.get_by_id(user_id)
        if not zan_user:
            raise ValueError("ZanUser not found")
        return zan_user

    def get_zan_user_by_email(self, email: str):
        zan_user = self.repo.get_by_email(email)
        if not zan_user:
            raise ValueError("ZanUser not found")
        return zan_user

    def get_all_zan_users(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip, limit)

    def get_zan_users_by_zancrew(self, zancrew_id: int, skip: int = 0, limit: int = 100):
        return self.repo.get_by_zancrew_id(zancrew_id, skip, limit)

    def update_zan_user(self, user_id: int, first_name: str = None, last_name: str = None,
                       email: str = None, phone: str = None, address: str = None,
                       is_zancrew: str = None, zancrew_id: int = None):
        # Phone must be unique (when updating to a new phone)
        if phone is not None:
            existing = self.repo.get_by_phone(phone)
            if existing and existing.user_id != user_id:
                raise ValueError("User with this phone number already exists")
        # Email must be unique when provided (optional)
        if email is not None:
            existing = self.repo.get_by_email(email)
            if existing and existing.user_id != user_id:
                raise ValueError("User with this email already exists")

        zan_user = self.repo.update(user_id, first_name, last_name, email, phone,
                                    address, is_zancrew, zancrew_id)
        if not zan_user:
            raise ValueError("ZanUser not found")

        # Cascade phone update to zan_crew if phone was updated
        if phone is not None and self.zan_crew_repo:
            self.zan_crew_repo.update_phone_by_user_id(user_id, phone)
        
        return zan_user

    def delete_zan_user(self, user_id: int):
        success = self.repo.delete(user_id)
        if not success:
            raise ValueError("ZanUser not found")
        return {"message": "ZanUser deleted successfully"}

