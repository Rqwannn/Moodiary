from pydantic import BaseModel
from typing import List, Union, Optional

class DeleteRequest(BaseModel):
    ids: Union[str, List[str]]
    task: str
    
class GetUserData(BaseModel):
    email: Optional[str] = None
    
class UpdateUserData(BaseModel):
    uid: Optional[str] = None
    nama: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    tipe_keperibadian: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class InferenceModelInput(BaseModel):
    text: str = None
    history_notes: Optional[List[str]] = None