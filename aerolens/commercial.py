"""Transparent commercial *what-if* models; not any specific airline economics.

These calculations have illustrative inputs only: no actual costs, fare, airline shares,
revenue, capacity or operational reliability are bundled or represented.
"""
from dataclasses import dataclass, asdict
from random import Random
from statistics import mean
import math

@dataclass(frozen=True)
class Inputs:
    total_market_passengers: int
    assumed_capture_pct: float = 5.0
    annual_departures: int = 650
    seats_per_departure: int = 260
    net_fare_gbp: float = 550.0
    cost_per_departure_gbp: float = 46000.0
    variable_cost_per_passenger_gbp: float = 55.0
    annual_fixed_cost_gbp: float = 1_200_000.0
    market_uncertainty_pct: float = 10.0
    capture_uncertainty_pct: float = 25.0
    fare_uncertainty_pct: float = 12.0
    flight_cost_uncertainty_pct: float = 10.0

    def validate(self):
        if self.total_market_passengers < 0: raise ValueError('market passenger total must be nonnegative')
        if not (0 <= self.assumed_capture_pct <= 100): raise ValueError('capture percentage must be 0-100')
        if self.annual_departures <= 0 or self.seats_per_departure <= 0: raise ValueError('capacity must be positive')
        if self.net_fare_gbp <= 0 or self.cost_per_departure_gbp < 0 or self.variable_cost_per_passenger_gbp < 0 or self.annual_fixed_cost_gbp < 0:
            raise ValueError('fare and costs must be nonnegative; fare positive')
        for field in ('market_uncertainty_pct','capture_uncertainty_pct','fare_uncertainty_pct','flight_cost_uncertainty_pct'):
            if not 0 <= getattr(self,field) <= 100: raise ValueError('uncertainties must be 0-100%')
        return self


def economics(x: Inputs):
    x.validate()
    seats=x.annual_departures*x.seats_per_departure
    desired=x.total_market_passengers*x.assumed_capture_pct/100
    carried=min(desired,seats)
    denied=max(0,desired-seats)
    gross=carried*x.net_fare_gbp
    costs=x.annual_departures*x.cost_per_departure_gbp + carried*x.variable_cost_per_passenger_gbp + x.annual_fixed_cost_gbp
    contribution=gross-costs
    marginal=x.net_fare_gbp-x.variable_cost_per_passenger_gbp
    breakeven_pax=(x.annual_departures*x.cost_per_departure_gbp+x.annual_fixed_cost_gbp)/marginal if marginal>0 else None
    breakeven_lf=breakeven_pax/seats if breakeven_pax is not None else None
    return dict(available_seats=seats,requested_passengers=round(desired),carried_passengers=round(carried),
                unserved_demand=round(denied),load_factor=round(carried/seats,4),
                gross_ticket_sales_gbp=round(gross),total_model_cost_gbp=round(costs),
                indicative_contribution_gbp=round(contribution),
                breakeven_passengers=round(breakeven_pax) if breakeven_pax is not None else None,
                breakeven_load_factor=round(breakeven_lf,4) if breakeven_lf is not None else None,
                capacity_sufficient=desired<=seats,
                breakeven_feasible=breakeven_lf is not None and breakeven_lf<=1)


def quantile(sorted_values, frac):
    index=(len(sorted_values)-1)*frac
    i=int(index); j=min(i+1,len(sorted_values)-1)
    return sorted_values[i]+(sorted_values[j]-sorted_values[i])*(index-i)


def simulate(x: Inputs, draws=5000, seed=20261019):
    """Seeded illustrative uncertainty stress test, *not* empirical forecast.

    Gaussian std deviations are based on arbitrary assumptions, with each
    variable independently sampled. No inference from actual airline variances.
    """
    x.validate()
    if not 100 <= draws <= 100000: raise ValueError('Draws must be 100..100000')
    rng=Random(seed); outputs=[]; lfs=[]
    for _ in range(draws):
        market=max(0,rng.gauss(x.total_market_passengers,x.total_market_passengers*x.market_uncertainty_pct/100))
        share=max(0,min(100,rng.gauss(x.assumed_capture_pct,x.assumed_capture_pct*x.capture_uncertainty_pct/100)))
        fare=max(.01,rng.gauss(x.net_fare_gbp,x.net_fare_gbp*x.fare_uncertainty_pct/100))
        depcost=max(0,rng.gauss(x.cost_per_departure_gbp,x.cost_per_departure_gbp*x.flight_cost_uncertainty_pct/100))
        y=economics(Inputs(total_market_passengers=round(market),assumed_capture_pct=share,
                           annual_departures=x.annual_departures,seats_per_departure=x.seats_per_departure,
                           net_fare_gbp=fare,cost_per_departure_gbp=depcost,
                           variable_cost_per_passenger_gbp=x.variable_cost_per_passenger_gbp,
                           annual_fixed_cost_gbp=x.annual_fixed_cost_gbp))
        outputs.append(y['indicative_contribution_gbp']);lfs.append(y['load_factor'])
    outputs.sort();lfs.sort()
    return dict(draws=draws,seed=seed,model='Independent Gaussian perturbations of invented inputs; NOT an empirical forecast',
                contribution_p05_gbp=round(quantile(outputs,.05)),
                contribution_p50_gbp=round(quantile(outputs,.5)),
                contribution_p95_gbp=round(quantile(outputs,.95)),
                assumed_probability_positive=round(sum(v>0 for v in outputs)/draws,4),
                load_factor_p05=round(quantile(lfs,.05),4),load_factor_p95=round(quantile(lfs,.95),4))
