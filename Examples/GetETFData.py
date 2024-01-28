# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 09:26:56 2024

@author: Diego
"""

import os
import requests
import pandas as pd
import datetime as dt
import yfinance as yf

from bs4 import BeautifulSoup

class GetETF:
    
    def __init__(self):
        
        self.parent_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        self.examples_path = os.path.join(self.parent_path, "Examples")
        self.prices_path = os.path.join(self.examples_path, "etf_prices.parquet")
        self.tickers_path = os.path.join(self.examples_path, "tickers.csv")
    
    def _get_tickers(self) -> pd.DataFrame:

        print("Collecting Ticker Data")
        url = "https://stockanalysis.com/etf/provider/state-street/"
        headers = headers = {"User-Agent": "Chrome/92.0.4515.131 Safari/537.36"}
        response = requests.get(url = url, headers = headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        symbols = [symbol.text for symbol in soup.find_all(class_ = "sym svelte-132bklf")]
        fund_names = [fund_name.text for fund_name in soup.find_all(class_ = "slw svelte-132bklf")]
        
        df = pd.DataFrame({
            symbols[0].strip(): symbols[1:],
            fund_names[0].strip(): fund_names[1:]})
        
        df.to_csv(path_or_buf = self.tickers_path)
        print("Collected Ticker Data")
        
        return df

    def _prep_data(self) -> pd.DataFrame:

        return(self._get_tickers().assign(
            first_letter = lambda x: x.Symbol.str[0]).
            query("first_letter == 'X'").
            drop(columns = ["first_letter"]))
    
    def _collect_data(
        self,
        end_date: dt.date = dt.date.today(),
        lookback: int = 20) -> pd.DataFrame:
        
        start_date = dt.date(year = end_date.year - lookback, month = 1, day = 1)
        tickers = self._prep_data()["Symbol"].to_list() + ["SPY"]
        df = (yf.download(
            tickers = tickers, start = start_date, end = end_date).
            reset_index().
            melt(id_vars = "Date").
            dropna())
        
        df.to_parquet(path = self.prices_path, engine = "pyarrow")
        return df
        
    def collect(self) -> pd.DataFrame:
        
        try: 
        
            return(pd.read_parquet(path = self.prices_path, engine = "pyarrow"))
            print("Data Found in Directory")
            
        except: 
            
            print("Data Not Found in Directory, Now Collecting")
            return(self._collect_data())
    
    