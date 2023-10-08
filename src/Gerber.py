# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 07:09:41 2022

@author: Diego
"""

import itertools
import numpy as np
import pandas as pd


class Gerber:
    
    def __init__(self, rtns, threshold = 1/2):
        
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
        
    def corr(self, method = "method1"):
    
        if method == "method2":
    
            combinations = list(itertools.combinations(self.rtns.columns.to_list(),2))
            m_ij = pd.DataFrame(columns = ["Date", "m_ij", "ticker1", "ticker2"]).set_index("Date")
            gerber_stat = pd.DataFrame(columns = ["ticker1", "ticker2", "gerber_stat"])
    
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
    
    def cov(self, threshold = 1/2, method = "method1"):
        
        self.corr = self.corr(method)
        self.std_vec = self.rtns.std()
        self.cov = pd.DataFrame(
            data = np.dot(np.diag(self.std_vec), np.dot(self.corr, np.diag(self.std_vec))),
            columns = self.corr.columns,
            index = self.corr.columns)
        
        return self.cov