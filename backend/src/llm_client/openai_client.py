import aisuite as ai
from src.logger_config import logger
from .template.base import LLMClientTemplate

class OpenAIClient(LLMClientTemplate):
    def _initialize_client(self):
        try:
            # 嘗試初始化 OpenAI 客戶端
            self.client = ai.Client({"openai": {"api_key": self.api_key}})
            self.model = "openai:gpt-3.5-turbo"
        except Exception as e:
            # 記錄初始化失敗的錯誤，並且提供 API 鍵的詳細信息
            logger.error(
                "Failed to initialize OpenAI client with API key '%s': %s", 
                self.api_key, str(e), exc_info=True
            )
            raise Exception(f'Something went wrong while initializing OpenAI client: {str(e)}') from e