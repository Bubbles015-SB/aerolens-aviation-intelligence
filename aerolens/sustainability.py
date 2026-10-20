"""Air transport emissions scenario, not measured airline environmental reporting.

Great circle distance is a lower-bound geometry proxy, not flown route distance.
Fuel consumption is *user-assumed*, not calibrated to a certified aircraft type.
"""
from __future__ import annotations
from math import radians,sin,cos,atan2,sqrt,isfinite


def great_circle_km(lat1,lon1,lat2,lon2):
    for x in (lat1,lon1,lat2,lon2):
        if not isfinite(x):raise ValueError('Coordinates must be finite')
    if max(abs(lat1),abs(lat2))>90 or max(abs(lon1),abs(lon2))>180:raise ValueError('Invalid geographic coordinates')
    a,b=radians(lat1),radians(lat2)
    dlat=b-a; dlon=radians(lon2-lon1)
    h=sin(dlat/2)**2+cos(a)*cos(b)*sin(dlon/2)**2
    return 6371.0088*2*atan2(sqrt(h),sqrt(max(0,1-h)))


def flight_emission_scenario(distance_km,flights,seat_capacity,load_factor,fuel_burn_kg_per_hour,
                             block_hours,detour_factor=1.07,co2_factor=3.16):
    """Compute fuel and CO2 conditional on transparent, nonempirical assumptions."""
    if distance_km<=0 or block_hours<=0 or detour_factor<1 or flights<0 or not isinstance(flights,int):
        raise ValueError('Distance/hours/flight count or detour factor invalid')
    if seat_capacity<=0 or not isinstance(seat_capacity,int) or not 0<load_factor<=1 or fuel_burn_kg_per_hour<=0 or co2_factor<=0:
        raise ValueError('Seat, fuel, load or factor invalid')
    fuel=flights*block_hours*fuel_burn_kg_per_hour
    co2=fuel*co2_factor
    passengers=flights*seat_capacity*load_factor
    passenger_km=passengers*distance_km*detour_factor
    return dict(flights=flights,route_distance_km=round(distance_km,1),assumed_flown_distance_km=round(distance_km*detour_factor,1),
                estimated_fuel_t=round(fuel/1000,2),estimated_co2_t=round(co2/1000,2),
                assumed_passengers=round(passengers,1),emissions_kg_per_passenger_km=round(co2/passenger_km,4) if passenger_km else None,
                methodology='Illustrative fuel/hour × hours × flights × CO2 factor; excludes non-CO2 impacts and upstream emissions')
