import yaml
from pathlib import Path

class ConfigManagerYaml:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config: dict[str, any] = {}
        self.load_config()

    def load_config(self) -> None:
        """加载YAML配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}

    def save_config(self) -> None:
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, sort_keys=False)

    def get(self, key: str, default:list = None) -> any:
        """获取配置项 实现 config['server.host'] 的访问方式"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: any) -> None:
        """设置配置项"""
        keys = key.split('.')
        current = self.config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self.save_config()

    def delete(self, key: str) -> bool:
        """删除配置项"""
        keys = key.split('.')
        current = self.config
        
        try:
            for k in keys[:-1]:
                current = current[k]
            
            del current[keys[-1]]
            self.save_config()
            return True
        except (KeyError, TypeError):
            return False

    def __getitem__(self, key: str) -> any:
        return self.get(key)

    def __setitem__(self, key: str, value: any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.delete(key)
        
if __name__ == '__main__':
    # 初始化配置管理器
    config = ConfigManagerYaml('config.yaml')

    # 获取配置项 __getitem__
    print(config['server.host'])  # 输出: 0.0.0.0
    print(config.get('ai.openai.api_key'))  # 输出: 1
    print(config.get('ai.openai')) 

    # 修改配置项
    # config['server.port'] = 3000
    # config.set('ai.new_provider.api_key', 'new_key_value')

    # # 添加新配置项
    # config['new_section'] = {
    #     'key1': 'value1',
    #     'key2': {
    #         'subkey': 'subvalue'
    #     }
    # }

    # # 删除配置项
    # del config['database.neo4j']
    # config.delete('ai.aliyun')

    # 检查配置是否已保存
    config.load_config()  # 重新加载确认更改
    print(config['server.port'])  # 输出: 2666