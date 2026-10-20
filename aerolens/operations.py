"""Optional external operational flight schedule import and connection simulation.

No real flight schedules are bundled. This adapter only validates uploaded data.
Required field provenance is user-declared, not independently authenticated.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from hashlib import sha256
from random import Random
from statistics import mean
import csv,math
from aerolens.connectivity import AIRPORTS,Flight

FIELDS=['flight_id','carrier','origin','destination','departure_local','arrival_local']

def _tz_checked(iso,airport):
    dt=datetime.fromisoformat(iso.replace('Z','+00:00'))
    if dt.tzinfo is None or dt.utcoffset() is None:raise ValueError('Times must include numeric UTC offsets')
    if airport not in AIRPORTS:raise ValueError(f'Airport {airport} not in the supported time-zone dictionary')
    correct=dt.astimezone(ZoneInfo(AIRPORTS[airport][0]))
    if correct.replace(tzinfo=None)!=dt.replace(tzinfo=None) or correct.utcoffset()!=dt.utcoffset():
        raise ValueError(f'Incorrect time-zone offset for {airport}: {iso}')
    return dt

def import_schedule(csvfile,source_declaration):
    """Read a dated local/offset schedule, validate UTC chronology, provenance & duplicates.

    The importer checks format, not actual flight existence or interline protections.
    """
    path=Path(csvfile)
    if len(source_declaration.strip())<12:raise ValueError('Source declaration needs a meaningful provenance note')
    with path.open(encoding='utf-8-sig',newline='') as f:
        rd=csv.DictReader(f)
        if rd.fieldnames!=FIELDS:raise ValueError(f'Expected these exact CSV headers: {FIELDS}')
        seen=set();flights=[]
        for ix,r in enumerate(rd,2):
            flight_id=r['flight_id'].strip();carrier=r['carrier'].strip().upper()
            a=r['origin'].strip().upper();b=r['destination'].strip().upper()
            if not flight_id or flight_id in seen:raise ValueError(f'Line {ix}: duplicate/missing flight ID')
            if not carrier or not a or not b or a==b:raise ValueError(f'Line {ix}: invalid carrier or airport pair')
            seen.add(flight_id)
            depart=_tz_checked(r['departure_local'],a)
            arrive=_tz_checked(r['arrival_local'],b)
            elapsed=(arrive.astimezone(timezone.utc)-depart.astimezone(timezone.utc)).total_seconds()/60
            if not 20<=elapsed<=1200:raise ValueError(f'Line {ix}: invalid elapsed flight time')
            flights.append(Flight(flight_id,a,b,carrier,depart.astimezone(timezone.utc),arrive.astimezone(timezone.utc),
                                  depart.isoformat(),arrive.isoformat(),schedule_status='user_supplied_unverified'))
    if not flights:raise ValueError('No flight legs in file')
    return dict(flights=sorted(flights,key=lambda x:x.depart_utc),source=source_declaration,
                sha256=sha256(path.read_bytes()).hexdigest(),authenticity='NOT independently verified')


def connection_reliability(legs,assumed_minimum_minutes=75,draws=5000,seed=42,
                           assumed_leg_cancel_probability=.01,assumed_delay_mean_minutes=12,
                           assumed_delay_std_minutes=16,assumed_shared_shock_std_minutes=14):
    """Simulate whether a fixed itinerary is protected against hypothetical disruptions.

    Random arrival and departure delays include a shared weather-style shock;
    normal draws truncated to avoid early arrivals. Does not model reaccommodation.
    These are not empirical reliability estimates or approved MCT constraints.
    """
    if not 2<=len(legs)<=5:raise ValueError('Supply 2..5 connected dated flights')
    if not 100<=draws<=50000:raise ValueError('draws 100..50000')
    for f,g in zip(legs,legs[1:]):
        if f.destination!=g.origin:raise ValueError('Non-contiguous itinerary')
        if (g.depart_utc-f.arrive_utc).total_seconds()/60<assumed_minimum_minutes:
            raise ValueError('Connection is below assumed minimum before delays')
    if not 0<=assumed_leg_cancel_probability<=1 or min(assumed_delay_mean_minutes,assumed_delay_std_minutes,
                                                       assumed_shared_shock_std_minutes)<0:raise ValueError('Negative disruption parameter')
    rng=Random(seed);complete=0;slack_all=[]
    for _ in range(draws):
        if any(rng.random()<assumed_leg_cancel_probability for _ in legs):continue
        shock=rng.gauss(0,assumed_shared_shock_std_minutes)
        arrivals=[max(0,shock+rng.gauss(assumed_delay_mean_minutes,assumed_delay_std_minutes)) for _ in legs]
        departures=[max(0,.4*shock+rng.gauss(assumed_delay_mean_minutes*.5,assumed_delay_std_minutes*.7)) for _ in legs]
        margins=[]
        for i in range(len(legs)-1):
            published=(legs[i+1].depart_utc-legs[i].arrive_utc).total_seconds()/60
            margins.append(published+departures[i+1]-arrivals[i]-assumed_minimum_minutes)
        if all(m>=0 for m in margins):complete+=1;slack_all.append(min(margins))
    return dict(draws=draws,seed=seed,assumed_completion_rate=round(complete/draws,4),
                realised_survivor_mean_slack_minutes=round(mean(slack_all),1) if slack_all else None,
                classification='MODELLED DISRUPTION ONLY',source='Hypothetical Gaussian and Bernoulli assumptions, not airline reliability data')
