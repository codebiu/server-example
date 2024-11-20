
class CodeGenerate:
    '''代码生成器'''
    def __init__(self, code):
        self.code = code

    def generate(self):
        return self.code

    def __str__(self):
        return self.generate()
    