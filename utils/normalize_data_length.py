def normalize_data_length(*data_lists):
    """
    确保所有数据列表长度一致，不够长度的用空字符串补充
    
    Args:
        *data_lists: 可变数量的列表参数
        
    Returns:
        tuple: 长度一致的所有列表
    """
    if not data_lists:
        return ()
    
    # 找到最长的列表长度
    max_length = max(len(lst) for lst in data_lists)
    
    # 对每个列表进行长度标准化
    normalized_lists = []
    for lst in data_lists:
        if len(lst) < max_length:
            # 如果列表长度不够，用空字符串补充
            normalized_list = lst + [''] * (max_length - len(lst))
        else:
            normalized_list = lst
        normalized_lists.append(normalized_list)
    
    return tuple(normalized_lists)
