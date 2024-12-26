import re


def snake_to_camel(snake_str):
    """分割字符串，转换成驼峰"""
    components = snake_str.split("_")
    # 将第一个单词保持小写，后面的单词首字母大写
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(camel_str):
    """分割字符串，转换成下划线"""
    components = re.findall(r"([A-Z][a-z]*)", camel_str)
    return "_".join(x.lower() for x in components)