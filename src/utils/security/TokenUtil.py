from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request
from passlib.context import CryptContext
import jwt
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenUtil:

    def __init__(self, SECRET_KEY="19d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"):
        # 加密密钥
        self.SECRET_KEY = SECRET_KEY
        # 加密方式
        self.ALGORITHM = "HS256"
        # 过期时间
        self.EXPIRE_MINUTES = timedelta(minutes=30)
        # 加密
        # 密码加密 Header和Payload部分分别进行Base64Url编码成消息字符串。
        # 使用指定的算法（例如HMAC SHA256）和密钥对消息字符串进行签名
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # pwd_context.hash(password)

    def data2token(self, data: dict)-> Token:
        """
        创建一个带有过期时间的 JWT。
        :param data: 需要编码到 JWT 中的数据。
        :return: 编码后的 JWT 字符串。
        """
        expire = datetime.now(timezone.utc) + self.EXPIRE_MINUTES
        data.update({"exp": expire})
        # 加密
        encoded_jwt = jwt.encode(data, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return Token(access_token=encoded_jwt, token_type="Bearer")

    def token2data(self, request: Request):
        """
        解码 JWT 并返回数据。
        :param request: HTTP 请求对象。
        :return: 解码后的数据。
        :raises HTTPException: 如果无法验证凭据或 JWT 已过期。
        """
        # 从请求头中获取 Bearer 令牌
        authorization_header = request.headers.get("Authorization")
        if authorization_header is None:
            raise HTTPException(
                status_code=401,
                detail="Missing Authorization Header",
                headers={"WWW-Authenticate": "Bearer"}
            )
        # 假设 Token 格式为 "Bearer <token>"
        token_type, _, token = authorization_header.partition(" ")
        if token_type != "Bearer":
            raise HTTPException(status_code=401, detail="无效的Token")
        try:
            # 解码 JWT
            data_decoded = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return data_decoded
        except jwt.exceptions.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

    def update_token(self, old_request: Request):
        """
        更新 JWT 令牌。
        :param old_request: 包含旧 JWT 令牌的请求对象。
        :return: 新的 JWT 令牌。
        :raises HTTPException: 如果旧的 JWT 令牌无效或已过期。
        """
        try:
            # 验证旧的 JWT 令牌
            old_data = self.token2data(old_request)
            # 生成新的 JWT 令牌
            new_token = self.data2token(old_data)
            return new_token
        except HTTPException as e:
            raise e

# 示例用法
if __name__ == "__main__":
    
    import time
    token_util = TokenUtil()
    
    # 创建 JWT
    data = {"sub": "test123"}
    token = token_util.data2token(data)
    print(f"Generated Token: {token}")
    
    # 解码 JWT
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    
    class MockRequest(StarletteRequest):
        headers = {"Authorization": f"Bearer {token.access_token}"}
    
    mock_request = MockRequest(scope={"type": "http"})
    try:
        decoded_data = token_util.token2data(mock_request)
        print(f"Decoded Data: {decoded_data}")
    except HTTPException as e:
        print(f"Error: {e.detail}")

    # 更新 JWT
    try:
        time.sleep(1)  # 等待一段时间以使令牌更新依赖时间戳不一致
        new_token = token_util.update_token(mock_request)
        print(f"Updated Token: {new_token}")
        
        print(f"token是否一致: {token.access_token == new_token.access_token}")
    except HTTPException as e:
        print(f"Error: {e.detail}")
        
    # 多对消息字符串和签名组可以提供更多数据点，但推导出SECRET_KEY仍然是极其困难的 较为安全
        
    