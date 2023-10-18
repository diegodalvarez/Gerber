# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 21:11:46 2023

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

rtns = pd.read_parquet(path = "df.parquet", engine = "pyarrow")
gerber = Gerber()

corr_diff = abs(gerber.corr(rtns) - rtns.corr())
cov_diff = abs(gerber.cov(rtns) - rtns.cov())

fig, axes = plt.subplots(ncols = 2, figsize = (20,7))

sns.heatmap(data = corr_diff, ax = axes[0])
sns.heatmap(data = cov_diff, ax = axes[1])

fig.suptitle("Absolute Difference between Gerber and Standard Calculation using NASDAQ 100")
axes[0].set_title("Correlation")
axes[1].set_title("Covariance")