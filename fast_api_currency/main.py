# main.py
from typing import Union
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import date, timedelta
import requests
import datetime
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def krw_currency_history():

    output_filename = 'USD_TO_KRW.json'
    api_url = f"https://api.frankfurter.dev/v1/2000-01-01..?base=USD&symbols=KRW"
    response = requests.get(api_url)
    response.raise_for_status() 
    full_data = response.json()

    base_currency = full_data.get("base", "USD")

    target_currency = None
    if full_data["rates"]:
        first_date_entry = next(iter(full_data["rates"].values())) 
        if first_date_entry:
            target_currency = next(iter(first_date_entry.keys())) 
    
    if target_currency is None:
        print("Error: Could not determine target currency from 'rates' field.")
        return
    currency_list = []
    sorted_dates = sorted(full_data["rates"].keys())

    for date_str in sorted_dates:
        rates_on_date = full_data["rates"][date_str]
        if target_currency in rates_on_date:
            currency_list.append({
                "date": date_str,
                "currency": rates_on_date[target_currency] # KRW 환율 값
            })
        else:
            print(f"Warning: Missing '{target_currency}' rate for date {date_str}. Skipping this entry.")
        # 최종 출력 형식 구성
    transformed_data = {
        "base": base_currency,
        "target": target_currency,
        "currency": currency_list
    }

        # JSON 파일로 저장
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(transformed_data, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully saved {len(currency_list)} entries to '{output_filename}'")
    except IOError as e:
        print(f"Error saving data to file '{output_filename}': {e}")

    except requests.exceptions.RequestException as e:
        print(f"Network or API error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")




def fetch_and_save_usd_to_krw_history(start_date_str: str, end_date: date, output_filename: str = "USD_TO_KRW.json"):
    history_data = []
    current_date = date.fromisoformat(start_date_str) 
    print(f"Fetching USD to KRW exchange rate history from {start_date_str} to {end_date.isoformat()}...")
    while current_date <= end_date:

        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue

        date_str = current_date.isoformat()
        api_url = f"https://api.frankfurter.dev/v1/{date_str}?base=USD&symbols=KRW"

        try:
            response = requests.get(api_url)
            response.raise_for_status() 
            data = response.json()

            if data and "rates" in data and "KRW" in data["rates"]:
                krw_rate = data["rates"]["KRW"]
                history_data.append({
                    "date": data["date"],
                    "currency": krw_rate
                })
                print(f"Fetched {data['date']}: 1 USD = {krw_rate} KRW")
            else:
                print(f"Warning: Could not retrieve data for {date_str} or invalid format. Response: {data}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {date_str}: {e}")

        current_date += timedelta(days=1) 

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully saved {len(history_data)} entries to {output_filename}")
    except IOError as e:
        print(f"Error saving data to file {output_filename}: {e}")


def get_usd_to_krw_rate():
    """
    Frankfurter API에서 USD 대 KRW 환율을 가져옵니다.
    """
    api_url = "https://api.frankfurter.app/latest?from=USD&to=KRW"
    try:
        response = requests.get(api_url)
        response.raise_for_status() # HTTP 오류 발생 시 예외 발생
        data = response.json()

        if data and "rates" in data and "KRW" in data["rates"]:
            return {
                "base": data.get("base"),
                "date": data.get("date"),
                "rate_to_krw": data["rates"]["KRW"] # USD -> KRW 환율 값
            }
        else:
            print(f"Error: Invalid data structure from Frankfurter API: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rates from Frankfurter API: {e}")
        return None

def get_usd_to_krw_rate_daliy():
    fetch_and_save_usd_to_krw_history('2025-01-01',datetime.date.today(),"USD_TO_KRW.json")\

@app.get('/')
def read_root():
    krw_currency_history()
    return {"message": "Welcome to the USD to KRW Currency Exchange API!"}

@app.get("/api/usd-to-krw")
def get_usd_to_krw_api():
    """
    현재 USD 대 KRW 환율 정보를 JSON 형태로 반환합니다.
    """
    rate_data = get_usd_to_krw_rate()
    if rate_data:
        return rate_data
    else:
        raise HTTPException(status_code=500, detail="Failed to retrieve USD to KRW exchange rate.")

@app.get("/currency-view", response_class=HTMLResponse)
async def currency_view_page(request: Request):
    """
    USD 대 KRW 환율을 표시하는 웹 페이지를 렌더링합니다.
    """
    rate_data = get_usd_to_krw_rate()

    if rate_data:
        context = {
            "request": request, 
            "base_currency": rate_data["base"],
            "target_currency": "KRW",
            "date": rate_data["date"],
            "rate": rate_data["rate_to_krw"]
        }
        return templates.TemplateResponse("currency.html", context)
    else:
        context = {
            "request": request,
            "message": "현재 USD 대 KRW 환율 정보를 불러오는 데 실패했습니다."
        }
        return templates.TemplateResponse("error.html", context, status_code=500)