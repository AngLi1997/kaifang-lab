"""基于 loguru 的应用日志配置。"""

import sys

from loguru import logger as loguru_logger

from app.settings import settings


class Loggin:
    """按 `settings.DEBUG` 选择日志级别并配置 loguru。"""

    def __init__(self) -> None:
        debug = settings.DEBUG
        if debug:
            self.level = "DEBUG"
        else:
            self.level = "INFO"

    def setup_logger(self):
        """把 loguru 的输出重置为标准输出，并返回配置后的 logger。"""
        loguru_logger.remove()
        loguru_logger.add(sink=sys.stdout, level=self.level)

        # logger.add("my_project.log", level=level, rotation="100 MB")  # Output log messages to a file
        return loguru_logger


loggin = Loggin()
logger = loggin.setup_logger()
