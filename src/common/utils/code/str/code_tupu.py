class CodeTupu:
    # 代码关系判断 子集
    def subset(a, b):
        """
        判断文字 a 是否完全包含在文字 b 中。

        参数:
            a: [a_row_start, a_col_start, a_row_end, a_col_end]
                表示 a 文字的起始行、起始列、结束行和结束列。
            b: [b_row_start, b_col_start, b_row_end, b_col_end]
                表示 b 文字的起始行、起始列、结束行和结束列。

        返回:
            bool: 如果 a 完全包含在 b 中，返回 True，否则返回 False。
        """
        a_row_start, a_col_start, a_row_end, a_col_end = a
        b_row_start, b_col_start, b_row_end, b_col_end = b
        if a_row_start >= b_row_start and a_row_end <= b_row_end:
            if a_row_start == b_row_start and a_col_start < b_col_start:
                return False
            if a_row_end == b_row_end and a_col_end > b_col_end:
                return False
            return True
        return False


    # 交集
    def intersection(a, b):
        """
        判断文字a 与 b 有交集

        参数:
            a: [a_row_start, a_col_start, a_row_end, a_col_end]
                表示 a 文字的起始行、起始列、结束行和结束列。
            b: [b_row_start, b_col_start, b_row_end, b_col_end]
                表示 b 文字的起始行、起始列、结束行和结束列。

        返回:
            bool: 如果 a 与 b 有交集，返回 True，否则返回 False。
        """
        a_row_start, a_col_start, a_row_end, a_col_end = a
        b_row_start, b_col_start, b_row_end, b_col_end = b
        # 优先排除没有交集
        if a_row_start > b_row_end or b_row_start > a_row_end:
            return False
        # A起始行在B结束行，列A在B后,没有交集
        if a_row_start == b_row_end and a_col_start > b_col_end:
            return False
        # A结束行在B起始行，列A在B前,没有交集
        if a_row_end == b_row_start and a_col_end < b_col_start:
            return False
        return True