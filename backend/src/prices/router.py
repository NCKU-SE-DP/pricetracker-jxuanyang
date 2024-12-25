from fastapi import Query, FastAPI,APIRouter
import requests
from src.logger_config import logger

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
        raise Exception(f'Something went wrong while fetching necessities prices for category "{category}" and commodity "{commodity}": {str(e)}') from e
    
    return response.json()