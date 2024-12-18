import aisuite as ai
from src.logger_config import logger
from sentry_sdk import capture_exception, capture_message
from .template.base import LLMClientTemplate

class AnthropicClient(LLMClientTemplate):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def _initialize_client(self):
        try:
            self.client = ai.Client({"anthropic": {"api_key": self.api_key}})
        except Exception as e:
            # 更具體的錯誤訊息，記錄 API 鍵初始化失敗的具體情境
            logger.error(
                "Failed to initialize Anthropic client with API key '%s': %s", 
                self.api_key, str(e), exc_info=True
            )
            capture_message('Something went wrong while initializing Anthropic client')  # 自定義錯誤訊息
            capture_exception(e)  # 捕捉並發送例外到 Sentry
        self.model = "anthropic:claude-3-5-sonnet-20240620"
