"""Transparent, reproducible multi-route capacity portfolio optimisation.

All forecasts, shares, fares, costs, block hours and emissions are assumptions.
This module never infers airline profitability from aggregate CAA passenger data.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Sequence
from random import Random
import math

@dataclass(frozen=True)
class RouteOption:
    code: str
    weekly_demand: int
    seats_per_flight: int
    fare_gbp: float
    departure_cost_gbp: float
    variable_cost_per_pax_gbp: float
    hours_per_flight: int
    emissions_t_per_flight: int
    max_weekly_flights: int = 14
    min_weekly_flights: int = 0
    def validate(self):
        if not (len(self.code) == 3 and self.code.isalpha()): raise ValueError('Airport code must be 3 letters')
        for field in ('weekly_demand','seats_per_flight','hours_per_flight','emissions_t_per_flight','max_weekly_flights','min_weekly_flights'):
            v = getattr(self, field)
            if not isinstance(v,int) or v < 0: raise ValueError(f'{self.code}: invalid {field}')
        if self.seats_per_flight <= 0 or self.hours_per_flight <= 0: raise ValueError('Nonzero seats/hours required')
        if self.min_weekly_flights>self.max_weekly_flights: raise ValueError('Minimum flights exceed maximum')
        if self.weekly_demand<0 or min(self.fare_gbp,self.departure_cost_gbp,self.variable_cost_per_pax_gbp)<0:
            raise ValueError('Negative assumption')
        return self


def outcome(route:RouteOption, flights:int):
    route.validate()
    if not route.min_weekly_flights<=flights<=route.max_weekly_flights: raise ValueError('Flight count exceeds bounds')
    seats=route.seats_per_flight*flights
    carried=min(route.weekly_demand,seats)
    revenue=carried*route.fare_gbp
    costs=flights*route.departure_cost_gbp+carried*route.variable_cost_per_pax_gbp
    return dict(route=route.code,flights=flights,seats=seats,carried=carried,spill=max(0,route.weekly_demand-carried),
                hours=flights*route.hours_per_flight,emissions_t=flights*route.emissions_t_per_flight,
                revenue_gbp=round(revenue,2),cost_gbp=round(costs,2),contribution_gbp=round(revenue-costs,2),
                load_factor=round(carried/seats,4) if seats else None)


def optimise(routes:Sequence[RouteOption],hours_budget:int,emissions_budget_t:int|None=None):
    """Exact multiple-choice knapsack over per-route frequencies, fleet block hours and optional CO2 cap.

    Dynamic programming states are (used_hours, used_emission_t). One option per route.
    Ties prefer fewer hours, then lower emissions, then lexicographically smaller flight vector.
    This is exact for integer inputs and modeled, separable economic assumptions.
    """
    if not routes or len(routes)>12: raise ValueError('Supply 1–12 route scenarios')
    if len({r.code for r in routes})!=len(routes): raise ValueError('Repeated route')
    if not isinstance(hours_budget,int) or hours_budget<0 or hours_budget>5000:raise ValueError('Hours budget must be 0..5000')
    if emissions_budget_t is not None and (not isinstance(emissions_budget_t,int) or emissions_budget_t<0 or emissions_budget_t>20000):raise ValueError('Invalid emission cap')
    for r in routes:r.validate()
    min_h=sum(r.min_weekly_flights*r.hours_per_flight for r in routes)
    min_e=sum(r.min_weekly_flights*r.emissions_t_per_flight for r in routes)
    if min_h>hours_budget or (emissions_budget_t is not None and min_e>emissions_budget_t):
        return {'feasible':False,'reason':'Minimum frequencies exceed resource budget','routes':[], 'contribution_gbp':None}
    frontier={(0,0):(0.0,())}
    for r in routes:
        next_frontier={}
        for (h,e),(score,chosen) in frontier.items():
            for n in range(r.min_weekly_flights,r.max_weekly_flights+1):
                oh=n*r.hours_per_flight;oe=n*r.emissions_t_per_flight
                if h+oh>hours_budget or (emissions_budget_t is not None and e+oe>emissions_budget_t):continue
                cand=score+outcome(r,n)['contribution_gbp']
                key=(h+oh,e+oe)
                prev=next_frontier.get(key)
                if prev is None or cand>prev[0]+1e-8 or (abs(cand-prev[0])<=1e-8 and chosen+(n,)<prev[1]):
                    next_frontier[key]=(cand,chosen+(n,))
        frontier=next_frontier
        if not frontier:raise AssertionError('Unexpected empty dynamic-programming frontier')
    used,(score,choices)=min(frontier.items(),key=lambda kv:(-kv[1][0],kv[0][0],kv[0][1],kv[1][1]))
    results=[outcome(r,n) for r,n in zip(routes,choices)]
    assert sum(r['hours'] for r in results)==used[0]
    assert sum(r['emissions_t'] for r in results)==used[1]
    return dict(feasible=True,method='exact multiple-choice dynamic programming; integer resource units',
                assumed_inputs=True,hours_budget=hours_budget,emissions_budget_t=emissions_budget_t,
                hours_used=used[0],emissions_used_t=used[1],contribution_gbp=round(score,2),
                hours_utilisation=round(used[0]/hours_budget,4) if hours_budget else 0,
                routes=results,states_evaluated=len(frontier))


def stress_portfolio(routes, hours_budget, emissions_budget_t=None,draws=200,seed=310):
    """Illustrative uncertainty stress, NOT an empirical confidence interval.

    Frequencies remain fixed to the optimal base plan; scenario outcome measures robustness.
    No spurious retroactive reoptimisation with knowledge of future uncertainty.
    """
    if not 10<=draws<=2000:raise ValueError('draws 10..2000')
    result=optimise(routes,hours_budget,emissions_budget_t)
    if not result['feasible']:return result
    rng=Random(seed); totals=[]
    for _ in range(draws):
        common=rng.gauss(0,0.08); net=0.0
        for r,plan in zip(routes,result['routes']):
            market=round(max(0,r.weekly_demand*(1+common+rng.gauss(0,.10))))
            fare=max(0,r.fare_gbp*(1+rng.gauss(0,.08)))
            departure_cost=max(0,r.departure_cost_gbp*(1+rng.gauss(0,.09)))
            d=RouteOption(r.code,market,r.seats_per_flight,fare,departure_cost,r.variable_cost_per_pax_gbp,
                          r.hours_per_flight,r.emissions_t_per_flight,r.max_weekly_flights,r.min_weekly_flights)
            net+=outcome(d,plan['flights'])['contribution_gbp']
        totals.append(net)
    totals.sort()
    def pct(p):return totals[round((len(totals)-1)*p)]
    return dict(base=result,draws=draws,seed=seed,p05_gbp=round(pct(.05)),p50_gbp=round(pct(.5)),p95_gbp=round(pct(.95)),
                simulated_probability_negative=round(sum(x<0 for x in totals)/len(totals),3),
                scenario_warning='Illustrative distributions only; the assumptions are NOT fitted to airline data.')
