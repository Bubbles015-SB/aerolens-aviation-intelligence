/* AeroLens 3 — general aviation operations intelligence modules. */
(()=>{'use strict';
const E=window.AEROLENS_ENTERPRISE;
if(!E)throw Error('Enterprise bundle missing. Run scripts/build_enterprise.py.');
const $=id=>document.getElementById(id);
const fmt=(x,d=0)=>Number(x).toLocaleString('en-GB',{maximumFractionDigits:d});
const gbp=x=>'£'+(x<0?'-':'')+fmt(Math.abs(Math.round(x)));
const esc=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const clamp=(x,a,b)=>Math.max(a,Math.min(x,b));
const plus=x=>Number(x)>=0?'positive':'negative';
const selection=['fleet','sustain','assurance','forecast'];
const title=['Fleet portfolio','Sustainability studio','Engineering assurance','Forecasting lab'];
const panel=(k,head,html)=>`<section class="panel enterprise-panel"><div class="panel-kicker">${k}</div><h2>${head}</h2>${html}</section>`;
const headline=(eyebrow,head,sub,badge)=>`<div class="eyebrow"><span class="eyebrow-line"></span>${eyebrow}</div><div class="page-head"><div><h1>${head}</h1><p class="lede">${sub}</p></div><div class="year-pill"><span>DATA CLASS</span><strong>${badge}</strong></div></div>`;
const warning=(text)=>`<div class="insight-alert amber-alert"><span class="alert-icon">!</span><p>${text}</p></div>`;
const kpis=(rows)=>`<div class="adv-metrics">${rows.map(([title,v,foot])=>`<div class="adv-kpi"><small>${title}</small><strong>${v}</strong><em>${foot}</em></div>`).join('')}</div>`;
const slider=(id,name,min,max,step,value,unit='')=>`<div class="slider-header"><label class="field-label" for="${id}">${name}</label><strong id="${id}Text">${value}${unit}</strong></div><input class="al3slider" type="range" id="${id}" min="${min}" max="${max}" step="${step}" value="${value}" />`;
const tbl=(headers,rows)=>`<div class="table-overflow"><table class="al3table"><thead><tr>${headers.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
const download=(name,content,mime='text/plain')=>{const u=URL.createObjectURL(new Blob([content],{type:mime+';charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),600)};
const routeList=E.routes;
let lastPortfolio=null,lastForecast=null;
const options=routeList.map(r=>({code:r.code,city:r.city,demand:r.assumed_weekly_demand,seats:r.seats_per_flight,
 fare:r.assumed_fare_gbp,flightCost:r.assumed_departure_cost_gbp,varCost:r.assumed_variable_cost_per_pax_gbp,
 hours:r.assumed_block_hours_per_flight,emissions:r.assumed_emissions_t_per_flight,max:r.max_weekly_flights}));

function navSetup(){
 const nav=document.querySelector('.navigation'),select=$('mobilePageSelect'),content=document.querySelector('.content');
 if(!nav||!select||!content)return;
 selection.forEach((id,i)=>{
  const section=document.createElement('section');section.id='page-'+id;section.className='page';section.setAttribute('aria-label',title[i]);
  document.querySelector('footer.footer').before(section);
  let label=title[i],glyph=['▥','◉','▤','▦'][i];
  const b=document.createElement('button');b.className='nav-item';b.dataset.page=id;
  b.innerHTML=`<span class="nav-glyph">${glyph}</span> ${label} <span class="nav-n">${String(i+6).padStart(2,'0')}</span>`;
  nav.appendChild(b);
  select.insertAdjacentHTML('beforeend',`<option value="${id}">${label}</option>`);
  b.addEventListener('click',()=>activate(id));
 });
 select.addEventListener('change',e=>{if(selection.includes(e.target.value))activate(e.target.value)});
}
function activate(id){
 document.querySelectorAll('.page').forEach(n=>n.classList.toggle('active',n.id==='page-'+id));
 document.querySelectorAll('.nav-item').forEach(n=>n.classList.toggle('active',n.dataset.page===id));
 $('mobilePageSelect').value=id;$('crumb').textContent=title[selection.indexOf(id)].toUpperCase();window.scrollTo(0,0);
}

function fleetSetup(){
 $('page-fleet').innerHTML=headline('OPERATIONS RESEARCH / INTEGER OPTIMISATION',
   'Fleet allocation <em>decision studio.</em>',
   'Choose a weekly flying programme under finite block-hours and an optional emissions limit. The optimiser compares every feasible frequency portfolio.','SCENARIO')+
  warning('<strong>Training assumptions, not airline financials.</strong> Weekly route demand, seats, hours, fares, costs and emissions per flight are illustrative. Only the separate 2025 all-carrier airport-pair market column traces to official CAA counts.')+
  `<div class="adv-grid-left">`+
   panel('01 / RESOURCE LIMITS','Constrained flying programme',
     slider('fpHours','TOTAL WEEKLY FLEET BLOCK HOURS',0,400,10,200,' h')+
     slider('fpCarbon','TOTAL ILLUSTRATIVE CO₂ CAP',0,5000,100,2100,' t')+
     slider('fpFare','FARE SCENARIO MULTIPLIER',50,150,5,100,'%')+
     `<div class="adv-detail">Max 8 flights/route/week. A route consumes block-hours and its scenario carbon tonnes. The solver optimises financial contribution over integer frequencies; no actual airline slot, aircraft rotation or fleet constraints are asserted.</div>
       <button class="button button-outline" id="fpExport">↧ Export allocation CSV</button>`)+
   panel('02 / PORTFOLIO OPTIMUM','Recommended hypothetical allocation',
     `<div id="fpStatus" class="al3status">Calculating allocation...</div><div id="fpKpis"></div><div id="fpBars" class="al3bars"></div>`)+
  `</div>`+panel('03 / ROUTE DECISION TABLE','All scenario routes',`<div id="fpTable"></div>`)+
  panel('04 / EXPERIMENT LIMITS','When would this become a real airline optimiser?',
   `<div class="al3grid3"><div><strong>Required demand data</strong><p>Booking curves, class mix, transfer flows and route yields.</p></div><div><strong>Operational constraints</strong><p>Real aircraft tail rotations, turn times, slot availability and maintenance.</p></div><div><strong>Validation</strong><p>Shadow-test scenarios against known schedules, costs and realised outcomes.</p></div></div>`);
 for(const id of ['fpHours','fpCarbon','fpFare'])$(id).addEventListener('input',renderFleet);
 $('fpExport').addEventListener('click',()=>{if(!lastPortfolio?.feasible)return;download('aerolens_modelled_fleet_allocation.csv',
 ['route,weekly_flights,carried_passengers,modelled_contribution_gbp,block_hours,modelled_co2_t',...lastPortfolio.routes.map(x=>`${x.code},${x.n},${x.carried},${x.contribution.toFixed(2)},${x.hours},${x.emissions}`)].join('\r\n'),'text/csv')});
 renderFleet();
}
function routeOutcome(route,n){
 const carried=Math.min(route.demand,route.seats*n),margin=carried*(route.fare-route.varCost)-n*route.flightCost;
 return {code:route.code,city:route.city,n,carried,spill:Math.max(0,route.demand-carried),
         contribution:margin,hours:n*route.hours,emissions:n*route.emissions};
}
function solvePortfolio(routes,hoursBudget,carbonBudget){
 let states=new Map([['0|0',{score:0,hours:0,carbon:0,choice:[]}]]);
 for(const route of routes){const next=new Map();
  for(const rec of states.values())for(let n=0;n<=route.max;n++){
   const o=routeOutcome(route,n),hours=rec.hours+o.hours,carbon=rec.carbon+o.emissions;
   if(hours>hoursBudget||carbon>carbonBudget)continue;
   const key=hours+'|'+carbon,score=rec.score+o.contribution,prior=next.get(key);
   if(!prior||score>prior.score+1e-6)next.set(key,{score,hours,carbon,choice:[...rec.choice,n]});
  }states=next;
  if(!states.size)return {feasible:false};
 }
 const best=[...states.values()].sort((a,b)=>b.score-a.score||a.hours-b.hours||a.carbon-b.carbon)[0];
 return {feasible:true,score:best.score,hours:best.hours,carbon:best.carbon,
   routes:routes.map((route,i)=>routeOutcome(route,best.choice[i]))};
}
function renderFleet(){
 const h=+$('fpHours').value,c=+$('fpCarbon').value,fa=+$('fpFare').value;
 $('fpHoursText').textContent=h+' h';$('fpCarbonText').textContent=c+' t';$('fpFareText').textContent=fa+'%';
 const prepared=options.map(x=>({...x,fare:x.fare*fa/100}));lastPortfolio=solvePortfolio(prepared,h,c);
 if(!lastPortfolio.feasible){$('fpStatus').textContent='No feasible schedule under selected constraints.';return;}
 const x=lastPortfolio,carried=x.routes.reduce((a,r)=>a+r.carried,0),spill=x.routes.reduce((a,r)=>a+r.spill,0);
 $('fpStatus').textContent='EXACT INTEGER OPTIMISATION · '+fmt(x.routes.length)+' HYPOTHETICAL ROUTES';
 $('fpKpis').innerHTML=kpis([['Modelled weekly contribution',gbp(x.score),'Illustrative GBP; not airline earnings'],
 ['Fleet block hours',`${x.hours} / ${h}`,'Hours consumed by selected programme'],
 ['Modelled CO₂',`${x.carbon} / ${c} t`,'Assumptions, not measured flight data'],
 ['Carried / unmet demand',`${fmt(carried)} / ${fmt(spill)}`,'Under assumed weekly route demand']]);
 $('fpBars').innerHTML=x.routes.map(r=>`<div class="al3bar"><div><b>${esc(r.code)}</b><small>${esc(r.city)}</small></div><div class="al3track"><span style="width:${r.n/8*100}%"></span></div><strong>${r.n} flights</strong></div>`).join('');
 $('fpTable').innerHTML=tbl(['ROUTE','FLIGHTS / WEEK','CARRIED / SPILL','BLOCK HOURS','CO₂ ASSUMPTION','MODELED CONTRIBUTION'],
 x.routes.map(r=>[esc(r.code),fmt(r.n),`${fmt(r.carried)} / ${fmt(r.spill)}`,fmt(r.hours),fmt(r.emissions)+' t',`<b class="${plus(r.contribution)}">${gbp(r.contribution)}</b>`]));
}

function sustainSetup(){
 $('page-sustain').innerHTML=headline('SUSTAINABILITY / TRANSPARENT UNIT MODEL','Flight emissions <em>scenario studio.</em>',
  'Evaluate fuel-use assumptions, passenger intensity and route geometry without presenting scenario numbers as verified aircraft emissions.','SCENARIO')+
 warning('<strong>Scenario model only.</strong> Great-circle distance is geographical geometry, not an actual flown track. Fuel burn, block hours and load factor are adjustable assumptions; the calculation excludes non-CO₂ impacts.')+
 `<div class="adv-grid-left">`+
 panel('01 / OPERATING ASSUMPTIONS','Route and aircraft inputs',
 `<label class="field-label" for="suRoute">ROUTE (LHR TO)</label><select id="suRoute" class="big-select">${routeList.map(r=>`<option value="${r.code}">${r.code} · ${esc(r.city)}</option>`).join('')}</select>`+
 slider('suFuel','FUEL BURN (KG / BLOCK HOUR)',2500,12000,250,5500,' kg/h')+
 slider('suLoad','ASSUMED PASSENGER LOAD FACTOR',40,100,5,82,'%')+
 slider('suFlights','WEEKLY DEPARTURES',1,30,1,8,'')+
 `<div class="adv-detail">Assumed aircraft capacity: 250 seats. Jet fuel combustion scenario factor: 3.16 kg CO₂ / kg fuel. Not a carrier or aircraft-specific inventory.</div>`)+
 panel('02 / MODEL OUTPUTS','Passenger intensity and fuel',`<div id="suKpis"></div><div id="suChart"></div><div class="adv-detail" id="suInfo"></div><button class="button button-outline" id="suExport">↧ Export scenario JSON</button>`)+
 `</div>`+panel('03 / METHODS','What would improve emissions validity?',
 `<div class="al3grid3"><div><strong>Aircraft-specific performance</strong><p>Fuel flow versus payload, altitude, taxi, wind and flight phase.</p></div><div><strong>Actual trajectories</strong><p>Flown distance, ground delays, holdings and operational fuel burn.</p></div><div><strong>Environmental accounting</strong><p>Scope selection, sustainable aviation fuel eligibility and non-CO₂ impact treatment.</p></div></div>`);
 for(const id of ['suRoute','suFuel','suLoad','suFlights'])$(id).addEventListener('input',renderSustain);
 $('suExport').addEventListener('click',()=>download('aerolens_emissions_scenario.json',JSON.stringify(lastSustain,null,2),'application/json'));
 renderSustain();
}
let lastSustain;
function renderSustain(){
 const r=routeList.find(x=>x.code===$('suRoute').value),fuel=+$('suFuel').value,lf=+$('suLoad').value/100,n=+$('suFlights').value;
 $('suFuelText').textContent=fmt(fuel)+' kg/h';$('suLoadText').textContent=fmt(100*lf)+'%';$('suFlightsText').textContent=n;
 const dist=r.assumed_distance_km,block=r.assumed_block_hours_per_flight,seats=r.seats_per_flight;
 const passenger=n*seats*lf,fuelT=n*block*fuel/1000,co2T=fuelT*3.16,intensity=(co2T*1000)/(passenger*dist*1.07);
 lastSustain={route:r.code,scenario_classification:'HYPOTHETICAL',great_circle_distance_km:dist,
 weekly_departures:n,assumed_block_hours_per_flight:block,assumed_seats_per_departure:seats,
 assumed_load_factor:lf,assumed_fuel_burn_kg_per_hour:fuel,assumed_co2_factor:3.16,
 model_fuel_t:Math.round(fuelT*100)/100,model_co2_t:Math.round(co2T*100)/100,
 model_kg_co2_per_passenger_km:Math.round(intensity*1000)/1000};
 $('suKpis').innerHTML=kpis([['Modelled CO₂',fmt(co2T,1)+' t','Combustion-only scenario'],
 ['Modelled fuel',fmt(fuelT,1)+' t','Fuel/h × block hours × flights'],
 ['Passenger CO₂ intensity',fmt(intensity,3)+' kg/pax-km','Scenario, not certified inventory'],
 ['Great-circle geometry',fmt(dist)+' km','Not flown track distance']]);
 const scales=[['Fuel tonnes',fuelT],['Combustion CO₂ tonnes',co2T]],largest=Math.max(...scales.map(x=>x[1]));
 $('suChart').innerHTML=`<div class="al3bars">${scales.map(([label,v])=>`<div class="al3bar al3twobar"><div><b>${label}</b></div><div class="al3track"><span style="width:${100*v/largest}%"></span></div><strong>${fmt(v,1)} t</strong></div>`).join('')}</div>`;
 $('suInfo').textContent=`Assumed ${fmt(passenger)} passengers over ${n} departures. Assumed block time ${block} h/flight. Detour factor 1.07. No actual flight or aircraft measurements.`;
}

function assuranceSetup(){
 $('page-assurance').innerHTML=headline('ENGINEERING SYSTEMS / DOCUMENT TRACEABILITY','Evidence assurance <em>workbench.</em>',
 'A fictional record-control exercise showing how revision state, approval and deadlines affect engineering release readiness.','SYNTHETIC')+
 warning('<strong>All 40 records are fictional.</strong> This is a technical record-control demonstration, not evidence of work on any real aircraft, employer or customer. Readiness does not equal regulator approval.')+
 panel('01 / RELEASE QUALITY','Documentation health overview',`<div id="asKPIs"></div><div class="al3filter"><label class="field-label" for="asFilter">FILTER REGISTER</label><select id="asFilter" class="big-select"><option value="all">All records</option><option value="blocked">Blocked</option><option value="ready">Ready</option><option value="critical">High/critical blocked</option></select><button class="button button-outline" id="asExport">↧ Export action queue</button></div><div id="asTable"></div>`)+
 panel('02 / ENGINEERING RELEASE GATES','The control logic',
 `<div class="al3grid3"><div><strong>Revision consistency</strong><p>Current revision must equal approved revision.</p></div><div><strong>Explicit approval</strong><p>No release readiness without an approval state.</p></div><div><strong>Escalation</strong><p>Overdue blocked evidence and critical blockers are marked for action.</p></div></div>`);
 $('asFilter').addEventListener('change',renderAssurance);
 $('asExport').addEventListener('click',()=>{const rows=E.assurance.filter(x=>x.status==='blocked');download('aerolens_synthetic_assurance_queue.csv',
 ['id,requirement,criticality,revision,approved_revision,status,issues',...rows.map(x=>[x.id,x.requirement,x.criticality,x.revision,x.approved_revision,x.status,x.issues].join(','))].join('\r\n'),'text/csv')});
 renderAssurance();
}
function renderAssurance(){
 const all=E.assurance,ready=all.filter(x=>x.status==='ready'),blocked=all.filter(x=>x.status==='blocked'),critical=blocked.filter(x=>['high','critical'].includes(x.criticality));
 $('asKPIs').innerHTML=kpis([['Records',fmt(all.length),'Fictional evidence register'],
 ['Ready',fmt(ready.length),'Current and approved'],['Blocked',fmt(blocked.length),'Requires review'],
 ['High / critical blocked',fmt(critical.length),'Prioritised corrective action']]);
 let rows=all;switch($('asFilter').value){case'blocked':rows=blocked;break;case'ready':rows=ready;break;case'critical':rows=critical;break;}
 $('asTable').innerHTML=tbl(['EVIDENCE ID','REQUIREMENT','PRIORITY','REVISION / APPROVED','STATUS','CONTROL ISSUES'],
 rows.map(r=>[`<strong>${esc(r.id)}</strong>`,esc(r.requirement),esc(r.criticality.toUpperCase()),`${r.revision} / ${r.approved_revision}`,
 `<span class="al3pill ${r.status==='ready'?'good':'warn'}">${r.status.toUpperCase()}</span>`,esc(r.issues||'—')]));
}

function forecastSetup(){
 $('page-forecast').innerHTML=headline('TIME SERIES / OUT-OF-SAMPLE VERIFICATION','Aviation demand <em>forecast lab.</em>',
 'Import authentic monthly passenger data to compare seasonal baselines with rolling holdout errors, then produce a transparent six-month projection.','INPUT REQUIRED')+
 warning('<strong>No seasonality is inferred from the bundled annual CAA data.</strong> A genuine, continuous monthly series with at least 30 points is required. The optional built-in demo is wholly synthetic, clearly marked and unsuitable for real market decisions.')+
 `<div class="adv-grid-left">`+
 panel('01 / VERIFIED TIME SERIES INPUT','Load a monthly series',
 `<label class="field-label" for="fcFile">CSV: month,passengers</label><input id="fcFile" type="file" class="adv-upload" accept=".csv,text/csv" />
 <label class="field-label" for="fcSource">ORIGINAL DATA SOURCE / URL</label><input id="fcSource" class="searchbox" style="max-width:100%;width:100%" placeholder="Record public source and download date"/>
 <button class="button button-outline" id="fcSample">↧ Blank CSV schema</button> <button class="button button-outline" id="fcDemo">Load SYNTHETIC demonstration</button>
 <div id="fcStatus" class="adv-detail">No monthly source loaded. Forecasting is unavailable until source data are supplied.</div>`)+
 panel('02 / ROLLING BACKTEST','Model selection and error band',`<div id="fcKpis"></div><div id="fcChart"></div><div id="fcTable"></div><button id="fcExport" class="button button-outline" disabled>↧ Export forecast result</button>`)+
 `</div>`+panel('03 / FORECAST LIMITATIONS','How to interpret the model',
 `<div class="al3grid3"><div><strong>Origin of records</strong><p>CSV authenticity must be checked against its original source; the browser cannot authenticate uploads.</p></div><div><strong>Validation design</strong><p>Rolling one-step-ahead MAE prevents future leakage. Data require at least 30 consecutive months.</p></div><div><strong>Uncertainty</strong><p>Backtest residual bands are heuristics, not confidence intervals or causal demand forecasts.</p></div></div>`);
 $('fcSample').addEventListener('click',()=>download('monthly_passengers_schema.csv','month,passengers\r\n','text/csv'));
 $('fcDemo').addEventListener('click',()=>{
  const rows=[];for(let n=0;n<48;n++)rows.push([`${2022+Math.floor(n/12)}-${String(n%12+1).padStart(2,'0')}`,Math.round(12000+125*n+2400*Math.sin(2*Math.PI*n/12))]);
  forecastRun(rows,'SYNTHETIC / IN-APP DEMONSTRATION',true);
 });
 $('fcFile').addEventListener('change',async e=>{
  const file=e.target.files?.[0];if(!file)return;
  try{const raw=(await file.text()).replace(/^\ufeff/,'').trim();const lines=raw.split(/\r?\n/);
    if(lines[0].trim()!=='month,passengers')throw Error('Use exact header: month,passengers');
    const rows=lines.slice(1).filter(Boolean).map((line,i)=>{const [month,pax,...extra]=line.split(',');if(extra.length)throw Error('Unexpected extra columns on line '+(i+2));return [month?.trim(),Number(pax)];});
    if(!($('fcSource').value.trim()))throw Error('Enter original source URL / provenance before loading data');
    forecastRun(rows,$('fcSource').value.trim(),false);
  }catch(error){$('fcStatus').textContent='Import rejected: '+error.message;}
 });
 $('fcExport').addEventListener('click',()=>lastForecast&&download('aerolens_forecast_results.json',JSON.stringify(lastForecast,null,2),'application/json'));
}
function forecastRun(rows,source,synthetic){
 try{
  if(rows.length<30)throw Error('At least 30 observed months required');
  for(let i=0;i<rows.length;i++){
   const [m,p]=rows[i];if(!/^\d{4}-(0[1-9]|1[0-2])$/.test(m)||!Number.isSafeInteger(p)||p<0)throw Error('Invalid month or passengers at row '+(i+2));
   if(i){const prev=rows[i-1][0],z=12*(+m.slice(0,4))+(+m.slice(5)),q=12*(+prev.slice(0,4))+(+prev.slice(5));if(z-q!==1)throw Error('Months must be unique, consecutive, and in order');}
  }
  const errors={seasonal_naive:[],seasonal_level:[]};
  const v=rows.map(x=>x[1]);
  for(let t=24;t<v.length;t++){
    const baseline=v[t-12],trend=Math.max(0,baseline+(v.slice(t-12,t).reduce((a,b)=>a+b,0)-v.slice(t-24,t-12).reduce((a,b)=>a+b,0))/12);
    errors.seasonal_naive.push(Math.abs(v[t]-baseline));errors.seasonal_level.push(Math.abs(v[t]-trend));
  }
  const mae=Object.fromEntries(Object.entries(errors).map(([key,e])=>[key,e.reduce((a,b)=>a+b,0)/e.length]));
  const method=mae.seasonal_naive<=mae.seasonal_level?'seasonal_naive':'seasonal_level';
  const sorted=errors[method].slice().sort((a,b)=>a-b),band=sorted[Math.floor(.9*(sorted.length-1))];
  const drift=(v.slice(-12).reduce((a,b)=>a+b,0)-v.slice(-24,-12).reduce((a,b)=>a+b,0))/12;
  const last=rows.at(-1)[0],z=12*(+last.slice(0,4))+(+last.slice(5))-1;
  const forecast=Array.from({length:6},(_,i)=>{const value=Math.max(0,v[v.length-12+i]+(method==='seasonal_level'?drift:0));const n=z+i+1;
    return {month:`${Math.floor(n/12)}-${String(n%12+1).padStart(2,'0')}`,estimate:Math.round(value),low:Math.max(0,Math.round(value-band)),high:Math.round(value+band)};});
  lastForecast={data_classification:synthetic?'SYNTHETIC_DEMONSTRATION':'USER_SUPPLIED_SOURCE_UNVERIFIED',source,observations:rows.length,chosen_method:method,mae,
    backtest_months:errors[method].length,absolute_error_p90:Math.round(band),forecast,
    disclaimer:'Heuristic residual band, not a statistical confidence interval. Not an operational forecast.'};
  $('fcStatus').textContent=(synthetic?'SYNTHETIC DEMONSTRATION':'USER-SUPPLIED FILE')+` · ${rows.length} monthly records · ${source}`;
  $('fcKpis').innerHTML=kpis([['Selected baseline',method.replace('_',' '),'Lowest rolling one-step MAE'],
    ['Holdout months',fmt(errors[method].length),'Evaluated without future leakage'],
    ['Backtest MAE',fmt(mae[method],1)+' pax','Absolute error, not %'],
    ['90th % absolute residual',fmt(band)+' pax','Heuristic ± band around scenario estimates']]);
  const chartRows=[...rows.slice(-18).map(([month,p])=>({month,passengers:p,kind:'history'})),...forecast.map(p=>({month:p.month,passengers:p.estimate,kind:'forecast'}))];
  const max=Math.max(...chartRows.map(r=>r.passengers));
  $('fcChart').innerHTML=`<div class="al3forecast">${chartRows.map(r=>`<div class="al3forecastcol" title="${r.month}: ${fmt(r.passengers)} (${r.kind})"><span class="al3forecastbar ${r.kind}" style="height:${100*r.passengers/max}%"></span><small>${r.month.slice(5)}</small></div>`).join('')}</div><p class="adv-caveat">18 prior months in teal, six hypothetical forecast months in amber. Scenario source: ${esc(source)}.</p>`;
  $('fcTable').innerHTML=tbl(['FORECAST MONTH','POINT ESTIMATE','LOWER HEURISTIC BAND','UPPER HEURISTIC BAND'],forecast.map(x=>[x.month,fmt(x.estimate),fmt(x.low),fmt(x.high)]));
  $('fcExport').disabled=false;
 }catch(err){$('fcStatus').textContent='Forecast rejected: '+err.message;$('fcExport').disabled=true;lastForecast=null;}
}

navSetup();fleetSetup();sustainSetup();assuranceSetup();forecastSetup();
window.AEROLENS_V3_TEST={solvePortfolio,routeOutcome,forecastRun,renderFleet};
})();
