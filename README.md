# Gerber
Package for using the Gerber Statistic for various statistical techniques. 

# Applications of Gerber Statistic
1. Gerber Portfolio Optimization
2. Rolling Gerber Correlations
3. AutoGerberlation
4. Gerber Betas
5. GerberPCA

## Repo layout
```bash
    Gerber
      └───src
          │   Gerber.py
          │   setup.py
      └───testNotebooks
          │   setup.py
          │   TestEfficientFrontier.ipynb
          │   TestRollingGerber.ipynb
      └───testScripts
          │   setup.py
          │   testMatrices.py
          │   testGerberNp.py
          │   testAutoGerberalation.py
      └───Examples
          │   StockBondCorrelation.ipynb
```

src files:
* ```Gerber.py```: OOP file for all of the Gerber Functions

testNotebooks Files:
* ```setup.py```: Downloads sample retursn data from yahoo finance
* ```TestEfficientFrontier.ipynb```: Examines the differences between Efficient Frontiers using Gerber Covariance and Standard Covariance
* ```TestRollingGerber.ipynb```: Look at the rolling Gerber correlation and standard rolling Gerber Correlation

testScripts Files:
* ```setup.py```: Downloads sample retursn data from yahoo finance
* ```testMatrices.py```: Creates Sample covariance and correlation matrix using Gerber Statistic
* ```testGerberNp.py```: Compares Gerber-based covariance and correlation matrix to standard
* ```testAutoGerberlation.py```: Creats Gerber based autocorrelation and autocovariance matrix and the difference between Gerber and Pearson
Example Files:
* ```StockBondCorrelation.ipynb```: Analyzing rolling stock bond correlation using some examples from other research. Specifically looking at historical relationship using Shiller Data.
