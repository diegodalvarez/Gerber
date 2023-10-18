# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 08:45:44 2023

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

autogerber_corr = Gerber().auto_corr_matrix(rtns = rtns)
corr = Gerber()._get_lag(rtns).corr()

autogerber_cov = Gerber().auto_cov_matrix(rtns = rtns)
cov = Gerber()._get_lag(rtns).cov()

fig, axes = plt.subplots(ncols = 2, nrows = 3, figsize = (20,18))

sns.heatmap(
data = autogerber_corr,
    ax = axes[0,0])

sns.heatmap(
    data = corr,
    ax = axes[1,0])

sns.heatmap(
    data = autogerber_corr - corr,
    ax = axes[2,0])

sns.heatmap(
    data = autogerber_cov,
    ax = axes[0,1])

sns.heatmap(
    data = cov,
    ax = axes[1,1])

sns.heatmap(
    data = autogerber_cov - cov,
    ax = axes[2,1])

axes[0,0].set_title("Gerber Autocorrelation")
axes[0,1].set_title("Gerber Autocovariance")

axes[1,0].set_title("Pearson Autocorrelation")
axes[1,1].set_title("Pearson Autocovariance")

axes[2,0].set_title("Gerber - Pearson Autocorrelation")
axes[2,1].set_title("Gerber - Pearson Autocovariance")

fig.suptitle("Autocorrelation Measures with AAPL Returns from {} to {}".format(
    rtns.index.min().date(),
    rtns.index.max().date()))

plt.tight_layout()
plt.show()