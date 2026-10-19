"""Predeclared paired binary contrasts; no optional statistical dependency."""
import math

def binomial_tail(k,n,p,*,upper=False):
    indices=range(k,n+1) if upper else range(k+1)
    return min(1.,max(0.,math.fsum(math.comb(n,i)*p**i*(1-p)**(n-i) for i in indices)))

def exact_cell_interval(k,n,alpha=.025):
    """Two-sided Clopper-Pearson; default 97.5% for simultaneous two-cell coverage."""
    if not 0<=k<=n or n<1:raise ValueError('Invalid binomial counts')
    tail=alpha/2
    if k==0:low=0.
    else:
        lo,hi=0.,1.
        for _ in range(70):
            mid=(lo+hi)/2
            if binomial_tail(k,n,mid,upper=True)<tail:lo=mid
            else:hi=mid
        low=(lo+hi)/2
    if k==n:high=1.
    else:
        lo,hi=0.,1.
        for _ in range(70):
            mid=(lo+hi)/2
            if binomial_tail(k,n,mid)>tail:lo=mid
            else:hi=mid
        high=(lo+hi)/2
    return low,high

def paired_contrast(condition,control):
    if len(condition)!=len(control) or not condition:raise ValueError('Nonempty paired samples required')
    n=len(condition);wins=sum(bool(x) and not bool(y) for x,y in zip(condition,control));losses=sum(bool(y) and not bool(x) for x,y in zip(condition,control))
    m=wins+losses;p=min(1.,2*binomial_tail(min(wins,losses),m,.5)) if m else 1.
    wl,wu=exact_cell_interval(wins,n);ll,lu=exact_cell_interval(losses,n)
    return {'tasks':n,'wins':wins,'losses':losses,'both_success':sum(bool(x) and bool(y) for x,y in zip(condition,control)),
            'both_failure':sum(not bool(x) and not bool(y) for x,y in zip(condition,control)),
            'difference':(wins-losses)/n,'lower':max(-1.,wl-lu),'upper':min(1.,wu-ll),'mcnemar_exact_p':p,
            'interval_method':'Bonferroni simultaneous exact Clopper-Pearson discordant-cell intervals; at least 95% pointwise coverage'}

def holm(rows):
    previous=0.;count=len(rows)
    for rank,index in enumerate(sorted(range(count),key=lambda i:rows[i]['mcnemar_exact_p'])):
        adjusted=max(previous,min(1.,(count-rank)*rows[index]['mcnemar_exact_p']));rows[index]['holm_p']=adjusted;previous=adjusted
    return rows
