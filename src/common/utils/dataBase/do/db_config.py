from pydantic import BaseModel, Field, field_validator


# 模型配置对象
class DBConfig(BaseModel):
    database: str = Field(..., description="数据库名")
    # charset: str = Field("utf8mb4", description="数据库字符集")
class PostgresConfig(DBConfig):
    """Postgres数据库配置"""
    host: str = Field(..., description="数据库地址")
    port: int = Field(..., description="数据库端口")
    user: str = Field(..., description="数据库用户名")
    password: str = Field(..., description="数据库密码")

class SqliteConfig(DBConfig):
    """Sqlite数据库配置"""
    dir: str = Field(..., description="路径")
    # 尾标
    suffix: str = Field(".db", description="数据库文件后缀")
    

