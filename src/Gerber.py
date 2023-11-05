# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 07:09:41 2022

@author: Diego
"""

import itertools
import numpy as np
import pandas as pd


class Gerber:
    
    def _setup(self, rtns: pd.DataFrame, threshold: float = 1/2):

        self.rtns = rtns
        self.stds = self.rtns.std().reset_index()
        self.stds_cols = self.stds.columns.to_list()
        self.hk = (self.stds.rename(
            columns = {
                self.stds_cols[0]: "ticker",
                self.stds_cols[1]: "h_k"}).
            assign(h_k = lambda x: x.h_k * threshold))
    
        self.threshold_df = (rtns.reset_index().melt(
            id_vars = "Date", var_name = "ticker", value_name = "rtns").
            merge(right = self.hk, how = "inner", on = "ticker"))
        
    def rolling_gerber_corr(self, rtns: pd.DataFrame, window: int, threshold: float = 1/2) -> pd.DataFrame:

        self._setup(rtns = rtns, threshold = threshold)
        combined_tmp, combo = self._get_combined_tmp()

        out = (combined_tmp.assign(
            numerator = lambda x: x.m_ij.rolling(window = window).sum(),
            denominator = lambda x: np.abs(x.m_ij).rolling(window = window).sum(),
            gerber_stat = lambda x: x.numerator / x.denominator)
            [["gerber_stat"]])
        
        return out
        
    def _get_combined_tmp(self):
        
        combinations = list(itertools.combinations(self.rtns.columns.to_list(),2))
        for combo in combinations:

            returns_tmp = (self.threshold_df[
                ["Date", "ticker", "rtns"]].
                query("ticker == [@combo[0], @combo[1]]").
                 pivot(index = "Date", columns = "ticker", values = "rtns").
                 rename(columns = 
                        {combo[0]: "{}_rtns".format(combo[0]), 
                         combo[1]: "{}_rtns".format(combo[1])}))

            hk_rtmp = (self.threshold_df[
                ["Date", "ticker", "h_k"]].
                query("ticker == [@combo[0], @combo[1]]").
                 pivot(index = "Date", columns = "ticker", values = "h_k").
                 rename(columns = 
                       {combo[0]: "{}_hk".format(combo[0]), 
                        combo[1]: "{}_hk".format(combo[1])}))

            combined_tmp = returns_tmp.merge(hk_rtmp, how = "inner", on = "Date")

            combined_tmp.loc[
                (combined_tmp["{}_rtns".format(combo[0])] >= combined_tmp["{}_hk".format(combo[0])]) &
                (combined_tmp["{}_rtns".format(combo[1])] >= combined_tmp["{}_hk".format(combo[1])]), 
                "m_ij"] = 1 

            combined_tmp.loc[
                (combined_tmp["{}_rtns".format(combo[0])] <= - combined_tmp["{}_hk".format(combo[0])]) &
                (combined_tmp["{}_rtns".format(combo[1])] <= - combined_tmp["{}_hk".format(combo[1])]), 
                "m_ij"] = 1

            combined_tmp.loc[
                (combined_tmp["{}_rtns".format(combo[0])] >=  combined_tmp["{}_hk".format(combo[0])]) &
                (combined_tmp["{}_rtns".format(combo[1])] <= - combined_tmp["{}_hk".format(combo[1])]), 
                "m_ij"] = -1

            combined_tmp.loc[
                (combined_tmp["{}_rtns".format(combo[0])] <= - combined_tmp["{}_hk".format(combo[0])]) &
                (combined_tmp["{}_rtns".format(combo[1])] >= combined_tmp["{}_hk".format(combo[1])]), 
                "m_ij"] = -1

            combined_tmp = (combined_tmp.fillna(0)[["m_ij"]].assign(
                ticker1 = combo[0], 
                ticker2 = combo[1]))
            
            return combined_tmp, combo
        
    def corr(self, rtns: pd.DataFrame, threshold: float = 1/2, method = "method1"):
        
        self._setup(rtns, threshold)
    
        if method == "method2":
            
            m_ij = pd.DataFrame(columns = ["Date", "m_ij", "ticker1", "ticker2"]).set_index("Date")
            gerber_stat = pd.DataFrame(columns = ["ticker1", "ticker2", "gerber_stat"])
            combined_tmp, combo = self._get_combined_tmp()
            
            gerber_tmp = (pd.DataFrame(
                {"ticker1": [combo[0]],
                 "ticker2": [combo[1]],
                 "gerber_stat": 
                     [sum(combined_tmp["m_ij"]) / 
                      sum(abs(combined_tmp["m_ij"]))]
                }))
    
            gerber_stat = gerber_stat.append(gerber_tmp)
            m_ij = m_ij.append(combined_tmp)

            if len(gerber_stat.query("gerber_stat < 0")) > 0:
                print("Gerber Matrix is not positive-definite")
    
            else:
                gerber_stat = gerber_stat.assign(tuple_name = lambda x: x.ticker1 + "_" + x.ticker2)
    
            g_matrix = (gerber_stat[
                ["ticker1", "ticker2", "gerber_stat"]].
                pivot(index = "ticker1", columns = "ticker2", values = "gerber_stat"))
            
            g_matrix[g_matrix.index[0]] = np.nan
            cols = g_matrix.columns.to_list()
            cols = cols[-1:] + cols[:-1]
            g_matrix = g_matrix[cols]
            g_matrix = g_matrix.append(pd.DataFrame(columns = g_matrix.columns, index = [g_matrix.columns[-1]]))
            g_matrix = g_matrix.fillna(g_matrix.T)
            np.fill_diagonal(g_matrix.values, 1)
    
        if method == "method1":
    
            R = self.threshold_df.rename(columns = {"h_k": "h_j"})
            U = R
            U.loc[(U["rtns"] >= U["h_j"]), "u_tj"] = 1
            U = U.fillna(0)[["Date", "ticker", "u_tj"]].pivot(index = "Date", columns = "ticker", values = "u_tj")
    
            D = R
            D.loc[(D["rtns"] <= - D["h_j"]), "d_tj"] = 1
            D = D.fillna(0)[["Date", "ticker", "d_tj"]].pivot(index = "Date", columns = "ticker", values = "d_tj")
    
            N_UU = U.T.dot(U)
            N_DD = D.T.dot(D)
    
            N_conc = N_UU + N_DD
            N_disc = U.T.dot(D) + D.T.dot(U)
    
            g_matrix = (N_conc - N_disc).divide(N_conc + N_disc)
            
        return g_matrix
    
    def cov(self, rtns: pd.DataFrame, threshold: float = 1/2, method: str = "method1"):
        
        self.corr = self.corr(rtns = rtns, threshold = threshold, method = method)
        self.std_vec = self.rtns.std()
        self.cov = pd.DataFrame(
            data = np.dot(np.diag(self.std_vec), np.dot(self.corr, np.diag(self.std_vec))),
            columns = self.corr.columns,
            index = self.corr.columns)
        
        return self.cov
    
    def _get_lag(self, rtns: pd.Series, lags: int = 30) -> pd.DataFrame:

        df_prep = (rtns.to_frame().sort_values(
            rtns.index.name).
            rename(columns = {rtns.name: "value"}))

        for lag in range(lags): df_prep[lag+1] = df_prep["value"].shift(lag + 1)

        return(df_prep.rename(columns = {"value": 0}))
    
    def auto_corr_matrix(self, rtns: pd.Series, lags: int = 30, threshold: float = 1/2, method: str = "method1") -> pd.DataFrame:

        df_prep = self._get_lag(rtns = rtns, lags = lags)
        corr = self.corr(rtns = df_prep, threshold = threshold, method = method)
        return corr
    
    def auto_cov_matrix(self, rtns: pd.Series, lags: int = 30, threshold: float = 1/2, method: str = "method1") -> pd.DataFrame:

        df_prep = self._get_lag(rtns = rtns, lags = lags)
        cov = self.cov(rtns = df_prep, threshold = threshold, method = method)
        return cov
    
    def autogerbercorr(self, ts: pd.Series, lags: int, threshold: float = 1/2, method: str = "method1") -> pd.Series:
        
        df = ts.rename(0).to_frame()
        for i in range(1, lags): df[i] = ts.shift(i)
        corr = self.corr(rtns = df, threshold = threshold, method = method)
        corr.columns.name = "lag"
        return corr[0]
        