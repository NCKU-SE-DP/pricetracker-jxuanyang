from fastapi import Query, FastAPI,APIRouter
import requests
from src.logger_config import logger
from sentry_sdk import capture_exception,capture_message

router = APIRouter()
app=FastAPI()

@router.get("/prices/necessities-price")
def get_necessities_prices(category: str = Query(None), commodity: str = Query(None)):
    try:
        response = requests.get(
            "https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice",
            params={"CategoryName": category, "Name": commodity}
        )
        response.raise_for_status()  # 確保 HTTP 請求成功
    except Exception as e:
        # 更改 logger.error 記錄錯誤內容
        logger.error(
            "Failed to fetch necessities prices for category '%s' and commodity '%s': %s", 
            category, commodity, str(e), exc_info=True
        )
        capture_message('Something went wrong while fetching necessities prices')  # 發送自定義錯誤訊息到 Sentry
        capture_exception(e)  # 捕捉並發送例外到 Sentry
        return {"error": "Failed to fetch necessities prices. Please try again later."}
    
    return response.json()