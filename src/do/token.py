from enum import Enum
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenType(Enum):
    tel = "tel"
    email = "java"
    out_token = "out_token"




