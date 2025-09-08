import random
import string
import time


def generate_image_id(prefix='img'):
    # 获取当前时间戳的后6位
    timestamp_suffix = str(int(time.time()))[-6:]

    # 生成4位随机字母数字
    random_chars = ''.join(random.choices(
        string.ascii_lowercase + string.digits,
        k=4
    ))

    business_id = f"{prefix}-{timestamp_suffix}{random_chars}"

    return business_id


def generate_short_id(length=8):
    return ''.join(random.choices(
        string.ascii_lowercase + string.digits,
        k=length
    ))


def generate_image_id_v2(prefix='img', length=10):

    random_part = generate_short_id(length)
    return f"{prefix}-{random_part}"

