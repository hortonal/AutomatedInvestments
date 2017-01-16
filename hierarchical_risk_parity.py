import pandas as pd
import numpy as np
from collections import OrderedDict

import data
import helpers


symbols = pd.read_csv('MiniAssetUniverse.csv')
symbols = symbols.loc[:,['Ticker', 'Quandl', 'PriceColumn']]
           
rets = data.get_pricing(symbols, start_date='2015-1-1')
rets = rets.pct_change(fill_method='pad')


#try:
#    network_weights = local_csv('Quantopian.csv', date_column = 'date')
#    network_weights = network_weights.reset_index().pivot_table(columns='symbol', values='weight', index='date').resample('b', fill_method='ffill')
#except IOError as e:
#    print(e)
#    pass

# There has to be a more succinct way to do this using rolling_apply or resample
# Would love to see a better version of this.
eoms = rets.resample('1BM').index[13:-1]
covs = pd.Panel(items=eoms, minor_axis=rets.columns, major_axis=rets.columns)
corrs = pd.Panel(items=eoms, minor_axis=rets.columns, major_axis=rets.columns)
covs_robust = pd.Panel(items=eoms, minor_axis=rets.columns, major_axis=rets.columns)
corrs_robust = pd.Panel(items=eoms, minor_axis=rets.columns, major_axis=rets.columns)
for eom in eoms:
    covs.loc[eom] = rets.loc[eom-pd.Timedelta('252d'):eom].cov()
    corrs.loc[eom] = rets.loc[eom-pd.Timedelta('252d'):eom].corr()

portfolio_funcs = OrderedDict((
    ('Equal weighting', lambda returns, cov, corr: np.ones(cov.shape[0]) / len(cov.columns)),
    ('Inverse Variance weighting', lambda returns, cov, corr: helpers.getIVP(cov)),
    #('Minimum-variance (CLA) weighting', getCLA),
    ('Mean-Variance weighting', lambda returns, cov, corr: helpers.get_mean_variance(returns, cov)),
    ('Robust Mean-Variance weighting', lambda returns, cov, corr: helpers.get_mean_variance(returns, cov=helpers.cov_robust(cov))),
    ('Min-Variance weighting', lambda returns, cov, corr: helpers.get_min_variance(returns, cov)),
    ('Robust Min-Variance weighting', lambda returns, cov, corr: helpers.get_min_variance(returns, cov=helpers.cov_robust(cov))),        
    ('Hierarchical weighting (by LdP)', lambda returns, cov, corr: helpers.getHRP(cov, corr)),
    ('Robust Hierarchical weighting (by LdP)', lambda returns, cov, corr: helpers.getHRP(helpers.cov_robust(cov), helpers.corr_robust(corr))),
    #('Network weighting (by Jochen Papenbrock)', lambda x: network_weights.loc[x])
))

weights = pd.Panel(items=portfolio_funcs.keys(), major_axis=eoms, minor_axis=symbols, dtype=np.float32)
port_returns = pd.DataFrame(columns=portfolio_funcs.keys(), index=rets.index)
for name, portfolio_func in portfolio_funcs.items():
    w = pd.DataFrame(index=eoms, columns=symbols, dtype=np.float32)
    for idx in covs:
        w.loc[idx] = portfolio_func(rets.loc[idx-pd.Timedelta('252d'):idx].T, 
                                    covs.loc[idx],
                                    corrs.loc[idx]
        )
    
    port_returns[name] = w.loc[rets.index].ffill().multiply(rets).sum(axis='columns')

    weights.loc[name, :, :] = w

