# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 20:46:53 2023

@author: Diego
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# accesssing geber object 
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), "src"))
from Gerber import Gerber


rtns = pd.read_parquet(path = "df.parquet", engine = "pyarrow")

# original
# gerber = Gerber(rtns, threshold = 1/2)

gerber = Gerber()
gerber_corr = gerber.corr(rtns = rtns, threshold = 1/2)
gerber_cov = gerber.cov(rtns = rtns, threshold = 1/2)

fig, axes = plt.subplots(ncols = 2, figsize = (20,7))

sns.heatmap(data = gerber_corr, ax = axes[0])
sns.heatmap(data = gerber_cov, ax = axes[1])

axes[0].set_title("Gerber Correlation")
axes[1].set_title("Gerber Covariance")