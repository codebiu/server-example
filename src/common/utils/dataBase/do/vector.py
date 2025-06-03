from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.types import UserDefinedType, Float, String
import numpy as np
from struct import pack, unpack_from


class Vector:
    def __init__(self, value):
        # 如果不是numpy数组或数据类型不符，则转换
        if not isinstance(value, np.ndarray) or value.dtype != '>f4':
            value = np.asarray(value, dtype='>f4')

        if value.ndim != 1:
            raise ValueError('维度必须为1')

        self._value = value

    def __repr__(self):
        return f'Vector({self.to_list()})'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return np.array_equal(self.to_numpy(), other.to_numpy())
        return False

    def dimensions(self):
        return len(self._value)

    def to_list(self):
        return self._value.tolist()

    def to_numpy(self):
        return self._value

    def to_text(self):
        return '[' + ','.join([str(float(v)) for v in self._value]) + ']'

    def to_binary(self):
        return pack('>HH', self.dimensions(), 0) + self._value.tobytes()

    @classmethod
    def from_text(cls, value):
        return cls([float(v) for v in value[1:-1].split(',')])

    @classmethod
    def from_binary(cls, value):
        dim, unused = unpack_from('>HH', value)
        return cls(np.frombuffer(value, dtype='>f4', count=dim, offset=4))

    @classmethod
    def _to_db(cls, value, dim=None):
        if value is None:
            return value

        if not isinstance(value, cls):
            value = cls(value)

        if dim is not None and value.dimensions() != dim:
            raise ValueError('期望维度为%d，实际为%d' % (dim, value.dimensions()))

        return value.to_text()

    @classmethod
    def _to_db_binary(cls, value):
        if value is None:
            return value

        if not isinstance(value, cls):
            value = cls(value)

        return value.to_binary()

    # @classmethod
    # def _from_db(cls, value):
    #     if value is None or isinstance(value, np.ndarray):
    #         return value

    #     return cls.from_text(value).to_numpy().astype(np.float32)
    @classmethod
    def _from_db(cls, value):
        if value is None or isinstance(value, np.ndarray):
            return value
        # 直接解析文本 -> numpy
        return np.fromstring(value[1:-1], sep=',', dtype=np.float32)
    
    @classmethod
    def _from_db_binary(cls, value):
        if value is None or isinstance(value, np.ndarray):
            return value

        return cls.from_binary(value).to_numpy().astype(np.float32)


class VECTOR(UserDefinedType):
    cache_ok = True
    _string = String()

    def __init__(self, dim=None):
        super(UserDefinedType, self).__init__()
        self.dim = dim

    def get_col_spec(self, **kw):
        if self.dim is None:
            return 'VECTOR'
        return f'VECTOR({self.dim})'

    def bind_processor(self, dialect):
        def process(value):
            return Vector._to_db(value, self.dim)
        return process

    def literal_processor(self, dialect):
        string_literal_processor = self._string._cached_literal_processor(dialect)

        def process(value):
            return string_literal_processor(Vector._to_db(value, self.dim))
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return Vector._from_db(value)
        return process

    class comparator_factory(UserDefinedType.Comparator):
        def l2_distance(self, other):
            return self.op('<->', return_type=Float)(other)

        def max_inner_product(self, other):
            return self.op('<#>', return_type=Float)(other)

        def cosine_distance(self, other):
            return self.op('<=>', return_type=Float)(other)

        def l1_distance(self, other):
            return self.op('<+>', return_type=Float)(other)


# 用于反射
ischema_names['vector'] = VECTOR