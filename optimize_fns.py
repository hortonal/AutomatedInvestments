import numpy as np
import cvxpy
import matplotlib.pyplot as plt

def mean_variance(returns, samples=100):
    # Setup the optimization problem
    p = returns.mean().as_matrix()
    w = cvxpy.Variable(len(p))
    gamma = cvxpy.Parameter(sign='positive')
    
    
    ret = p * w
    
    covs = returns.cov().as_matrix()
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
    for i in sols:
        plt.plot(i['sd'], i['mean'], 'bs')
        
    p = rets.mean().as_matrix()
    covs = rets.cov().as_matrix()
    for i in range(len(p)):
        plt.plot(cvxpy.sqrt(covs[i,i]).value, p[i], 'ro')
        
    plt.xlabel('Standard deviation')
    plt.ylabel('Return')
    plt.show()
    
def plot_weights(rets, sol):
    plt.bar([x[1] for x in rets.columns.values], np.squeeze(np.asarray(sol['wgts'])))
    plt.show()
