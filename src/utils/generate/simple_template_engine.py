import re

class SimpleTemplateEngine:
    def render(template_str, context):
        """
        渲染模板，将 context 中的键替换到模板中
        :param context: 一个字典，包含模板变量名及其对应的值
        :return: 渲染后的字符串
        """
        # 匹配以 $ 开头的占位符，如 $name
        pattern = r"\$(\w+)"
        
        def replace_placeholder(match):
            key = match.group(1)
            value = context.get(key, f"{{{{ {key} }}}}")  # 如果找不到变量，则返回占位符
            return str(value)  # 确保返回值是字符串

        # 使用正则表达式替换占位符
        return re.sub(pattern, replace_placeholder, template_str)

    
    
if __name__ == "__main__":
    template = "Hello, $name! You are $age years old."
    context = {"name": "itild", "age": 18}
    print(SimpleTemplateEngine.render(template,context))