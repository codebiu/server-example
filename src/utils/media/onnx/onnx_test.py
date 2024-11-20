import onnxruntime as ort
import numpy as np
import cv2

# 加载 ONNX 模型
model_path = 'source/img/test/model.onnx'
session = ort.InferenceSession(model_path)


# 读取和预处理图片
def preprocess_image(image, target_size=(640, 640)):
    # 调整图片大小
    image = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
    
    # 归一化
    image = image.astype(np.float32) / 255.0
    
    # 转换为 CHW 格式
    image = image.transpose((2, 0, 1))
    
    # 添加批次维度
    image = np.expand_dims(image, axis=0)
    
    return image

# 运行
def run_inference(image, session):
    # 获取输入和输出名称
    input_name = session.get_inputs()[0].name
    output_names = [output.name for output in session.get_outputs()]
    
    # 运行模型
    outputs = session.run(output_names, {input_name: image})
    
    return outputs

# 输出
def postprocess_outputs(outputs, image_size, confidence_threshold=0.5):
    # 解析输出
    boxes = outputs[0][0]
    scores = outputs[1][0]
    class_ids = outputs[2][0]
    
    # 过滤低置信度的检测结果
    valid_detections = []
    for i in range(len(scores)):
        if scores[i] > confidence_threshold:
            box = boxes[i]
            class_id = class_ids[i]
            valid_detections.append({
                'box': box,
                'score': scores[i],
                'class_id': class_id
            })
    
    # 调整框的位置到原始图片尺寸
    original_width, original_height = image_size
    target_width, target_height = (640, 640)
    
    scale_x = original_width / target_width
    scale_y = original_height / target_height
    
    for detection in valid_detections:
        box = detection['box']
        box[0] *= scale_x
        box[1] *= scale_y
        box[2] *= scale_x
        box[3] *= scale_y
    
    return valid_detections


# 绘制
def draw_boxes(image, detections):
    for detection in detections:
        box = detection['box']
        score = detection['score']
        class_id = detection['class_id']
        
        x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
        color = (0, 255, 0)  # 绿色框
        
        # 绘制边界框
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # 绘制标签
        label = f"{class_id}: {score:.2f}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return image




if __name__ == "__main__":
    def main():
        # 图片路径
        image_path = 'source/img/test/code_person_car_l.png'
        
        # 读取图片
        original_image = cv2.imread(image_path)
        image_size = (original_image.shape[1], original_image.shape[0])
        
        # 预处理图片
        image = preprocess_image(original_image)
        
        # 运行模型
        outputs = run_inference(image, session)
        
        # 处理输出结果
        detections = postprocess_outputs(outputs, image_size)
        
        # 绘制检测结果
        result_image = draw_boxes(original_image, detections)
        
        # 显示结果
        cv2.imshow('Result', result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    main()