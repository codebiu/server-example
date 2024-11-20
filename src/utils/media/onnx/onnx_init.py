import numpy as np
from sklearn.linear_model import LinearRegression
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as ort

def train_data():
    '''定义固定的输入数据和目标值'''
    X = np.array([[1.0], [2.0], [3.0], [4.0]], dtype=np.float32)
    y = np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float32)
    return X, y

def train_model(X, y):
    '''训练模型'''
    model = LinearRegression()
    model.fit(X, y)
    
    return model

def onnx_convert(model, X): 
    '''将模型转换为 ONNX 格式'''   
    initial_type = [('float_input', FloatTensorType([None, X.shape[1]]))]
    onnx_model = convert_sklearn(model, initial_types=initial_type)
    return onnx_model

def onnx_save(path,onnx_model):
    '''保存 ONNX 文件'''
    with open(path, "wb") as f:
        f.write(onnx_model.SerializeToString())

    print("模型已成功转换并保存为 ONNX 格式。")

def inference_onnx(model_path, input_data):
    '''推理'''
    session = ort.InferenceSession(model_path)
    # 获取输入和输出的名称
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    # 进行预测
    result = session.run([output_name], {input_name: input_data})

    # 打印预测结果
    print("预测结果:", result)
    
    
if __name__ == "__main__":
    # 模型输出和加载
    path_model = "source/test/linear_regression_fixed.onnx"
    
    #训练
    # X, y = train_data()
    # model = train_model(X, y)
    # onnx_model = onnx_convert(model,X)
    # onnx_save(path_model,onnx_model)
    
    # 推理
    # 定义输入数据
    input_data = np.array([[5.0]], dtype=np.float32)
    inference_onnx(path_model, input_data)