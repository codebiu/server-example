from functools import lru_cache
import requests


@lru_cache()
def get_ip_location(oper_ip: str):
    """
    查询ip 相关信息
    """
    oper_location = '内网IP'
    try:
        if oper_ip != '127.0.0.1' and oper_ip != 'localhost':
            oper_location = '未知'
            ip_result = requests.get(f'https://qifu-api.baidubce.com/ip/geo/v1/district?ip={oper_ip}')
            if ip_result.status_code == 200:
                oper_location = ip_result.json().get('data')
    except Exception as e:
        oper_location = '未知'
    return oper_location