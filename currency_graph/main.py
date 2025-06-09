import pandas as pd
import json
import os
from datetime import date, timedelta
from typing import Union
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- 그래프 데이터 준비 로직 ---
def get_filtered_currency_data_for_plot():
    filename = "USD_TO_KRW.json"
    
    if not os.path.exists(filename):
        print(f"ERROR: The file '{filename}' was not found.")
        raise HTTPException(status_code=404, detail=f"Currency data file '{filename}' not found.")

    try:
        with open(filename, "r", encoding='utf-8') as f:
            data = json.load(f)

        if 'currency' not in data or not isinstance(data['currency'], list):
            raise HTTPException(status_code=500, detail="Invalid JSON format: missing 'currency' list.")

        currency_list = data['currency']
        if not currency_list:
            raise HTTPException(status_code=500, detail="No currency data found in the file.")

        df = pd.DataFrame(currency_list)
        df['date'] = pd.to_datetime(df['date'])
        df['currency'] = pd.to_numeric(df['currency'])
        df = df.set_index('date')
        df = df.sort_index()

        today = date.today()
        one_year_ago = today - timedelta(days=60)

        df_filtered = df.loc[str(one_year_ago):str(today)]
        
        # [수정 1] Timestamp 객체를 JSON으로 변환 가능한 문자열('YYYY-MM-DD')로 변경
        df_filtered.index = df_filtered.index.strftime('%Y-%m-%d')
        


        plot_data = df_filtered.reset_index().rename(columns={'index': 'date'}).to_dict(orient='records')
        print(f'plot_data : {plot_data}')


        return {
            "base": data.get('base', 'USD'),
            "target": data.get('target', 'KRW'),
            "filtered_data": plot_data
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding JSON from currency data file.")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Missing expected key in JSON data: {e}.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")

# --- API 엔드포인트 ---
@app.get('/')
def read_root():
    return {"message":"Welcome to the Currency Chart App"}

@app.get("/currency-chart-page", response_class=HTMLResponse)
async def serve_currency_chart_page(request: Request):
    """
    환율 그래프를 표시하는 HTML 페이지를 제공합니다.
    """
    print('print data')
    try:
        chart_data = get_filtered_currency_data_for_plot()
        
        return templates.TemplateResponse(
            "chart_page.html",
            {
                "request": request,
                "chart_data": chart_data 
            }
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": e.detail}, status_code=e.status_code
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "서버 내부 오류: " + str(e)}, status_code=500
        )