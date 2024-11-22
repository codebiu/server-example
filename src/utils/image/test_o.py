from PIL import Image

def horizontal_concatenate_images(image1_path, image2_path, output_path):
    # 打开两张图片
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # 获取图片的宽度和高度
    width1, height1 = image1.size
    width2, height2 = image2.size

    # 创建一个新的空白图片，宽度为两张图片宽度之和，高度取最大值
    max_height = max(height1, height2)
    new_image = Image.new('RGB', (width1 + width2, max_height))

    # 将第一张图片粘贴到新图片的左侧
    new_image.paste(image1, (0, 0))

    # 将第二张图片粘贴到新图片的右侧
    new_image.paste(image2, (width1, 0))

    # 保存新图片
    new_image.save(output_path)
    
    list_test = []
    for i in range(1, 200):
        list_test.append(new_image)

    new_image.save('source/test/pdf_name.pdf', "PDF", resolution=96.0, save_all=True,append_images = list_test)

# 示例用法
image1_path = 'source/test/1.jpg'
image2_path = 'source/test/2.jpg'
output_path = 'source/test/output3.jpg'

horizontal_concatenate_images(image1_path, image2_path, output_path)