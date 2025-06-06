import numpy as np


class Mock:
    async def content_embedding_data_pg(session, pid="proj_1", count=6, dim=1024):
        """生成测试数据"""

        # 生成随机向量（1024维）
        def random_vector():
            return [float(x) for x in np.random.rand(dim).tolist()]

        target = {"content": f"目标文档", "embedding": [0.1] * dim, "pid": pid}
        documents = [target]
        for i in range(count):
            documents.append(
                {"content": f"文档内容 {i}", "embedding": random_vector(), "pid": pid}
            )
        return documents, target
