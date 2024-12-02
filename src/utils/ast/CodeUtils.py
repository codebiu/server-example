import os
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

# 定义一些常见的编程语言及其特征
language_features = {
    'Python': {
        'keywords': ['def', 'class', 'import', 'from'],
        'comments': ['#'],
        'extensions': ['.py']
    },
    'JavaScript': {
        'keywords': ['function', 'var', 'let', 'const'],
        'comments': ['//', '/*', '*/'],
        'extensions': ['.js']
    },
    'Java': {
        'keywords': ['public', 'class', 'import', 'extends'],
        'comments': ['//', '/*', '*/'],
        'extensions': ['.java']
    },
    'C++': {
        'keywords': ['class', 'template', 'namespace', '#include'],
        'comments': ['//', '/*', '*/'],
        'extensions': ['.cpp', '.cc', '.cxx', '.h', '.hpp']
    }
}

def detect_language_with_features(filename=None,content=None):
    if filename is not None:
        # 检查文件扩展名
        _, ext = os.path.splitext(filename)
        for lang, features in language_features.items():
            if ext in features['extensions']:
                return lang
    if content is not None:
        # # 初始化一个字典来存储每个语言的关键字和注释出现次数
        # language_scores = {lang: 0 for lang in language_features}
        # # 计算每个语言的关键字和注释出现次数
        # for lang, features in language_features.items():
        #     keyword_count = sum(content.count(kw) for kw in features['keywords'])
        #     comment_count = sum(content.count(cm) for cm in features['comments'])
        #     language_scores[lang] = keyword_count + comment_count

        # # 选择得分最高的语言
        # best_match = max(language_scores, key=language_scores.get)
        # if language_scores[best_match] > 0:
        #     return best_match

        # 使用 pygments 进行检测
        try:
            lexer = guess_lexer(content)
            return lexer.name
        except ClassNotFound:
            return "Unknown"


if __name__ == '__main__':
    
    # 示例用法
    filename = 'example_file.java'
    # with open(filename, 'r') as file:
    print(detect_language_with_features(filename,None ))