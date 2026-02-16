from infrastructure.db.models import ZanUser

class ZanUserRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, user_id: int):
        return self.db.query(ZanUser).filter(ZanUser.user_id == user_id).first()

    def get_by_email(self, email: str):
        return self.db.query(ZanUser).filter(ZanUser.email == email).first()

    def get_by_phone(self, phone: str):
        return self.db.query(ZanUser).filter(ZanUser.phone == phone).first()

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(ZanUser).offset(skip).limit(limit).all()

    def get_by_zancrew_id(self, zancrew_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(ZanUser).filter(ZanUser.zancrew_id == zancrew_id).offset(skip).limit(limit).all()

    def create(self, phone: str, first_name: str = None, last_name: str = None, 
               email: str = None, address: str = None, is_zancrew: str = "false", zancrew_id: int = None):
        zan_user = ZanUser(
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            is_zancrew=is_zancrew,
            zancrew_id=zancrew_id
        )
        self.db.add(zan_user)
        self.db.flush()  # get PK without committing; get_db will commit
        self.db.refresh(zan_user)
        return zan_user

    def update(self, user_id: int, first_name: str = None, last_name: str = None, 
               email: str = None, phone: str = None, address: str = None, 
               is_zancrew: str = None, zancrew_id: int = None):
        zan_user = self.get_by_id(user_id)
        if not zan_user:
            return None
        
        if first_name is not None:
            zan_user.first_name = first_name
        if last_name is not None:
            zan_user.last_name = last_name
        if email is not None:
            zan_user.email = email
        if phone is not None:
            zan_user.phone = phone
        if address is not None:
            zan_user.address = address
        if is_zancrew is not None:
            zan_user.is_zancrew = is_zancrew
        if zancrew_id is not None:
            zan_user.zancrew_id = zancrew_id
        
        self.db.flush()
        self.db.refresh(zan_user)
        return zan_user

    def delete(self, user_id: int):
        zan_user = self.get_by_id(user_id)
        if not zan_user:
            return False
        
        self.db.delete(zan_user)
        self.db.flush()
        return True

