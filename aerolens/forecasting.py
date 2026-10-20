"""Out-of-sample monthly baseline forecast comparison.

Requires at least 30 genuine months. Two annual observations do not support seasonal forecasts.
The interval is a back-test error band, NOT a confidence interval.
"""
from __future__ import annotations
import csv
from pathlib import Path
from statistics import median


def read_monthly_csv(file):
    """month,passengers; expects continuous YYYY-MM sorted months and nonnegative integers."""
    with Path(file).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=['month','passengers']:raise ValueError('Expected month,passengers')
        rows=[]
        for r in reader:
            m=r['month']
            if len(m)!=7 or m[4]!='-' or not(m[:4]+m[5:]).isdigit() or not 1<=int(m[5:])<=12:
                raise ValueError('Month must be YYYY-MM')
            try: n=int(r['passengers'])
            except (ValueError,TypeError):raise ValueError('Invalid passengers')
            if n<0:raise ValueError('Negative passengers')
            rows.append((m,n))
    if len(rows)<30:raise ValueError('At least 30 genuine monthly observations needed')
    months=[12*int(m[:4])+int(m[5:])-1 for m,_ in rows]
    if any(b-a!=1 for a,b in zip(months,months[1:])):raise ValueError('Monthly data must be consecutive, unique and ordered')
    return rows


def evaluate_and_forecast(rows,horizon=6):
    """Prequential seasonal-naive and 12m-level-trend rolling evaluation, no leakage."""
    y=[v for _,v in rows]
    if len(y)<30:raise ValueError('Requires >=30 months')
    if not 1<=horizon<=12:raise ValueError('Horizon must be 1..12')
    errors={'seasonal_naive':[],'seasonal_level':[]}
    for t in range(24,len(y)):
        methods={'seasonal_naive':y[t-12],
                 'seasonal_level':max(0,y[t-12]+(sum(y[t-12:t])-sum(y[t-24:t-12]))/12)}
        for method,value in methods.items():errors[method].append(abs(y[t]-value))
    mae={k:round(sum(e)/len(e),2) for k,e in errors.items()}
    winning=min(mae,key=lambda k:(mae[k],k))
    abs_res=sorted(errors[winning]);uncertainty=abs_res[int(.9*(len(abs_res)-1))]
    last_month=12*int(rows[-1][0][:4])+int(rows[-1][0][5:])-1
    current=sum(y[-12:]);previous=sum(y[-24:-12])
    drift=(current-previous)/12
    output=[]
    for step in range(1,horizon+1):
        base=y[-12+(step-1)]
        point=max(0,base+(drift if winning=='seasonal_level' else 0))
        index=last_month+step;month=f'{index//12:04d}-{index%12+1:02d}'
        output.append(dict(month=month,passengers_model=round(point),
                           low_backtest_band=max(0,round(point-uncertainty)),high_backtest_band=round(point+uncertainty)))
    return dict(chosen=winning,backtest_months=len(errors[winning]),backtest_mae=mae,
                backtest_abs_error_p90=round(uncertainty),horizon=output,
                caution='Rolling one-step test errors; heuristic interval, NOT a forecast confidence interval. No causal or structural capacity effects.')
