from fastapi import Query, FastAPI
import requests

router = APIRouter()

@router.get("/necessities-price")
def get_necessities_prices(category: str = Query(None), commodity: str = Query(None)):
    response = requests.get("https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice", params={"CategoryName": category, "Name": commodity})
    return response.json()

@app.get("/api/v1/prices/necessities-price")
def get_necessities_prices(
        category=Query(None), commodity=Query(None)
):
    return requests.get(
        "https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice",
        params={"CategoryName": category, "Name": commodity},
    ).json()