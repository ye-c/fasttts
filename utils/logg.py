import os

from loguru import logger

LOG_DIR = ".logs"
os.makedirs(LOG_DIR, exist_ok=True)
logger.remove()

# 用于存放已创建过的logger对象（或说唯一性的logger名字）
_LOGGER_INSTANCES = {}


def get_logger(name: str = "fasttts", level="DEBUG", format=None):
    file_path = os.path.join(LOG_DIR, f"{name}.log")
    def_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <5} | {name}:{function}:{line} | {message}"
    if name not in _LOGGER_INSTANCES:
        logger.add(
            file_path,
            filter=lambda record: record["extra"].get("logname") == name,
            rotation="00:00",
            retention="7 days",
            level=level,
            encoding="utf-8",
            enqueue=True,
            backtrace=True,
            format=format or def_format,
        )
        # bind 返回一个带 extra 的 logger
        _LOGGER_INSTANCES[name] = logger.bind(logname=name)
    return _LOGGER_INSTANCES[name]
