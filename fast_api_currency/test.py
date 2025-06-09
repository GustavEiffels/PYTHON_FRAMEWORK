import pandas as pd
import matplotlib.pyplot as plt
import json
import os # To check if the file exists

def plot_exchange_rate_from_json(filename="USD_TO_KRW.json"):
    """
    Loads exchange rate data from a JSON file and plots it.

    Args:
        filename (str): The name of the JSON file containing the exchange rate data.
                        The file should have the structure:
                        {
                          "base": "USD",
                          "target": "KRW",
                          "currency": [
                            {"date": "YYYY-MM-DD", "currency": value},
                            ...
                          ]
                        }
    """
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found in the current directory.")
        print("Please ensure the JSON file exists or provide the correct path.")
        return

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filename}'. Please check the file content for validity.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading '{filename}': {e}")
        return

    # Extract the 'currency' list which contains date and currency values
    if 'currency' not in data or not isinstance(data['currency'], list):
        print(f"Error: Expected a 'currency' list in the JSON data, but found none or it's not a list.")
        return

    currency_list = data['currency']

    if not currency_list:
        print(f"No currency data found in '{filename}' to plot.")
        return

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(currency_list)

    # Convert 'date' column to datetime objects for proper plotting
    if 'date' not in df.columns or 'currency' not in df.columns:
        print(f"Error: 'date' or 'currency' columns not found in the data from '{filename}'.")
        return
    
    df['date'] = pd.to_datetime(df['date'])
    df['currency'] = pd.to_numeric(df['currency']) # Ensure currency is numeric

    # Set the date as the index for time-series plotting
    df = df.set_index('date')
    
    # Sort by date index to ensure correct plotting order
    df = df.sort_index()

    # Get base and target currencies for plot title/labels
    base_currency = data.get('base', 'BASE_CURRENCY')
    target_currency = data.get('target', 'TARGET_CURRENCY')

    # Create the plot
    plt.figure(figsize=(12, 6)) # Set figure size
    plt.plot(df.index, df['currency'], marker='o', linestyle='-', color='skyblue')

    # Add titles and labels
    plt.title(f'{base_currency} to {target_currency} Exchange Rate Over Time', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel(f'Exchange Rate ({target_currency} / {base_currency})', fontsize=12)

    # Improve x-axis date formatting and rotation
    plt.gcf().autofmt_xdate()
    plt.grid(True, linestyle='--', alpha=0.7) # Add a grid for better readability
    plt.tight_layout() # Adjust layout to prevent labels from overlapping

    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Ensure you have a USD_TO_KRW.json file in the same directory as this script.
    # If your file is named 'USD_TO_KRW_FullHistory.json', change the filename below.
    json_file_name = "USD_TO_KRW.json"
    plot_exchange_rate_from_json(json_file_name)