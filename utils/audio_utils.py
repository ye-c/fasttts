import numpy as np
import torchaudio


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


def load_wav(wav, target_sr=16000):
    speech, sample_rate = torchaudio.load(wav, backend="soundfile")
    speech = speech.mean(dim=0, keepdim=True)
    if sample_rate != target_sr:
        assert sample_rate > target_sr, (
            "wav sample rate {} must be greater than {}".format(sample_rate, target_sr)
        )
        speech = torchaudio.transforms.Resample(
            orig_freq=sample_rate, new_freq=target_sr
        )(speech)
    return speech
