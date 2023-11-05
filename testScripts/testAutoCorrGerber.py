# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 04:26:14 2023

@author: Diego
"""

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# accesssing geber object 
import sys
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), "src"))
from Gerber import Gerber

rtns = (pd.read_parquet(
    path = "df.parquet", engine = "pyarrow")
    ["AAPL"])

autogerbercorr = (Gerber().autogerbercorr(
    ts = rtns,
    lags = 40))

autogerbercorr.plot(
    figsize = (16,6),
    ylabel = "Gerber Correlation",
    xlabel = "lag (days)",
    title = "Gerber Autocorrelation of AAPL Returns from {} to {}".format(
        rtns.index.min().date(),
        rtns.index.max().date()))