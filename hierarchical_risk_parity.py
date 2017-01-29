import pandas as pd
import numpy as np
#from collections import OrderedDict
import cvxpy

import data
#import helpers

def mean_variance(returns, samples=100):
    # Setup the optimization problem
    p = returns.mean().as_matrix()
    w = cvxpy.Variable(len(p))
    gamma = cvxpy.Parameter(sign='positive')
    
    
    ret = p * w
    
    covs = rets.cov().as_matrix()
    sigma = cvxpy.quad_form(w, covs)
    
    prob = cvxpy.Problem(cvxpy.Maximize(ret - gamma*sigma),
                         [cvxpy.sum_entries(w)==1, w>=0])

    # Compute trade-off curve.
    SAMPLES = 100
    solutions = []
    gamma_vals = np.logspace(-2, 3, num=SAMPLES)
    for i in range(SAMPLES):
        gamma.value = gamma_vals[i]
        prob.solve()
        solutions.append({'mean':ret.value, 'sd':cvxpy.sqrt(sigma).value, 'wgts':w.value})
        
    return(solutions)

def plot_portfolios(rets, sols):
    fig = plt.figure()
    
    for i in sols:
        plt.plot(i['sd'], i['mean'], 'bs')
        
    p = rets.mean().as_matrix()
    covs = rets.cov().as_matrix()
    for i in range(len(p)):
        plt.plot(cvxpy.sqrt(covs[i,i]).value, p[i], 'ro')
        
    plt.xlabel('Standard deviation')
    plt.ylabel('Return')
    plt.show()
    
symbols = pd.read_csv('MiniAssetUniverse.csv')
symbols = symbols.loc[:,['Ticker', 'Quandl', 'PriceColumn']]
           
fixings = data.get_pricing(symbols, start_date='2015-1-1')

# Do we wante to resample to just weekly/monthly fixings?
resample = fixings.resample('W-MON')

rets = resample.pct_change(fill_method='pad')

sol = mean_variance(rets)
#%%
plot_portfolios(rets, sol)
'''

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

'''