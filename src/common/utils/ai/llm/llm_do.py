from pydantic import BaseModel, Field, field_validator


# 模型配置对象
class ModelConfig(BaseModel):
    model: str = Field(..., description="模型标识名称")
    # 配置
    temperature: float = Field(0.5, ge=0, le=2, description="生成温度系数")
    max_tokens: int = Field(8192, gt=0, description="最大生成token数")
    timeout: int = Field(60, gt=0, description="请求超时时间(秒)")



class OpenAIConfig(ModelConfig):
    """OpenAI模型配置"""
    url: str | None = Field(None, description="API基础URL")
    api_key: str | None = Field(None, description="API访问密钥")


class OllamaConfig(ModelConfig):
    """Ollama本地模型配置"""
    url: str | None = Field(None, description="API基础URL")
    
class AWSConfig(ModelConfig):
    """AWS模型配置"""
    service_name: str = Field(..., description="AWS服务名称")
    region_name: str = Field(..., description="AWS区域名称")
    aws_access_key_id: str = Field(..., description="AWS访问密钥ID")
    aws_secret_access_key: str = Field(..., description="AWS访问密钥")
    



# # 上下文配置对象
# class ContextConfig(BaseModel):
#     max_length: int = 1024 # 上下文最大长度
#     overlap: int = 64 # 上下文重叠长度
