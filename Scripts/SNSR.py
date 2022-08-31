import pandas as pd
import glob
import matplotlib.pyplot as plt
# get input data
path = 'C:/Users/Nate/Desktop/SNSR Stock Analysis/Data'
data_files = glob.glob(path + "/*.csv")
li = []
for filename in data_files:
    df = pd.read_csv(filename)
    li.append(df)
df_input = pd.concat(li)


def clean_data(df_input):
    # Date column
    df_input['Date'] = pd.to_datetime(df_input['Date'])
    
    # Rename columns
    rename_cols = {'% of Net Assets': 'Weight',
                   'Market Price ($)': 'MarketPrice',
                   'Shares Held': 'SharesHeld',
                   'Market Value ($)': 'MarketValue'}
    
    df_input.rename(columns=rename_cols, inplace=True)
    # Delete commas
    df_input.replace(',','', regex=True, inplace=True)
    # Change type
    df_input = df_input.astype({'Weight': float,
                      'MarketPrice': float,
                      'SharesHeld': float,
                      'MarketValue': float})
    df_input = df_input.astype({'Ticker': str,
                      'Name': str,
                      'SEDOL': str})
    df_input['Value'] = df_input['SharesHeld'] * df_input['MarketPrice']
    df_cleaned = df_input
    return df_cleaned

# check new companies added, companies dropped, or no change
def check_ticker_lists(df_cleaned):
    # group dates
    recent_dates = df_cleaned.groupby('Date')['Ticker'].apply(list).reset_index(name='TickerList')
    # Sort by Date
    recent_dates.sort_values(by='Date', ascending=False,inplace=True)
    # get most recent tickers
    new_ticker_list = recent_dates.iloc[0]['TickerList']
    prev_ticker_list = recent_dates.iloc[1]['TickerList']
    
    if len(new_ticker_list) == len(prev_ticker_list):
        
        check =  all( item in new_ticker_list for item in prev_ticker_list)    
        if check is True:
            print("SNSR holdings have NOT changed")
            return df_cleaned
        else :
            print("SNSR has changed holdings, inspecting...")
            added_tickers = list(set(new_ticker_list).difference(prev_ticker_list))
            print("Ticker(s) added: ", added_tickers)
            dropped_tickers = list(set(prev_ticker_list).difference(new_ticker_list))
            print("Ticker(s) dropped: ", dropped_tickers)
            return df_cleaned
            
    elif len(new_ticker_list) > len(prev_ticker_list):
        list(set(new_ticker_list).difference(prev_ticker_list))
        added_tickers = list(set(new_ticker_list).difference(prev_ticker_list))
        print("Ticker(s) added: ", added_tickers)
        return df_cleaned        
    else:
        dropped_tickers = list(set(prev_ticker_list).difference(new_ticker_list))
        print("Ticker(s) dropped: ", dropped_tickers)
        return df_cleaned



# Value Timeseries Chart 
def money_over_time(df_cleaned):
    # filter for plotting
    df_money_plot = df_cleaned[['Date', 'Ticker', 'Value']]
    
    # Holdings over ten million in value
    df_high_value_holdings = df_money_plot[df_money_plot['Value'] >= 10000000]
    high_value_data_for_plotting = df_high_value_holdings.pivot(index="Date", columns="Ticker", values="Value")
    high_value_plot = high_value_data_for_plotting.plot(title = 'Holdings: Value over Ten Million')
    high_value_plot.legend(bbox_to_anchor=(1.1, 1.05))
    plt.show()
    
    # Holdings between 5 and ten million in value
    df_mid_value_holdings = df_money_plot[df_money_plot['Value'].between(5000000, 10000000)]
    mid_value_data_for_plotting = df_mid_value_holdings.pivot(index="Date", columns="Ticker", values="Value")
    mid_value_plot = mid_value_data_for_plotting.plot(title = 'Holdings: 5-10 Million')
    mid_value_plot.legend(bbox_to_anchor=(1.1, 1.05))
    plt.show()
    
    # Holdings between 2 and 5 million in value
    df_small_value_holdings = df_money_plot[df_money_plot['Value'].between(2000000, 5000000)]
    small_value_data_for_plotting = df_small_value_holdings.pivot(index="Date", columns="Ticker", values="Value")
    small_value_plot = small_value_data_for_plotting.plot(title = 'Holdings: 2-5 Million')
    small_value_plot.legend(bbox_to_anchor=(1.1, 1.05))
    plt.show()
    
    # Holdings between 0-2 million in value
    df_vsmall_value_holdings = df_money_plot[df_money_plot['Value'].between(1, 2000000)]
    vsmall_value_data_for_plotting = df_vsmall_value_holdings.pivot(index="Date", columns="Ticker", values="Value")
    vsmall_value_plot = vsmall_value_data_for_plotting.plot(title = 'Holdings: 0-2 Million')
    vsmall_value_plot.legend(bbox_to_anchor=(1.1, 1.05))
    plt.show()
    return 

def shares_reporting(df_cleaned):
    current_date = df_cleaned['Date'].max()
    first_date = df_cleaned['Date'].min()
    df_current = df_cleaned[df_cleaned['Date'] == current_date]
    df_first_date = df_cleaned[df_cleaned['Date'] == first_date]

    df_shares = df_current.merge(df_first_date, how='outer', left_on='Ticker',
                                  right_on='Ticker', suffixes=('_current', '_old'))

    df_shares['SharesAdded%'] = ((df_shares['SharesHeld_current'] - df_shares['SharesHeld_old']) /
                                  df_shares['SharesHeld_old']) * 100
    df_shares['MarketPriceChange%'] = ((df_shares['MarketPrice_current'] - 
                                      df_shares['MarketPrice_old']) / df_shares['MarketPrice_old']) * 100
    df_shares['TimePeriod'] = df_shares['Date_current'] - df_shares['Date_old']
    df_shares['MarketValueChange%'] = ((df_shares['MarketValue_current'] - 
                                      df_shares['MarketValue_old']) / df_shares['MarketValue_old']) * 100 
    df_shares['WeightChange'] = df_shares['Weight_current'] - df_shares['Weight_old']

    df_shares_report = df_shares[['Ticker', 'WeightChange', 'MarketPrice_current', 'MarketValueChange%',
                                  'MarketPriceChange%','SharesAdded%', 'TimePeriod', 'Date_current']]
    return df_shares_report

    



df_cleaned = clean_data(df_input)
df_cleaned = check_ticker_lists(df_cleaned)
df_shares_report = shares_reporting(df_cleaned)
plots = money_over_time(df_cleaned)

# =============================================================================
# from fpdf import FPDF
# pdf = FPDF()
# pdf.add_page()
# =============================================================================

    

# graph of biggest drop/gain in share price
    
    
    
    
    



        




# shares added or dropped over time
# group by ticker


# =============================================================================
# # new companies added, companies dropped, % of net assets changes, 
# current Weight and Previous Weight to calculate percent change










