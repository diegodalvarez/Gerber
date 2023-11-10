# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 10:53:42 2023

@author: Diego
"""

import os
import pandas as pd
import datetime as dt
import yfinance as yf

from blp import blp

class DataCollector():
    
    def __init__(self):
        
        self.end_date = dt.date.today()
        self.start_date = dt.date(year = 1970, month = 1, day = 1)
        
        self.end_date_input  = self.end_date.strftime("%Y%m%d")
        self.start_date_input = self.start_date.strftime("%Y%m%d")
        
        self.parent_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        self.data_path = os.path.join(self.parent_path, "data")
        
    def _collect_data(self, start_date, end_date, tickers, path):
        
        self.end_date_input  = self.end_date.strftime("%Y%m%d")
        self.start_date_input = self.start_date.strftime("%Y%m%d")
        
        bquery = blp.BlpQuery().start()
        df_tmp = (bquery.bdh(
            securities = tickers,
            fields = ["PX_LAST"],
            start_date = self.start_date_input,
            end_date = self.end_date_input))
        
        df_tmp.to_parquet(path = path, engine = "pyarrow")
        
    def collect_jpy_yield(self, start_date = None, end_date = None):
        
        if start_date != None: self.start_date = start_date
        if end_date != None: self.end_date = end_date
        
        jpy_path = os.path.join(self.data_path, "jpy_tickers.csv")
        tickers = (pd.read_csv(
            filepath_or_buffer = jpy_path, index_col = 0).
            assign(inflation = lambda x: x.Description.str.split(" ").str[-3]).
            query("inflation != 'Inflation'").
            Security.
            drop_duplicates().
            to_list())
        
        tickers = [*set(tickers)]
        out_path = os.path.join(self.data_path, "jpy_yield.parquet")
        
        self._collect_data(start_date = self.start_date, end_date = self.end_date, tickers = tickers, path = out_path)
        
    def collect_hedge_cost(self, start_date = None, end_date = None):
        
        if start_date != None: self.start_date = start_date
        if end_date != None: self.end_date = end_date
        
        hc_path = os.path.join(self.data_path, "hc_tickers.csv")
        tickers = (pd.read_csv(
            hc_path)
            [["Security"]].
            assign(filter_out = lambda x: x.Security.str[5]).
            query("filter_out == ['E', 'J']")
            ["Security"].
            to_list())
        
        out_path = os.path.join(self.data_path, "hc.parquet")
        self._collect_data(start_date = self.start_date, end_date = self.end_date, tickers = tickers, path = out_path)
        
    def collect_us_yield(self, start_date = None, end_date = None):
        
        if start_date != None: self.start_date = start_date
        if end_date != None: self.end_date = end_date
        
        tsy_path = os.path.join(self.data_path, "tsy_tickers.csv")
        tickers = (pd.read_csv(
            filepath_or_buffer = tsy_path, index_col = 0).
            assign(inflation = lambda x: x.Description.str.split(" ").str[3].str[0]).
            query("inflation != 'T' & inflation ! ='F'").
            Security.
            drop_duplicates().
            to_list())
        
        out_path = os.path.join(self.data_path, "tsy_yield.parquet")
        self._collect_data(start_date = self.start_date, end_date = self.end_date, tickers = tickers, path = out_path)
        
    def collect_eur_yield(self, start_date = None, end_date = None):
        
        if start_date != None: self.start_date = start_date
        if end_date != None: self.end_date = end_date
        
        eur_path = os.path.join(self.data_path, "eur_tickers.csv")
        tickers = (pd.read_csv(
            filepath_or_buffer = eur_path, index_col = 0).
            Security.
            drop_duplicates().
            to_list())
        
        out_path = os.path.join(self.data_path, "eur_yield.parquet")
        self._collect_data(start_date = self.start_date, end_date = self.end_date, tickers = tickers, path = out_path)
        
    def collect_tsy_holder(self, start_date = None, end_date = None):
        
        if start_date != None: self.start_date = start_date
        if end_date != None: self.end_date = end_date
        
        out_path = os.path.join(self.data_path, "tsy_holders.parquet")
        countries = ["BE", "FR", "GE", "IT", "JN", "LU", "NE", "SP"]
        tickers = ["HOLD{} Index".format(country) for country in countries]
        self._collect_data(start_date = self.start_date, end_date = self.end_date, tickers = tickers, path = out_path)
        
    def yf_collect_jpyusd(self, start_date = None, end_date = None):
        
        if start_date != None: self.start_date = start_date
        if end_date != None: self.end_date = end_date
        
        out_path = os.path.join(self.data_path, "usd_jpy.parquet")
        tickers = ["JPY=X"]
        df_tmp = yf.download(tickers = tickers, start =self.start_date, end = self.end_date)
        df_tmp.to_parquet(path = out_path, engine = "pyarrow")
 
if __name__ == "__main__":   

    data_collector = DataCollector()
    data_collector.collect_eur_yield()
    data_collector.collect_hedge_cost()
    data_collector.collect_us_yield()
    data_collector.collect_jpy_yield()
    data_collector.collect_tsy_holder()
    data_collector.yf_collect_jpyusd()