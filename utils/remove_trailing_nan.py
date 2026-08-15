import pandas as pd

def remove_trailing_nan(*arrays):
    """
    去除数组中后面为nan的值，从后往前删，直到不是nan就停止
    
    Args:
        *arrays: 可变数量的数组参数
        
    Returns:
        tuple: 处理后的数组元组
    """
    result = []
    for arr in arrays:
        # 从后往前遍历，找到第一个不是nan的位置
        end_index = len(arr)
        for i in range(len(arr) - 1, -1, -1):
            if pd.isna(arr[i]) or str(arr[i]).lower() == 'nan':
                end_index = i
            else:
                break
        
        # 截取到第一个不是nan的位置
        result.append(arr[:end_index])
    
    return tuple(result)
    