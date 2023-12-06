# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 21:11:46 2023

@author: Diego
"""

import os
import random
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

random.seed(1234)

# accesssing geber object 
import sys
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), "src"))
from Gerber import Gerber

rtns = pd.read_parquet(path = "df.parquet", engine = "pyarrow")
gerber = Gerber()

cols = rtns.columns.to_list()
random.shuffle(cols)

fig, axes = plt.subplots(ncols = 4, nrows = 4, figsize = (20,20))

j,k = 0,0
for i in range(16):
        
    cols_tmp = cols[3*i : 3*i+2]
    df_tmp = rtns[cols_tmp]
    
    cumsum_comovement = Gerber().cumsum_comovement(df_tmp)
    
    cumsum_comovement.plot(
        ax = axes[j,k],   
        legend = False, 
        title = "{} & {}".format(
            cols_tmp[0],
            cols_tmp[1]))
    
    j += 1
    if j == 4: 
        k += 1
        j = 0

fig.suptitle("Cumulative Comovement Sum from {} to {}".format(
    rtns.index.min().date(),
    rtns.index.max().date()))
plt.tight_layout(pad = 3)