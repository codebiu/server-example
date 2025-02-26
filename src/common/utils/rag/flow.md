# graphRAG流程

节点:
- 文件夹
- 文件
- 类
- 函数

边:
- 文件夹包含文件夹
- 文件夹包含文件(最大代码块)
- 代码块AST关系(多种多层 TODO)

## 流程图

```mermaid
graph TD;
    A[git拉取/zip上传] 
    -->B[获取代码]-->B00[获取文件树]-->B0[分析文件树]-->B1[遍历文件文件夹]
    --> C{类型?};
    C --> |文件夹| D[图插入节点
    文件夹]--> B1;
    C --> |文件| E[
        图插入节点
        文件
        ]

    E --> 文件与文件夹关系 --> 文件夹与文件夹关系
    E --> 构建ast --> 代码块从属当前文件关系 --> 代码块与代码块关系
```

```mermaid
graph LR
    A["DetResizeForTest::__init__(self, **kwargs)"] --> B{参数检查}
    B -->|image_shape| C[设置image_shape和resize_type为1]
    B -->|limit_side_len| D[设置limit_side_len和limit_type]
    B -->|resize_long| E[设置resize_type为2和resize_long]
    B -->|无参数| F[设置默认limit_side_len为736并limit_type为min]
    G["DetResizeForTest::__call__(self, data)"] --> H{resize_type}
    H -->|0| I[调用resize_image_type0]
    H -->|1| J[调用resize_image_type1]
    H -->|2| K[调用resize_image_type2]
    I --> L[更新数据和返回调整后的图像]
    J --> L
    K --> L
```
分析获取可分析文件列表,区分分析和权重,保留文件名/保留文件名并记录后续待分析

树结构是完整,存入节点?


### todo

- [ ] 代码块链添加子类子函数迭代 (多语言慢慢丰富)
- [ ] 代码块与代码块关系 (多语言慢慢丰富)
- [x] 代码块从属当前文件关系
- [x] 文件夹与文件夹关系
- [x] 文件与文件夹关系
- [ ] class属性和局部属性
- [ ] file import

### design

按文件结构建 图  实际节点

+部分按纯调用关系建

按纯调用关系建 图   虚拟节点


!!! 最后问题不好  相应级别的代码块加提示



<!-- 图 -->
构建真实节点和关系

单层关联抽取节点解释

抽取虚拟节点(业务模块等)





