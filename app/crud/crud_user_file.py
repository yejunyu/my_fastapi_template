from app.models.user_file import UserFile
from app.crud.base import CRUDBase
from app.schemas.user_file import UserFileCreate, UserFileUpdate


class CRUDUserFile(CRUDBase[UserFile, UserFileCreate, UserFileUpdate]):
    pass


user_file = CRUDUserFile(UserFile)
