import re


def snake_to_camel_first_lower(snake_str):
    """分割字符串，转换成驼峰"""
    components = snake_str.split("_")
    # 将第一个单词保持小写，后面的单词首字母大写
    return components[0] + "".join(x.title() for x in components[1:])

def snake_to_camel_first_capital(snake_str):
    """分割字符串，转换成驼峰首字母大写"""
    
    components = snake_str.split("_")
    
    # Capitalize the first letter of each component except the first one
    return "".join(x.title() for x in components)

def camel_to_snake(camel_str):
    """分割字符串，转换成下划线"""
    components = re.findall(r"([A-Z][a-z]*)", camel_str)
    return "_".join(x.lower() for x in components)