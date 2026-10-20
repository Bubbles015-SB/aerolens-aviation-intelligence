"""Date/time-correct synthetic scheduling, transfer feasibility, path quality.

ALL timetables, reliability probabilities, and interline assumptions are fictional.
Airport time zones are real IANA zones; flight times are not real carrier timetables.
The engine uses elapsed UTC minutes, never naive local-time subtraction.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, date, time, timezone
from zoneinfo import ZoneInfo
from collections import defaultdict
from heapq import heappush, heappop
import math

AIRPORTS = {
    'LHR': ('Europe/London', 51.4700, -0.4543), 'MAN': ('Europe/London', 53.3537, -2.2749),
    'AMS': ('Europe/Amsterdam', 52.3105, 4.7683), 'CDG': ('Europe/Paris', 49.0097, 2.5479),
    'JFK': ('America/New_York', 40.6413, -73.7781), 'BOS': ('America/New_York', 42.3656, -71.0096),
    'ATL': ('America/New_York', 33.6407, -84.4277), 'LAX': ('America/Los_Angeles', 33.9416, -118.4085),
    'MCO': ('America/New_York', 28.4312, -81.3081), 'MIA': ('America/New_York', 25.7954, -80.2901),
    'RDU': ('America/New_York', 35.8801, -78.7880), 'TPA': ('America/New_York', 27.9755, -82.5332),
    'MSY': ('America/Chicago', 29.9934, -90.2580), 'DTW': ('America/Detroit', 42.2162, -83.3554),
    'SEA': ('America/Los_Angeles', 47.4502, -122.3088),
}

# Explicitly fictional flight legs; times are locally expressed in the correct time zone.
# Carrier codes used as illustrative graph labels; NOT carrier schedule or alliance approval.
LEG_TEMPLATES = [
    ('S01','LHR','JFK','AX','09:40','12:55'),
    ('S02','LHR','BOS','AX','10:30','13:05'),
    ('S03','LHR','ATL','AX','09:15','14:15'),
    ('S04','LHR','LAX','AX','11:20','14:45'),
    ('S05','LHR','MCO','AX','11:05','15:25'),
    ('S06','MAN','JFK','AX','09:00','12:25'),
    ('S07','MAN','MCO','AX','09:40','14:10'),
    ('K01','LHR','AMS','CX','07:05','09:25'),
    ('K02','AMS','JFK','CX','12:15','15:00'),
    ('K03','AMS','BOS','CX','12:25','14:45'),
    ('A01','LHR','CDG','DX','06:50','09:05'),
    ('A02','CDG','ATL','DX','12:15','16:05'),
    ('A03','CDG','MIA','DX','11:30','15:50'),
    ('D01','JFK','MIA','BX','16:10','19:15'),
    ('D02','JFK','RDU','BX','16:00','17:50'),
    ('D03','JFK','TPA','BX','17:05','20:05'),
    ('D04','JFK','BOS','BX','17:15','18:35'),
    ('D05','ATL','MCO','BX','18:10','19:42'),
    ('D06','ATL','MSY','BX','18:15','19:05'),
    ('D07','ATL','RDU','BX','18:00','19:28'),
    ('D08','BOS','DTW','BX','17:10','19:18'),
    ('D09','LAX','SEA','BX','17:20','20:04'),
]

# Fictional minimum connection requirements, not actual airline/airport MCT rules.
MCT_MINUTES = {'JFK': 90, 'ATL': 85, 'BOS': 80, 'AMS': 65, 'CDG': 70, 'LAX': 65, 'MCO': 65}

@dataclass(frozen=True)
class Flight:
    id: str
    origin: str
    destination: str
    carrier: str
    depart_utc: datetime
    arrive_utc: datetime
    departure_local: str
    arrival_local: str
    schedule_status: str = 'synthetic'

    def export(self) -> dict:
        return dict(id=self.id, origin=self.origin, destination=self.destination,
                    carrier=self.carrier, depart_utc=self.depart_utc.isoformat().replace('+00:00','Z'),
                    arrive_utc=self.arrive_utc.isoformat().replace('+00:00','Z'),
                    depart_local=self.departure_local, arrive_local=self.arrival_local,
                    duration_minutes=int((self.arrive_utc-self.depart_utc).total_seconds()/60),
                    schedule_status=self.schedule_status)


def localized(day: date, hhmm: str, airport: str) -> datetime:
    hh, mm = map(int, hhmm.split(':'))
    return datetime.combine(day,time(hour=hh,minute=mm),tzinfo=ZoneInfo(AIRPORTS[airport][0]))


def generate_scenario(start_day=date(2026,11,3), days=7):
    if days < 1 or days > 31: raise ValueError('days must be between 1 and 31')
    flights = []
    for d in range(days):
        today = start_day + timedelta(days=d)
        for fid, a,b,carrier,dep,arr in LEG_TEMPLATES:
            dep_local=localized(today,dep,a)
            arr_local=localized(today,arr,b)
            # For a possible overnight crossing, choose the first subsequent local date
            # resulting in a sensible block time. The default templates are all same-day.
            while arr_local.astimezone(timezone.utc) <= dep_local.astimezone(timezone.utc):
                arr_local += timedelta(days=1)
            block=(arr_local-dep_local).total_seconds()/60 if dep_local.tzinfo==arr_local.tzinfo else (arr_local.astimezone(timezone.utc)-dep_local.astimezone(timezone.utc)).total_seconds()/60
            if not 40 <= block <= 950: raise ValueError(f'Physically implausible synthetic flight {fid}: {block}min')
            flights.append(Flight(f'{fid}-{today:%Y%m%d}',a,b,carrier,
                                  dep_local.astimezone(timezone.utc),arr_local.astimezone(timezone.utc),
                                  dep_local.isoformat(),arr_local.isoformat()))
    return sorted(flights,key=lambda f:(f.depart_utc,f.id))


def haversine_km(a: str,b: str):
    _,lat1,lon1=AIRPORTS[a];_,lat2,lon2=AIRPORTS[b]
    lat1,lat2,dlon=map(math.radians,[lat1,lat2,lon2-lon1]);dlat=lat2-lat1
    x=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return round(6371*2*math.asin(min(1,math.sqrt(x))),1)


def itinerary_metrics(legs:list[Flight],buffer_minutes=0):
    duration=(legs[-1].arrive_utc-legs[0].depart_utc).total_seconds()/60
    transfer_minutes=[];slacks=[]
    for a,b in zip(legs,legs[1:]):
        lay=(b.depart_utc-a.arrive_utc).total_seconds()/60
        transfer_minutes.append(int(lay))
        slacks.append(int(lay - MCT_MINUTES.get(a.destination,75) - buffer_minutes))
    # Purely hypothetical delay risk: assumed base leg reliability of 0.94,
    # transfer success logistic around 40 mins extra beyond fictional MCT.
    p_success=0.94**len(legs)
    for slack in slacks:
        p_success *= 1/(1+math.exp(-max(-40,min(300,slack-40))/30))
    distance=sum(haversine_km(l.origin,l.destination) for l in legs)
    # No emissions certification: rough distance proxy with arbitrary 0.09 kgCO2/pax-km.
    proxy_kg=round(distance*.09)
    score=max(0,min(100,round(110 - duration/20 - 12*(len(legs)-1) - 30*(1-p_success))))
    return dict(duration_minutes=int(duration),layover_minutes=transfer_minutes,
                slack_minutes=slacks,assumed_trip_completion_probability=round(p_success,4),
                distance_km=round(distance),emissions_proxy_kg=proxy_kg, illustrative_score=score)


def enumerate_itineraries(flights:list[Flight],origin:str,destination:str,
                           carriers=None,max_connections=2,buffer_minutes=15,
                           max_layover_minutes=480,max_elapsed_minutes=2400,
                           earliest_departure=None,limit=12):
    """Time-expanded directed graph search over up to max_connections transfers.

    Only one itinerary per unique combination of actual dated flight IDs. Does not assume
    codeshares, ticketing, protected transfers or real minimum connection times.
    """
    if origin not in AIRPORTS or destination not in AIRPORTS or origin==destination:
        return []
    if not 0 <= max_connections <= 3 or not 0 <= buffer_minutes <= 180:
        raise ValueError('Unreasonable search constraints')
    allowed=set(carriers) if carriers is not None else None
    edges=defaultdict(list)
    for f in flights:
        if allowed is None or f.carrier in allowed:
            edges[f.origin].append(f)
    for outgoing in edges.values(): outgoing.sort(key=lambda f:f.depart_utc)
    candidates=[]
    def visit(path, visited):
        last=path[-1]
        if last.destination==destination:
            metrics=itinerary_metrics(path,buffer_minutes)
            candidates.append(dict(flights=[x.export() for x in path],**metrics))
            return
        if len(path)>=max_connections+1:return
        for next_f in edges.get(last.destination,[]):
            if next_f.destination in visited:continue
            lay=(next_f.depart_utc-last.arrive_utc).total_seconds()/60
            minimum=MCT_MINUTES.get(last.destination,75)+buffer_minutes
            if not minimum <= lay <= max_layover_minutes:continue
            elapsed=(next_f.arrive_utc-path[0].depart_utc).total_seconds()/60
            if elapsed>max_elapsed_minutes:continue
            visit(path+[next_f],visited|{next_f.destination})
    for f in edges.get(origin,[]):
        if earliest_departure and f.depart_utc<earliest_departure:continue
        if f.destination==origin:continue
        visit([f],{origin,f.destination})
    # De-duplicate and return meaningful, score-ranked options.
    uniq={tuple(f['id'] for f in item['flights']):item for item in candidates}
    ranked=sorted(uniq.values(),key=lambda x:(-x['illustrative_score'],x['duration_minutes'],
                                               x['flights'][0]['depart_utc']))
    return ranked[:limit]


def pareto_frontier(options:list[dict]):
    """No itinerary strictly worse on all: duration, stops, assumed failure risk."""
    result=[]
    for a in options:
        d=a['duration_minutes'];s=len(a['flights'])-1;r=1-a['assumed_trip_completion_probability']
        dominated=any((b['duration_minutes']<=d and len(b['flights'])-1<=s and
                    1-b['assumed_trip_completion_probability']<=r and
                    (b['duration_minutes']<d or len(b['flights'])-1<s or
                     1-b['assumed_trip_completion_probability']<r)) for b in options if b is not a)
        if not dominated:result.append(a)
    return result
