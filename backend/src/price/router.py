from fastapi import APIRouter, Query
import requests

router = APIRouter()

@router.get("/necessities-price")
def get_necessities_prices(category: str = Query(None), commodity: str = Query(None)):
    response = requests.get("https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice", params={"CategoryName": category, "Name": commodity})
    return response.json()
