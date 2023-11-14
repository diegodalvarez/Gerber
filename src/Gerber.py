# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 07:09:41 2022

@author: Diego
"""

import itertools
import numpy as np
import pandas as pd
import statsmodels as sm

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
    
        self.threshold_df = (self.rtns.reset_index().melt(
            id_vars = self.rtns.index.name, var_name = "ticker", value_name = "rtns").
            merge(right = self.hk, how = "inner", on = "ticker"))
        
    def rolling_gerber_corr(self, rtns: pd.DataFrame, window: int, threshold: float = 1/2) -> pd.DataFrame:

        df_compare = (rtns.rolling(
            window = window).
            std().
            dropna().
            reset_index().
            melt(id_vars = "date", value_name = "_std").
            assign(hk = lambda x: x._std * threshold).
            drop(columns = ["_std"]).
            merge(
                right = rtns.reset_index().melt(id_vars = "date", value_name = "rtns"),
                how = "inner",
                on = ["date", "variable"]))

        combined_tmp = (df_compare.melt(
            id_vars = ["date", "variable"], var_name = "stat", value_name = "num").
            assign(name = lambda x: x.variable + "_" + x.stat).
            drop(columns = ["variable", "stat"]).
            pivot(index = "date", columns = "name", values = "num"))

        combo = rtns.columns.to_list()
        combined_tmp = self._get_stat(combined_tmp, combo)
        
        out = (combined_tmp.assign(
            numerator = lambda x: x.m_ij.rolling(window = window).sum(),
            denominator = lambda x: np.abs(x.m_ij).rolling(window = window).sum(),
            gerber_stat = lambda x: x.numerator / x.denominator)
            [["gerber_stat"]])
        
        return out
    
    def _get_stat(self, combined_tmp: pd.DataFrame, combo) -> pd.DataFrame:
        
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
        
        return combined_tmp
        
    def _get_combined_tmp(self):
        
        combinations = list(itertools.combinations(self.rtns.columns.to_list(),2))
        for combo in combinations:
            
            returns_tmp = (self.threshold_df[
                [self.rtns.index.name, "ticker", "rtns"]].
                query("ticker == [@combo[0], @combo[1]]").
                pivot(index = self.rtns.index.name, columns = "ticker", values = "rtns").
                rename(columns = 
                       {combo[0]: "{}_rtns".format(combo[0]), 
                        combo[1]: "{}_rtns".format(combo[1])}))

            hk_rtmp = (self.threshold_df[
                [self.rtns.index.name, "ticker", "h_k"]].
                query("ticker == [@combo[0], @combo[1]]").
                pivot(index = self.rtns.index.name, columns = "ticker", values = "h_k").
                rename(columns = 
                      {combo[0]: "{}_hk".format(combo[0]), 
                       combo[1]: "{}_hk".format(combo[1])}))

            combined_tmp = returns_tmp.merge(hk_rtmp, how = "inner", on = self.rtns.index.name)
            combined_tmp = self._get_stat(combined_tmp, combo)
            
            return combined_tmp, combo
        
    def corr(self, rtns: pd.DataFrame, threshold: float = 1/2, method = "method1"):
        
        self._setup(rtns, threshold)
    
        if method == "method2":
            
            m_ij = pd.DataFrame(columns = [self.rtns.index.name, "m_ij", "ticker1", "ticker2"]).set_index(self.rtns.index.name)
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
            U = U.fillna(0)[[self.rtns.index.name, "ticker", "u_tj"]].pivot(index = self.rtns.index.name, columns = "ticker", values = "u_tj")
    
            D = R
            D.loc[(D["rtns"] <= - D["h_j"]), "d_tj"] = 1
            D = D.fillna(0)[[self.rtns.index.name, "ticker", "d_tj"]].pivot(index = self.rtns.index.name, columns = "ticker", values = "d_tj")
    
            N_UU = U.T.dot(U)
            N_DD = D.T.dot(D)
    
            N_conc = N_UU + N_DD
            N_disc = U.T.dot(D) + D.T.dot(U)
    
            g_matrix = (N_conc - N_disc).divide(N_conc + N_disc)
            
        return g_matrix
    
    def cov(self, rtns: pd.DataFrame, threshold: float = 1/2, method: str = "method1"):
        
        self.corr_mat = self.corr(rtns = rtns, threshold = threshold, method = method)
        self.std_vec = self.rtns.std()
        self.cov_mat = pd.DataFrame(
            data = np.dot(np.diag(self.std_vec), np.dot(self.corr_mat, np.diag(self.std_vec))),
            columns = self.corr_mat.columns,
            index = self.corr_mat.columns)
        
        return self.cov_mat
    
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
    
    def gerberOLS(self, endog: pd.Series, exog: pd.Series, threshold: float = 1/2, method: str = "method1") -> tuple:

        rtns = endog.to_frame().merge(right = exog, how = "inner", on = exog.index.name)
        cov_mat = self.cov(rtns = rtns, threshold = threshold, method = method)
        cov_xy = cov_mat[endog.name][exog.name]
        var_x = cov_mat[endog.name][endog.name]
        
        gerber_beta = cov_xy / var_x
        gerber_alpha = endog.mean() - (gerber_beta * exog.mean())

        return gerber_alpha, gerber_beta
    
    def rolling_gerber_OLS(
            self,
            endog: pd.Series, exog: pd.Series, 
            window: float, verbose: bool = False, 
            threshold: float = 1/2, method: str = "method1") -> pd.DataFrame:

        rtns = (endog.to_frame().merge(
            right = exog, how = "inner", on = endog.index.name).
            rename(columns = {
                endog.name: "endog",
                exog.name: "exog"}))
        
        df_out = pd.DataFrame({
            "alpha": [],
            "beta": []})
        
        year = rtns.index[0].year
        if verbose == True: print("Working on", year)

        for i in range(len(rtns)):

            if verbose == True:
                old_year = rtns.index[i].year

                if year != old_year:
                    print("Working on", year)
                    year = old_year

            df_tmp = rtns.iloc[i-window: i]
            if len(df_tmp) == window:

                alpha, beta = self.gerberOLS(endog = df_tmp.endog, exog = df_tmp.exog)
                df_combine = pd.DataFrame({"alpha": [alpha], "beta": [beta], "date": [rtns.index[i]]})
                df_out = pd.concat([df_out, df_combine])

            else: 

                df_combine = pd.DataFrame({"alpha": [np.nan], "beta": [np.nan], "date": [rtns.index[i]]})
                df_out = pd.concat([df_out, df_combine])
            
        return df_out
    
    def PCA(self, df: pd.DataFrame, n_components: int, scale: bool = True, threshold: float = 1/2, method: str = "method1"):
        
        if scale == True: df = (df - df.mean(axis = 0)) / df.std(axis = 0)

        cov_matrix = self.cov(rtns = df, threshold = threshold, method = method)
        self.eigenvalues, self.eigenvectors = np.linalg.eig(cov_matrix)
        
        order = np.argsort(self.eigenvalues)[::-1]
        self.sorted_eigenvalues = self.eigenvalues[order]
        self.sorted_eigenvectors = self.eigenvectors[:, order]
        
        self.explained_variance = self.sorted_eigenvalues / np.sum(self.sorted_eigenvalues)
        self.reduced_data = np.matmul(df, self.sorted_eigenvectors[:, :n_components])
        self.reduced_data.columns = ["PC{}".format(i+1) for i in range(n_components)]
        
        return self.eigenvalues, self.eigenvectors, self.explained_variance, self.reduced_data