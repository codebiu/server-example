
from functools import wraps
def Dao(func):
    """
    自动事务装饰器（使用async with管理会话）：
    1. 支持嵌套事务
    2. 自动检测是否需要提交
    3. 支持手动控制事务
    4. 使用async with确保资源释放
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # 检查是否已有有效会话
        existing_session = getattr(self, 'session', None)
        
        if existing_session and hasattr(existing_session, 'is_active') and existing_session.is_active:
            # 使用现有会话
            return await func(self, *args, **kwargs)
        
        # 创建新会话并管理其生命周期
        async with self.session_factory() as session:
            setattr(self, 'session', session)
            try:
                async with session.begin():
                    result = await func(self, *args, **kwargs)
                    return result
            except Exception as e:
                print(f"数据库操作失败: {e}")
                if hasattr(session, 'in_transaction') and session.in_transaction():
                    await session.rollback()
                raise
            finally:
                delattr(self, 'session')  # 清理会话引用
    
    return wrapper


def transactional():
    """
    Service层事务装饰器
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 检查是否已有session
            if not hasattr(self, 'session') or not hasattr(self.session, 'commit'):
                async with self.session_factory() as session:
                    self.session = session
                    try:
                        result = await func(self, *args, **kwargs)
                        await session.commit()
                        return result
                    except Exception:
                        await session.rollback()
                        raise
            else:
                return await func(self, *args, **kwargs)
        return wrapper
    return decorator