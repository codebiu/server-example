import re

class SimpleTemplateEngine:
    def render(template_str, context):
        """
            渲染模板，$key -> context[key]
            context: 一个字典，包含模板变量名key及其对应的值 context[key]
            return: 渲染后的字符串 
        """
        # 匹配以 $ 开头的占位符，如 $name
        pattern = r"\$(\w+)"
        
        def replace_placeholder(match):
            old = match.group(1)
            # 如果找不到变量，则返回原值
            value = context.get(old) or '$'+old
            return value
        
        # 使用正则表达式替换占位符
        return re.sub(pattern, replace_placeholder, template_str)

class SimpleTemplateEngineFull:
    def render(template_str, context):
        """
            渲染模板，$key -> context[key]
            context: 一个字典，包含模板变量名key及其对应的值 context[key]
            return: 渲染后的字符串 
        """
        # 匹配以 $ 开头的占位符，如 $name
        pattern = r"\$(\w+)"
        
        def replace_placeholder(match):
            old = match.group(1)
            # 检查变量是否startswith在上下文中
            for key, value in context.items():
                if old.startswith(key):
                    return old.replace(key, value)
            return '$'+old
                
        # 使用正则表达式替换占位符
        return re.sub(pattern, replace_placeholder, template_str)
    
    
if __name__ == "__main__":
    template = "Hello, $name! You are $age years old."
    context = {"name": "itild", "age": 18}
    print(SimpleTemplateEngine.render(template,context))