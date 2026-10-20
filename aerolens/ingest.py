"""Optional user-supplied BTS T-100 segment input validation and aggregation.

No live BTS data are bundled. This is a real adapter to prepare an actually
obtained extract; it cannot claim carrier-specific statistics until run on one.
"""
import csv
from collections import defaultdict
from pathlib import Path

REQUIRED = {'ORIGIN', 'DEST', 'PASSENGERS', 'SEATS', 'DEPARTURES_PERFORMED', 'YEAR', 'MONTH'}
CARRIER_FIELDS=('UNIQUE_CARRIER','OP_UNIQUE_CARRIER','CARRIER')


def as_nonnegative_integer(s,name,row_num):
    try:
        raw=float(str(s).replace(',',''))
        if raw<0 or int(raw)!=raw:raise ValueError()
        return int(raw)
    except (ValueError,TypeError):raise ValueError(f'Line {row_num}: invalid {name}={s!r}')


def import_bts(path,only_lhr=True):
    """Parse a conventional BTS T100 segment CSV with row-level checks.

    Bidirectional origin-destination pairs are aggregated by year/month/carrier.
    Load factor is computed as passenger / seats ONLY on valid segment records.
    """
    results=defaultdict(lambda:dict(passengers=0,seats=0,departures=0,records=0))
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        rows=csv.DictReader(f)
        fields=set(rows.fieldnames or ())
        missing=REQUIRED-fields
        if missing:raise ValueError(f'BTS CSV missing required fields: {sorted(missing)}')
        carrier=next((x for x in CARRIER_FIELDS if x in fields),None)
        if not carrier:raise ValueError('BTS CSV missing carrier identifier')
        for i,r in enumerate(rows,2):
            a,b=r['ORIGIN'].strip().upper(),r['DEST'].strip().upper()
            if not (len(a)==3 and len(b)==3 and a.isalpha() and b.isalpha()):raise ValueError(f'Line {i}: invalid airport')
            if a==b:continue
            if only_lhr and 'LHR' not in (a,b):continue
            yr=as_nonnegative_integer(r['YEAR'],'YEAR',i)
            month=as_nonnegative_integer(r['MONTH'],'MONTH',i)
            if not 1990<=yr<=2100 or not 1<=month<=12:raise ValueError(f'Line {i}: bad reporting period')
            pax=as_nonnegative_integer(r['PASSENGERS'],'PASSENGERS',i)
            seats=as_nonnegative_integer(r['SEATS'],'SEATS',i)
            dep=as_nonnegative_integer(r['DEPARTURES_PERFORMED'],'DEPARTURES_PERFORMED',i)
            if pax>seats:raise ValueError(f'Line {i}: passengers exceed seats; check segment and fields')
            if dep==0 and (pax or seats):raise ValueError(f'Line {i}: zero departures but nonzero traffic')
            carr=r[carrier].strip().upper()
            if not carr:raise ValueError(f'Line {i}: missing carrier')
            key=(yr,month,carr,*sorted((a,b)))
            rec=results[key];rec['passengers']+=pax;rec['seats']+=seats;rec['departures']+=dep;rec['records']+=1
    out=[]
    for (yr,mo,carr,a,b),d in sorted(results.items()):
        out.append(dict(year=yr,month=mo,carrier=carr,airport_a=a,airport_b=b,**d,
                        seat_load_factor=round(d['passengers']/d['seats'],4) if d['seats'] else None))
    return out


def export_bts_summary(source,outpath):
    rows=import_bts(source)
    if not rows:raise ValueError('No matching LHR segments in extract')
    names=list(rows[0])
    with Path(outpath).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(rows)
    return len(rows)
