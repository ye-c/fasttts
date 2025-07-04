import torch
from typing import List, Optional
from pydantic import BaseModel


class TTSRequest(BaseModel):
    text: str
    emotion: str = "neutral"
    instruct: str = ""
    speed: float = 1.0
    prompt_speech_16k: Optional[List[float]] = None

    def convert_to_tensor(self, data: List[float]) -> torch.Tensor:
        """
        将 List[float] 转换为与 load_wav 输出一致的张量
        """
        if data is None:
            return None

        # 1. 转换为 PyTorch 张量
        tensor = torch.tensor(data)

        # 2. 添加通道维度 (N,) → (1, N)
        tensor = tensor.unsqueeze(0)  # shape: (1, N)

        # 3. 确保数据类型为 float32
        tensor = tensor.float()

        return tensor
