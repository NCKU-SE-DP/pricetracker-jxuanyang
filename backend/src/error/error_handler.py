import logging
from sentry_sdk import capture_message, capture_exception

class ErrorHandler:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle_error(self, message: str, exception: Exception):
        # 記錄錯誤信息
        self.logger.error(message, exc_info=True)
        # 捕獲 Sentry 錯誤信息
        capture_message(message)
        capture_exception(exception)
