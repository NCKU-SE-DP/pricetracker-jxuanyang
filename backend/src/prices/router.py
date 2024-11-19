from fastapi import Query, FastAPI
import requests
from fastapi import APIRouter

router = APIRouter()
app=FastAPI()

@router.get("/prices/necessities-price")
def get_necessities_prices(category: str = Query(None), commodity: str = Query(None)):
    response = requests.get("https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice", params={"CategoryName": category, "Name": commodity})
    return response.json()