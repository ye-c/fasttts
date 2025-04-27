import numpy as np


def add_silence(audio_data, sample_rate, seconds, noise=False):
    """在音频数据前添加静音或噪声

    Args:
        audio_data (np.array): 原始音频数据
        sample_rate (int): 采样率
        seconds (float): 静音时长（秒）
        noise (bool): 是否使用随机噪声代替静音

    Returns:
        np.array: 添加静音/噪声后的音频数据
    """
    if noise:
        # 生成-0.01到0.01之间的随机噪声
        padding = np.random.uniform(-0.005, 0.005, int(sample_rate * seconds))
        padding = padding.astype(audio_data.dtype)
    else:
        padding = np.zeros(int(sample_rate * seconds), dtype=audio_data.dtype)

    return np.concatenate((padding, audio_data))
