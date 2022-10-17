import os
import streamlit as st

api_key = os.environ["CM_KEY"]
#api_key = os.environ['CM_KEY']

import pandas as pd
from coinmetrics.api_client import CoinMetricsClient
from datetime import date, timedelta
#pip install coinmetrics-api-client

client = CoinMetricsClient(api_key)

grayscale_tickers = [
    'aave', 'ada', 'algo', 'amp', 'atom', 'avax', 'bat', 'bch', 'btc', 'comp',
    'crv', 'dot', 'eth', 'etc', 'fil', 'link', 'lpt', 'ltc', 'mana', 'matic',
    'mkr', 'sol', 'uni', 'xlm', 'yfi', 'zec', 'zen'
]

#streamlit run main.py
st.title('grayscale volume automator')

options_list = st.multiselect('Selected Assets (default is our portfolio)',
                              grayscale_tickers,
                              default=grayscale_tickers)

# select box of dates
start_time = str(st.date_input("Start Date", date(date.today().year, 1, 1)))
# end time
end_time = str(st.date_input("End Date", date.today() - timedelta(days=1)))
# frequency

csv = None


def run_automator(options_list: list, start_time: str, end_time: str) -> csv:
    df_list = []

    for asset in options_list:
        # logging
        st.write(f"getting usd-spot volume data for {asset}...")

        # getting candles
        candles_all = client.get_market_candles(
            markets=[f"*-{asset}-usd-spot"],
            start_time=start_time,
            end_time=end_time,
            frequency="1d").to_dataframe()

        # formatting
        candles_all[
            "candle_usd_volume"] = candles_all.candle_usd_volume.astype(float)
        candles_all["time"] = pd.to_datetime(candles_all.time)
        candles_all.sort_values(["market", "time"], inplace=True)

        # creating additional columns
        candles_all["exchange"] = candles_all.market.apply(
            lambda x: x.split("-")[0])
        candles_all["asset"] = candles_all.market.apply(
            lambda x: x.split("-")[1])
        print(candles_all.head())
        df_list.append(candles_all)
    df_final = pd.concat(df_list, ignore_index=True)
    df_final_csv = df_final.to_csv().encode('utf-8')

    # summary
    df2 = df_final.drop(columns=[
        'time', 'price_open', 'price_close', 'price_high', 'price_low', 'vwap'
    ])
    df2 = df2.groupby('market').sum()
    df2_csv = df2.to_csv().encode('utf-8')

    st.dataframe(df2)

    return df_final_csv, df2_csv


date_obj = str(date.today())
if st.button("RUN"):
    st.write("running... pls wait")
    csv_raw, csv_summary = run_automator(options_list, start_time, end_time)
    st.download_button(
        label="Download raw data as CSV",
        data=csv_raw,
        file_name=f"{date_obj}_volume_candles_all.csv",
    )
    st.download_button(label="Download summary data as CSV",
                       data=csv_summary,
                       file_name=f"{date_obj}_volume_summary.csv")
    st.write("complete!")
#df_final = pd.concat(df_list, ignore_index=True)

#df_final.to_csv(f"{date_obj}_volume_candles_all.csv")
