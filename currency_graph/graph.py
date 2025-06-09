import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from datetime import date, timedelta

def draw():
    df_filtered = pd.DataFrame() # df_filtered를 try 블록 밖에서 초기화하여 NameError 방지
    data = None # data 변수도 try 블록 밖에서 초기화하여 잠재적인 NameError 방지

    try:
        # 파일 존재 여부 확인 (선택 사항이지만 유용)
        filename = "USD_TO_KRW.json"
        if not os.path.exists(filename):
            print(f"ERROR: The file '{filename}' was not found. Please ensure it exists in the current directory.")
            return # 파일이 없으면 함수 종료

        with open(filename, "r", encoding='utf-8') as f:
            data = json.load(f)

        if 'currency' not in data or not isinstance(data['currency'], list):
            print(f"ERROR: Expected a 'currency' list in the JSON data, but found none or it's not a list.")
            return

        currency_list = data['currency']
        
        if not currency_list:
            print(f"ERROR: No currency data found in '{filename}' to plot.")
            return

        df = pd.DataFrame(currency_list)
        df['date'] = pd.to_datetime(df['date'])
        df['currency'] = pd.to_numeric(df['currency']) # Ensure currency is numeric
        df = df.set_index('date')
        df = df.sort_index()

        # ★★★ 수정: date.today()로 호출해야 합니다. ★★★
        today = date.today() # 현재 날짜 객체
        one_year_ago = today - timedelta(days=365) # 현재 날짜 기준 1년 전

        df_filtered = df.loc[str(one_year_ago):str(today)] # 날짜 범위로 필터링

    except FileNotFoundError:
        print(f"ERROR: The file 'USD_TO_KRW.json' was not found. Please ensure it exists in the current directory.")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from 'USD_TO_KRW.json'. Check file format.")
        return
    except KeyError as e:
        print(f"ERROR: Missing expected key in JSON data: {e}. Check JSON structure.")
        return
    except Exception as e: # 그 외 모든 예외를 잡음
        print(f'UNEXPECTED ERROR : {e}')
        return

    # ★★★ df_filtered가 비어있는지 확인하는 로직은 try 블록 밖에서 유지하되,
    #     try 블록에서 오류가 발생했을 경우 함수가 이미 return 되었으므로 안전함 ★★★
    if df_filtered.empty:
        # date.today()도 함수 호출로 변경
        print(f"No data available for the period from {one_year_ago.isoformat()} to {today.isoformat()}.")
        return

    # data 변수가 try 블록에서 성공적으로 로드되었는지 확인
    if data is None:
        print("ERROR: Data was not loaded successfully. Cannot proceed with plotting.")
        return

    # Get base and target currencies for plot title/labels
    base_currency = data.get('base', 'USD')
    target_currency = data.get('target', 'KRW')

    # Create the plot
    plt.figure(figsize=(14, 7)) # Adjust figure size for better readability of a year's data
    plt.plot(df_filtered.index, df_filtered['currency'], linestyle='-', color='skyblue', label=f'{base_currency} to {target_currency} Rate')

    # Add titles and labels
    plt.title(f'{base_currency} to {target_currency} Exchange Rate (Last Year: {one_year_ago.isoformat()} - {today.isoformat()})', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel(f'Exchange Rate ({target_currency} / {base_currency})', fontsize=12)

    # Improve x-axis date formatting and rotation
    plt.gcf().autofmt_xdate()
    plt.grid(True, linestyle='--', alpha=0.7) # Add a grid for better readability
    plt.legend() # Show legend
    plt.tight_layout() # Adjust layout to prevent labels from overlapping

    # Show the plot
    plt.show()

# 함수를 호출하여 실행
if __name__ == "__main__":
    draw()