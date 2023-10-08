# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 21:15:46 2023

@author: Diego
"""

import ssl
import pandas as pd
import yfinance as yf
import datetime as dt

def collect_data():
    
    try: 
        
        df_yf = pd.read_parquet(path  = "df.parquet", engine = "pyarrow")
        print("Data Found in Directory")
        
    except: 
        
        print("Collecting Data from Yahoo Finance")
    
        ssl._create_default_https_context = ssl._create_unverified_context
        tickers = (pd.read_html(
            io = "https://en.wikipedia.org/wiki/Nasdaq-100")
            [4]
            ["Ticker"].
            drop_duplicates().
            to_list())
        
        start_date = dt.date(year = 1999, month = 1, day = 1)
        end_date = dt.date.today()    
    
        df_yf = (yf.download(
            tickers = tickers, start = start_date, end = end_date)
            ["Adj Close"])
        
        good_tickers = (df_yf.reset_index().melt(
            id_vars = "Date").
            dropna().
            query("Date < '2000-01-01'").
            variable.
            drop_duplicates().
            to_list())
    
        out_df = (df_yf.reset_index().melt(
            id_vars = "Date").
            query("variable == @good_tickers").
            dropna().
            pivot(index = "Date", columns = "variable", values = "value").
            dropna().
            pct_change().
            dropna())
        
        out_df.to_parquet("df.parquet", engine = "pyarrow")

if __name__ == "__main__": 
    collect_data()