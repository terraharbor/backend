from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    username: str
    disabled: Optional[bool] = None
    sha512_hash: str
    salt: str
    token: Optional[str] = None
    token_validity: Optional[int] = None
    isAdmin: Optional[bool] = None