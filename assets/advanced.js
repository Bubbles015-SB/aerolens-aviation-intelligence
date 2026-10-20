/* AeroLens v2 — dated UTC network search, capacity economics and optional BTS validation. */
(() => {
'use strict';
const D=window.AEROLENS_DATA, A=window.AEROLENS_ADVANCED;
if(!D||!A)throw Error('Build both Python data pipelines first.');
const $=id=>document.getElementById(id);
const nfmt=(n,d=0)=>Number(n).toLocaleString('en-GB',{maximumFractionDigits:d});
const gbp=n=>'£'+nfmt(Math.round(n));
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const min=(a,b)=>(b-a)/60000;
const parseDate=s=>new Date(s).getTime();
const numeric=(id)=>Number($(id).value);
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
const save=(name,content,format='text/plain')=>{const url=URL.createObjectURL(new Blob([content],{type:format+';charset=utf-8'}));const x=document.createElement('a');x.href=url;x.download=name;x.click();setTimeout(()=>URL.revokeObjectURL(url),2000);};
const flightRows=A.flights.map(f=>({...f,t0:parseDate(f.depart_utc),t1:parseDate(f.arrive_utc)}));
const dates=[...new Set(flightRows.map(f=>f.depart_local.slice(0,10)))];
const allAirports=Object.keys(A.airports);
const currencies=new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP',maximumFractionDigits:0});

function install(){
 const alliance=$('page-alliances'),brief=$('page-brief'),quality=$('page-quality');
 alliance.innerHTML=`
  <div class="eyebrow"><span class="eyebrow-line"></span> TIME-EXPANDED GRAPH <span class="eyebrow-sep">/</span> CONTROLLED SYNTHETIC EXPERIMENT</div>
  <div class="page-head"><div><h1>Network <em>connectivity engine.</em></h1><p class="lede">Dated itineraries, UTC-safe transfers, partner reach, risk assumptions and multi-criteria ranking.</p></div><div class="year-pill"><span>MODEL</span><strong>UTC / TIME-ZONE SAFE</strong></div></div>
  <div class="insight-alert amber-alert"><span class="alert-icon">!</span><p><strong>Fictional scheduling sandbox.</strong> All 154 legs, flight numbers, carrier assignments, minimum connections and assumed risk probabilities are fabricated. Dates are 3–9 November 2026; real airport time zones are used. No real itinerary or commercial agreement is represented.</p></div>
  <div class="adv-grid-left">
    <section class="panel adv-controls"><div class="panel-kicker">01 / SEARCH CONSTRAINTS</div><h2>Itinerary optimiser</h2><p class="panel-intro">Use a dated flight graph; transfers must occur after arrival in UTC.</p>
     <label class="field-label" for="advOrigin">ORIGIN</label><select id="advOrigin" class="big-select"><option>LHR</option><option>MAN</option></select>
     <label class="field-label" for="advDest">DESTINATION</label><select id="advDest" class="big-select">${['MIA','RDU','MSY','DTW','SEA','TPA','MCO','BOS','JFK','ATL','LAX'].map(x=>`<option>${x}</option>`).join('')}</select>
     <label class="field-label" for="advDay">SYNTHETIC DEPARTURE DATE</label><select id="advDay" class="big-select">${dates.map(day=>`<option>${day}</option>`).join('')}</select>
     <div class="slider-header"><label class="field-label" for="advBuffer">ADDITIONAL TRANSFER BUFFER</label><strong id="advBufferLabel">15 min</strong></div><input id="advBuffer" type="range" min="0" max="90" step="5" value="15" />
     <div class="slider-header"><label class="field-label" for="advStops">MAXIMUM CONNECTIONS</label><strong id="advStopsLabel">2</strong></div><input id="advStops" type="range" min="0" max="2" value="2" step="1" />
     <label class="field-label" for="advWeight">SORT OPTIONS BY</label><select id="advWeight" class="big-select"><option value="balance">Composite quality</option><option value="duration">Shortest elapsed journey</option><option value="risk">Lowest assumed failure risk</option></select>
     <div class="adv-detail">The airport transfer thresholds are <strong>fictional learning parameters</strong>, not the official MCT rules used by airlines.</div>
    </section>
    <section class="panel adv-results"><div class="panel-head"><div><div class="panel-kicker">02 / NETWORK COMPARISON</div><h2>Standalone vs partner-enabled</h2><p id="advRouteSub">UTC itineraries from representative synthetic flights</p></div><button id="advExport" class="button button-outline">↧ Export scenarios</button></div>
      <div id="advOverview" class="adv-metrics"></div><div id="advItin" class="adv-itins"></div>
    </section>
  </div>
  <section class="panel adv-explainer"><div class="panel-kicker">03 / SYNTHETIC NETWORK TOPOLOGY</div><div class="panel-head"><div><h2>Geographic route graph</h2><p>Real airport coordinates; every simulated service edge is invented</p></div><span class="fake-chip">SCHEMATIC MAP</span></div><div id="advNetworkMap" class="adv-network-map" role="img" aria-label="Schematic airport graph showing illustrative connection arcs"></div><div class="adv-map-legend"><span><i class="cyan"></i> AX-labelled synthetic edges</span><span><i class="orange"></i> Partner-labelled synthetic edges</span><span><i class="focus"></i> Selected itinerary</span></div></section>
  <section class="panel adv-explainer"><div class="panel-kicker">04 / ENGINEERING METHOD</div><h2>How the model evaluates a connection</h2>
    <div class="adv-steps"><div><strong>01. UTC-normalise</strong><p>Convert every local airport time to an IANA zone-aware UTC instant, including dates and DST.</p></div><div><strong>02. Validate transitions</strong><p>Enforce connection buffer and fictional hub thresholds, reject backward time and revisiting airports.</p></div><div><strong>03. Enumerate paths</strong><p>Search up to two transfers, compare elapsed time, transfer slack and assumed trip-completion probability.</p></div><div><strong>04. Screen trade-offs</strong><p>Identify Pareto-efficient options under duration, transfers and modelled reliability. Never claim actual airline QSI.</p></div></div>
  </section>`;
 brief.innerHTML=`
  <div class="eyebrow"><span class="eyebrow-line"></span> COMMERCIAL SENSITIVITY <span class="eyebrow-sep">/</span> INVENTED ECONOMIC INPUTS</div>
  <div class="page-head"><div><h1>Contribution & <em>risk studio.</em></h1><p class="lede">Capacity-constrained unit economics, break-even analysis and reproducible uncertainty experiments.</p></div><div class="year-pill"><span>CONCLUSION CLASS</span><strong>SCENARIO ONLY</strong></div></div>
  <div class="insight-alert amber-alert"><span class="alert-icon">!</span><p><strong>Not an airline profit forecast.</strong> Only observed CAA all-carrier passenger totals are factual. Capture rate, capacity, net fares, unit costs, uncertainties and the risk distribution are <b>invented assumptions</b>. No any specific airline financial data is used.</p></div>
  <div class="adv-grid-left"><section class="panel adv-controls"><div class="panel-kicker">01 / CONFIGURE ASSUMPTIONS</div><h2>Annual route scenario</h2>
    <label class="field-label" for="ecoMarket">OBSERVED AIRPORT-PAIR MARKET</label><select id="ecoMarket" class="big-select">${D.routes.slice().sort((a,b)=>b.y2025-a.y2025).map(r=>`<option value="${r.code}">${escape(r.city)} (${r.code})</option>`).join('')}</select>
    ${range('ecoShare','Capture of all-airline market','%',0.5,12,0.5,5)}
    ${range('ecoFlights','Modelled annual flights','',100,2000,50,650)}
    ${range('ecoSeats','Seats per flight','',150,450,10,260)}
    ${range('ecoFare','Net fare / passenger (£)','£',200,1500,25,550)}
    ${range('ecoCost','Cost / flight (£)','£',15000,175000,2500,46000)}
    <details class="adv-more"><summary>Additional uncertainty and variable-cost settings</summary>
      ${range('ecoVar','Variable cost / passenger (£)','£',0,300,10,55)}
      ${range('ecoFixed','Annual fixed cost (£m)','m',0,20,.5,1.2)}
      ${range('ecoUncertainty','Demand uncertainty (1σ)','%',0,35,1,10)}
    </details>
    <button id="ecoDownload" class="button button-outline">↧ Download scenario brief</button>
  </section>
  <section class="panel adv-results"><div class="panel-head"><div><div class="panel-kicker">02 / ECONOMIC OUTPUTS</div><h2>Capacity & contribution</h2><p>Every number recalculates as inputs change</p></div><span class="fake-chip">HYPOTHETICAL</span></div>
    <div id="ecoKpis" class="adv-metrics"></div>
    <div id="ecoQuality" class="adv-detail"></div>
    <div class="panel-kicker" style="margin-top:22px">03 / SEE THE UNCERTAINTY</div><h2>Scenario stress test</h2>
    <p class="panel-intro">2,500 deterministic pseudo-random draws. These are <strong>assumption perturbations</strong>, not statistically estimated forecast intervals.</p>
    <div id="ecoRisk" class="adv-risk"></div><div id="ecoDistribution"></div>
    <div class="panel-kicker" style="margin-top:24px">04 / ONE-VARIABLE-AT-A-TIME SENSITIVITY</div><h2>Which assumption matters most?</h2><p class="panel-intro">Each invented input is moved independently ±20% from the selected scenario, holding all others constant.</p><div id="ecoTornado" class="adv-tornado"></div>
  </section></div>
  <section class="panel adv-explainer"><div class="panel-kicker">05 / COMMERCIAL DECISION HYGIENE</div><h2>Know what would be required for a real route decision</h2><div class="adv-steps"><div><strong>Demand</strong><p>True origin-destination demand, connection mix, booking curves and seasonality.</p></div><div><strong>Airline capacity</strong><p>Operator seats, inventory, flown frequency, load factor, slot rights and aircraft rotation.</p></div><div><strong>Unit economics</strong><p>Net passenger yields, cargo, fuel, airport charges, variable crew costs and allocated overhead.</p></div><div><strong>Alliance agreement</strong><p>Actual timetables, protected connections, prorates, joint venture settlements and restrictions.</p></div></div></section>`;
 const qualityCard=document.createElement('section');qualityCard.className='panel adv-explainer';qualityCard.innerHTML=`<div class="panel-kicker">04 / ADVANCED AUDIT</div><h2>Time-zone, finance and provenance checks</h2><p class="panel-intro">Additional independent checks beyond the original observed passenger reconciliation.</p><div id="advQa" class="adv-qa"></div>`;
 quality.querySelector('.sources-panel')?.before(qualityCard);
 const capacity=document.createElement('section');capacity.id='page-capacity';capacity.className='page';capacity.setAttribute('aria-label','Carrier capacity optional import');
 capacity.innerHTML=`<div class="eyebrow"><span class="eyebrow-line"></span> OPTIONAL EVIDENCE <span class="eyebrow-sep">/</span> LOCAL FILE ONLY</div>
 <div class="page-head"><div><h1>Carrier data <em>workbench.</em></h1><p class="lede">Import a user-provided BTS T-100 segment extract to calculate seats, departures and segment load factors—never estimated from CAA passengers.</p></div><div class="year-pill"><span>INPUT STATUS</span><strong>USER-SUPPLIED</strong></div></div>
 <div class="insight-alert"><span class="alert-icon">i</span><p><strong>No carrier capacity figures are bundled.</strong> The app validates file structure and arithmetic, not whether the file is genuine. Supply an official export and record its source. Files stay in your browser; nothing is uploaded.</p></div>
 <div class="adv-grid-left"><section class="panel adv-controls"><div class="panel-kicker">01 / SOURCE-DRIVEN ENRICHMENT</div><h2>Import BTS T-100 CSV</h2><p class="panel-intro">Use the official BTS international segment export. Required fields: YEAR, MONTH, ORIGIN, DEST, UNIQUE_CARRIER (or CARRIER), PASSENGERS, SEATS, DEPARTURES_PERFORMED.</p>
 <label class="field-label" for="btsProvenance">SOURCE URL / DOWNLOAD RECORD (SELF-DECLARED)</label><input id="btsProvenance" type="text" class="searchbox" style="width:100%;max-width:100%" placeholder="e.g. BTS T-100 download date and source URL"/>
 <label class="field-label" for="btsFile">SOURCE CSV FILE</label><input type="file" id="btsFile" accept=".csv,text/csv" class="adv-upload"/><button id="btsExample" class="button button-outline">↧ Download schema-only template</button>
 <div id="btsStatus" class="adv-detail">Awaiting user-supplied BTS CSV. Provenance is self-declared and cannot be independently authenticated here.</div>
 <div class="adv-detail">Source: <a href="https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FJE" target="_blank" rel="noopener">Bureau of Transportation Statistics, T-100 International Segment ↗</a></div>
 </section><section class="panel adv-results"><div class="panel-head"><div><div class="panel-kicker">02 / VERIFIED FILE OUTPUT</div><h2>Observed segment measures</h2><p>Calculated from uploaded records; source authenticity not independently verified</p></div><button id="btsExport" class="button button-outline" disabled>↧ Export</button></div><div id="btsOutput" class="adv-empty">No authentic BTS data loaded yet.</div></section></div>`;
 $('page-brief').after(capacity);
 const nav=document.querySelector('.navigation');
 const btn=document.createElement('button');btn.className='nav-item';btn.dataset.page='capacity';btn.innerHTML='<span class="nav-glyph">▥</span> Carrier evidence lab <span class="nav-n">05</span>';nav.appendChild(btn);
 $('mobilePageSelect').insertAdjacentHTML('beforeend','<option value="capacity">Carrier evidence lab</option>');
 const activate=()=>{document.querySelectorAll('.page').forEach(x=>x.classList.toggle('active',x===capacity));document.querySelectorAll('.nav-item').forEach(x=>x.classList.toggle('active',x===btn));$('crumb').textContent='CARRIER EVIDENCE LAB';$('mobilePageSelect').value='capacity';window.scrollTo(0,0);};
 btn.addEventListener('click',activate);
 $('mobilePageSelect').addEventListener('change',e=>{if(e.target.value==='capacity')activate();});
 ['advOrigin','advDest','advDay','advBuffer','advStops','advWeight'].forEach(id=>$(id).addEventListener('input',renderAlliance));
 ['ecoMarket','ecoShare','ecoFlights','ecoSeats','ecoFare','ecoCost','ecoVar','ecoFixed','ecoUncertainty'].forEach(id=>$(id).addEventListener('input',renderCommercial));
 $('ecoDownload').addEventListener('click',()=>save('aerolens_v2_synthetic_annual_scenario.md',economicsMemo(),'text/markdown'));
 $('advExport').addEventListener('click',()=>save('aerolens_v2_synthetic_itineraries.json',JSON.stringify(lastConnectivity,null,2),'application/json'));
 $('btsExample').addEventListener('click',()=>save('bts_t100_columns_example.csv','YEAR,MONTH,ORIGIN,DEST,UNIQUE_CARRIER,PASSENGERS,SEATS,DEPARTURES_PERFORMED\n','text/csv'));
 $('btsFile').addEventListener('change',loadBTS);$('btsExport').addEventListener('click',()=>{if(lastBTS)save('bts_t100_verified_aggregates.csv',makeCSV(lastBTS),'text/csv');});
 renderAlliance();renderCommercial();renderAdvancedQA();
}
function range(id,label,suffix,low,high,step,value){return `<div class="slider-header"><label class="field-label" for="${id}">${label.toUpperCase()}</label><strong id="${id}Val">${suffix==='£'?'£':''}${value}${suffix==='%'?'%':suffix==='m'?'m':''}</strong></div><input type="range" id="${id}" min="${low}" max="${high}" step="${step}" value="${value}"/>`;}
function timeLocal(f,k){const t=new Date(k==='dep'?f.depart_utc:f.arrive_utc);const airport=k==='dep'?f.origin:f.destination;return new Intl.DateTimeFormat('en-GB',{timeZone:A.airports[airport].timezone,hour:'2-digit',minute:'2-digit',day:'2-digit',month:'short',hour12:false}).format(t);}
function timeIsoDay(f){return f.depart_local.slice(0,10);}
function haversine(a,b){const p=A.airports[a],q=A.airports[b],rad=Math.PI/180,dlon=(q.longitude-p.longitude)*rad,dlat=(q.latitude-p.latitude)*rad;const z=Math.sin(dlat/2)**2+Math.cos(p.latitude*rad)*Math.cos(q.latitude*rad)*Math.sin(dlon/2)**2;return 6371*2*Math.asin(Math.min(1,Math.sqrt(z)));}
function metrics(path,buffer){
 const total=min(path[0].t0,path.at(-1).t1),transfers=[];let p=Math.pow(.94,path.length),distance=0;
 for(const l of path)distance+=haversine(l.origin,l.destination);
 for(let i=1;i<path.length;i++){const slack=min(path[i-1].t1,path[i].t0)-(A.mct[path[i-1].destination]??75)-buffer;
   transfers.push({minutes:Math.round(min(path[i-1].t1,path[i].t0)),slack:Math.round(slack)});
   p*=1/(1+Math.exp(-clamp(slack-40,-40,300)/30));}
 return {duration_minutes:Math.round(total), transfers,assumed_success_probability:p,
         distance_km:Math.round(distance),emissions_proxy_kg:Math.round(distance*.09),
         illustrative_score:clamp(Math.round(110-total/20-12*(path.length-1)-30*(1-p)),0,100)};
}
function enumerate(origin,dest,carriers,day,buffer,maxConnections=2){
 const edges=new Map();for(const f of flightRows){if(!carriers.has(f.carrier))continue;if(!edges.has(f.origin))edges.set(f.origin,[]);edges.get(f.origin).push(f);}
 for(const arr of edges.values())arr.sort((a,b)=>a.t0-b.t0);
 const solutions=[];
 const visit=(path,seen)=>{const last=path.at(-1);
   if(last.destination===dest){solutions.push({flights:path.map(f=>({...f,t0:undefined,t1:undefined})),...metrics(path,buffer)});return;}
   if(path.length>=maxConnections+1)return;
   for(const nx of edges.get(last.destination)||[]){if(seen.has(nx.destination))continue;
     const lay=min(last.t1,nx.t0);
     if(lay < (A.mct[last.destination]??75)+buffer || lay>480)continue;
     if(min(path[0].t0,nx.t1)>2400)continue;
     visit([...path,nx],new Set([...seen,nx.destination]));}
 };
 for(const first of edges.get(origin)||[])if(timeIsoDay(first)===day)visit([first],new Set([origin,first.destination]));
 const sort=$('advWeight').value;
 solutions.sort((a,b)=>sort==='duration'?a.duration_minutes-b.duration_minutes:sort==='risk'?b.assumed_success_probability-a.assumed_success_probability:b.illustrative_score-a.illustrative_score || a.duration_minutes-b.duration_minutes);
 return solutions.slice(0,25);
}
function pareto(r){return r.filter(a=>!r.some(b=>b!==a && b.duration_minutes<=a.duration_minutes && b.flights.length<=a.flights.length &&
 b.assumed_success_probability>=a.assumed_success_probability && (b.duration_minutes<a.duration_minutes || b.flights.length<a.flights.length || b.assumed_success_probability>a.assumed_success_probability)));}
function renderGeoNetwork(origin,dest,options){
 const edges=[...new Map(flightRows.map(f=>[f.origin+'-'+f.destination+'-'+f.carrier,f])).values()];
 const pathKeys=new Set((options[0]?.flights||[]).map(f=>f.origin+'-'+f.destination+'-'+f.carrier));
 const pos=k=>{const p=A.airports[k];return [65+(p.longitude+125)/140*930,340-(p.latitude-25)/33*300];};
 const paths=edges.map(f=>{
   const [x,y]=pos(f.origin),[a,b]=pos(f.destination),mx=(x+a)/2,my=(y+b)/2-Math.min(65,Math.abs(a-x)*.13);
   const focus=pathKeys.has(f.origin+'-'+f.destination+'-'+f.carrier),col=focus?'#f3b76e':f.carrier==='AX'?'#1da8b0':'#718ea4';
   return `<path d="M${x.toFixed(1)} ${y.toFixed(1)} Q${mx.toFixed(1)} ${my.toFixed(1)} ${a.toFixed(1)} ${b.toFixed(1)}" fill="none" stroke="${col}" stroke-width="${focus?3:1.3}" stroke-opacity="${focus?1:.42}" stroke-dasharray="${f.carrier==='AX'?'':'5 3'}"/>`;
 }).join('');
 const points=Object.entries(A.airports).map(([code])=>{
   const [x,y]=pos(code),selected=code===origin||code===dest;
   return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${selected?8:5}" fill="${selected?'#e2a35a':'#0c7683'}" stroke="white" stroke-width="2"/><text x="${x.toFixed(1)}" y="${(y-13).toFixed(1)}" fill="#39556b" font-size="12" font-weight="${selected?800:650}" text-anchor="middle">${code}</text>`;
 }).join('');
 $('advNetworkMap').innerHTML=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 370" role="img" aria-label="Geographic airport graph; all edges synthetic"><rect width="1080" height="370" fill="#f6fafb" rx="12"/><g stroke="#dbe9ec" stroke-width="1" opacity=".7"><path d="M0 75 H1080 M0 150 H1080 M0 225 H1080 M0 300 H1080 M180 0 V370 M360 0 V370 M540 0 V370 M720 0 V370 M900 0 V370"/></g><text x="125" y="33" fill="#a2b4bf" font-size="13" letter-spacing="3">NORTH AMERICA</text><text x="870" y="33" fill="#a2b4bf" font-size="13" letter-spacing="3">EUROPE</text>${paths}${points}</svg>`;
}
let lastConnectivity=null;
function renderAlliance(){
 const origin=$('advOrigin').value,dest=$('advDest').value,day=$('advDay').value,buffer=numeric('advBuffer'),stops=numeric('advStops');
 $('advBufferLabel').textContent=buffer+' min';$('advStopsLabel').textContent=String(stops);
 const vs=enumerate(origin,dest,new Set(['AX']),day,buffer,stops);
 const allied=enumerate(origin,dest,new Set(['AX','BX','DX','CX']),day,buffer,stops);
 const frontier=pareto(allied);
 lastConnectivity={model:'Entirely fictional alliance illustration, not real schedules',origin,destination:dest,day,buffer_minutes:buffer,maximum_connections:stops,standalone:vs,partner_enabled:allied,pareto:frontier};
 const kpi=(label,value,note)=>`<div class="adv-kpi"><small>${escape(label)}</small><strong>${escape(value)}</strong><em>${escape(note)}</em></div>`;
 $('advOverview').innerHTML=kpi('Standalone paths',String(vs.length),'AX-labelled only')+kpi('Partner paths',String(allied.length),'AX / BX / DX / CX labels')+kpi('Trade-off frontier',String(frontier.length),'Within searched options');
 $('advRouteSub').textContent=`${origin} → ${dest} | ${day} | additional transfer buffer ${buffer} min`;
 const section=(title,rows)=>`<section class="adv-itin-group"><h3>${title}<span>${rows.length} options</span></h3>${rows.length?rows.slice(0,4).map((row,i)=>{
 const ids=row.flights.map((f,j)=>j===0?f.origin+' → '+f.destination:f.destination).join(' → ');
 const parts=row.flights.map(f=>`<span class="adv-leg"><b>${escape(f.carrier)}</b> ${escape(timeLocal(f,'dep'))} → ${escape(timeLocal(f,'arr'))}</span>`).join('');
 return `<div class="adv-itinerary"><div class="adv-itin-top"><strong>${escape(ids)}</strong><span class="adv-score">${row.illustrative_score}/100</span></div><div class="adv-legs">${parts}</div><div class="adv-itin-small">${Math.floor(row.duration_minutes/60)}h ${row.duration_minutes%60}m elapsed · ${row.flights.length-1} transfer(s) · assumed trip-completion ${(row.assumed_success_probability*100).toFixed(0)}% · distance proxy ${nfmt(row.distance_km)} km</div>${row.transfers.length?`<div class="adv-itin-small">Connection time(s): ${row.transfers.map(t=>t.minutes+'min (slack '+t.slack+'min)').join(' · ')}</div>`:''}</div>`;
 }).join(''):'<div class="adv-empty">No valid itineraries in this fictional test network for the selected constraints.</div>'}</section>`;
 $('advItin').innerHTML=section('Standalone flight-label network',vs)+section('Illustrative expanded partner network',allied)+`<p class="adv-caveat">Ranking and success probabilities are solely pedagogical. Neither airline-approved minimum connections nor reliability distributions are observed.</p>`;
 renderGeoNetwork(origin,dest,allied); 
}
const gaussian=rand=>{const u=Math.max(1e-12,rand()),v=rand();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);};
function randomSource(seed){let s=seed>>>0;return ()=>{s=(1664525*s+1013904223)>>>0;return s/4294967296;};}
function commercial(){
 const route=D.routes.find(r=>r.code===$('ecoMarket').value);
 const x={market:route.y2025,share:numeric('ecoShare')/100,flights:numeric('ecoFlights'),seats:numeric('ecoSeats'),fare:numeric('ecoFare'),flightCost:numeric('ecoCost'),variable:numeric('ecoVar'),fixed:numeric('ecoFixed')*1e6,uncertainty:numeric('ecoUncertainty')/100};
 return {route,x};
}
function oneEconomics(x){
 const available=x.flights*x.seats,demand=x.market*x.share,carried=Math.min(available,Math.max(0,demand));
 const sales=carried*x.fare,cost=x.flights*x.flightCost+carried*x.variable+x.fixed;
 const breakeven=x.fare>x.variable ? (x.flights*x.flightCost+x.fixed)/(x.fare-x.variable) : Infinity;
 return {available,demand,carried,spill:Math.max(0,demand-available),sales,cost,contribution:sales-cost,loadFactor:carried/available,breakeven,breakevenLF:breakeven/available};
}
function monteCarlo(x,draws=2500){
 const rand=randomSource(20261019);const samples=[];let wins=0;
 for(let i=0;i<draws;i++){
   const z={...x,market:Math.max(0,x.market*(1+gaussian(rand)*x.uncertainty)),
     share:clamp(x.share*(1+gaussian(rand)*.25),0,1),fare:Math.max(1,x.fare*(1+gaussian(rand)*.12)),
     flightCost:Math.max(0,x.flightCost*(1+gaussian(rand)*.10))};
   const m=oneEconomics(z);samples.push(m.contribution);if(m.contribution>0)wins++;
 }
 const sorted=[...samples].sort((a,b)=>a-b),quant=q=>{const p=q*(sorted.length-1),j=Math.floor(p);return sorted[j]+(sorted[Math.min(j+1,sorted.length-1)]-sorted[j])*(p-j);};
 return {samples,p05:quant(.05),p50:quant(.5),p95:quant(.95),positive:wins/draws,draws,seed:20261019};
}
let lastEconomy=null;
function renderCommercial(){
 const {route,x}=commercial(),e=oneEconomics(x),m=monteCarlo(x);
 lastEconomy={route_code:route.code,observed_caa_market_2025:route.y2025,synthetic_inputs:x,synthetic_result:e,synthetic_stress:{draws:m.draws,seed:m.seed,p05:m.p05,p50:m.p50,p95:m.p95,positive_probability:m.positive}};
 for(const [id,suffix] of [['ecoShare','%'],['ecoFlights',''],['ecoSeats',''],['ecoFare','£'],['ecoCost','£'],['ecoVar','£'],['ecoFixed','m'],['ecoUncertainty','%']]){
  let v=numeric(id);$(''+id+'Val').textContent=suffix==='£'?'£'+nfmt(v):suffix==='m'?v.toFixed(1)+'m':suffix==='%'?v.toFixed(id==='ecoShare'?1:0)+'%':nfmt(v);
 }
 const metric=(title,value,foot,neg=false)=>`<div class="adv-kpi"><small>${escape(title)}</small><strong class="${neg?'negative':''}">${escape(value)}</strong><em>${escape(foot)}</em></div>`;
 $('ecoKpis').innerHTML=metric('Available annual seats',nfmt(e.available),'Hypothetical service plan')+
 metric('Potentially carried',nfmt(Math.round(e.carried)),'Market capture capped by seats')+
 metric('Implied load factor', (e.loadFactor*100).toFixed(1)+'%','MODELLED, not observed')+
 metric('Indicative contribution',gbp(e.contribution),'Assumed fares less assumed costs',e.contribution<0)+
 metric('Model break-even LF',isFinite(e.breakevenLF)?(e.breakevenLF*100).toFixed(1)+'%':'Not attainable','Within model assumptions',e.breakevenLF>1)+
 metric('Unserved assumed demand',nfmt(Math.round(e.spill)),'Capacity constraint');
 $('ecoQuality').innerHTML=`<strong>Capacity logic:</strong> Requested ${nfmt(Math.round(e.demand))} annual passenger movements are capped at ${nfmt(e.available)} seats.<br><strong>Break-even:</strong> ${e.breakevenLF<=1?'The chosen invented parameters admit a mathematical break-even.':'The chosen invented parameters imply break-even above 100% load factor, so this service plan does not break even.'}`;
 $('ecoRisk').innerHTML=metric('Illustrative probability of positive contribution',(m.positive*100).toFixed(1)+'%','Across 2,500 invented-input draws')+
 metric('5th percentile',gbp(m.p05),'Not a confidence interval')+metric('Median',gbp(m.p50),'Not an earnings forecast')+metric('95th percentile',gbp(m.p95),'Assumption-sensitive');
 const lo=Math.min(...m.samples,-1),hi=Math.max(...m.samples,1);let bars=Array(20).fill(0);for(const s of m.samples){let index=Math.floor((s-lo)/(hi-lo)*20);bars[clamp(index,0,19)]++;}
 const top=Math.max(...bars,1),zero=clamp((-lo)/(hi-lo),0,1)*100;
 $('ecoDistribution').innerHTML=`<div class="adv-histogram" aria-label="Distribution of invented-input scenario contributions">${bars.map((n,i)=>`<i style="height:${Math.max(2,n/top*100)}%" title="${n} simulation draws"></i>`).join('')}<span class="zero-line" style="left:${zero}%"></span></div><div class="adv-hist-label"><span>${gbp(lo)}</span><span>0 contribution shown by vertical line</span><span>${gbp(hi)}</span></div>`;
 const sensitivities=[['Demand', 'market'],['Capture rate','share'],['Net fare','fare'],['Cost per flight','flightCost'],['Available seats','seats']].map(([name,key])=>{
   const low=oneEconomics({...x,[key]:x[key]*.8}).contribution;
   const high=oneEconomics({...x,[key]:x[key]*1.2}).contribution;
   return {name,low,high,magnitude:Math.abs(high-low)};
 }).sort((a,b)=>b.magnitude-a.magnitude);
 const maxMagnitude=Math.max(...sensitivities.map(a=>Math.abs(a.low-e.contribution)),...sensitivities.map(a=>Math.abs(a.high-e.contribution)),1);
 $('ecoTornado').innerHTML=sensitivities.map(row=>{const left=(row.low-e.contribution)/maxMagnitude*46,right=(row.high-e.contribution)/maxMagnitude*46;
 return `<div class="adv-tornado-row"><span>${escape(row.name)}</span><div class="adv-tornado-scale"><i class="adv-tornado-axis"></i><i class="adv-tornado-bar negative-bar" style="left:${Math.min(50+left,50+right)}%;width:${Math.abs(right-left)}%"></i></div><span>${gbp(row.magnitude)} swing</span></div>`;
 }).join('')+`<div class="adv-caveat">Bars show a single parameter shifted ±20% around current model inputs, ranked by absolute contribution swing. Direction and magnitude are scenario-dependent.</div>`;

}
function economicsMemo(){const obj=lastEconomy;return `# AeroLens independent hypothetical commercial scenario\n\nSOURCE: CAA Table 12.1 2025 annual, selected two-way all-airline airport market.\nMARKET: LHR–${obj.route_code}\nObserved 2025 market passengers: ${obj.observed_caa_market_2025}\n\nALL OTHER INPUTS AND MODEL OUTPUTS ARE FICTIONAL. NOT AIRLINE FINANCIAL STATEMENTS OR A FORECAST.\n\n## Invented model inputs\n\n${JSON.stringify(obj.synthetic_inputs,null,2)}\n\n## Calculated model outputs\n\n${JSON.stringify(obj.synthetic_result,null,2)}\n\n## Reproducible hypothetical uncertainty perturbations\n\n${JSON.stringify(obj.synthetic_stress,null,2)}\n\nModel: Gaussian sigma assumptions 10% market (or slider), 25% capture, 12% fare, 10% flight costs. Seed=20261019. No empirical fitting.\n\nQuestions for a genuine commercial decision: validated O&D demand, airline flown seats, booking curves, net yields, fuel and operating costs, slot and fleet feasibility, competitor schedules, actual interline settlement.\n`;}
function renderAdvancedQA(){
 const utcOkay=flightRows.every(f=>Number.isFinite(f.t0)&&Number.isFinite(f.t1)&&f.t1>f.t0&&min(f.t0,f.t1)>40);
 const provenance=A.provenance.caa_csv_sha256.length===64;
 const dateCorrect=flightRows.some(f=>f.origin==='LHR'&&f.destination==='JFK'&&f.depart_local.slice(0,10)==='2026-11-03'&&min(f.t0,f.t1)>400);
 const consistent=flightRows.every(f=>f.schedule_status==='synthetic');
 const example=oneEconomics({market:1e6,share:.04,flights:100,seats:200,fare:500,flightCost:20000,variable:50,fixed:0});
 const seatCap=example.carried===20000 && example.loadFactor===1;
 const checks=[['Dated departure / arrival UTC monotonic',utcOkay,flightRows.length+' dated legs'],['Full SHA-256 provenance recorded',provenance,'CAA curated source fingerprint'],
 ['Time-zone-aware transatlantic duration',dateCorrect,'November UK / US offsets applied'],['Every itinerary leg explicitly labelled synthetic',consistent,'No carrier-timetable claims'],['Passenger demand capped by offered seats',seatCap,'No load factors above 100% in capacity model']];
 $('advQa').innerHTML=checks.map(([title,ok,info])=>`<div class="adv-qa-row"><span class="${ok?'ok':'bad'}">${ok?'✓':'!'}</span><div><strong>${escape(title)}</strong><small>${escape(info)}</small></div></div>`).join('');
}
let lastBTS=null;
function parseCSV(s){const out=[];let row=[],part='',q=false;for(let i=0;i<s.length;i++){const c=s[i];if(c==='"'){if(q&&s[i+1]==='"'){part+='"';i++;}else q=!q;}else if(c===','&&!q){row.push(part);part='';}else if((c==='\n'||c==='\r')&&!q){if(c==='\r'&&s[i+1]==='\n')i++;row.push(part);if(row.some(v=>v!==''))out.push(row);row=[];part='';}else part+=c;}if(q)throw Error('Malformed CSV: unterminated quoted field');if(part||row.length){row.push(part);out.push(row);}return out;}
function makeCSV(rows){if(!rows.length)return '';const cols=Object.keys(rows[0]);return [cols.join(','),...rows.map(r=>cols.map(k=>'"'+String(r[k]??'').replaceAll('"','""')+'"').join(','))].join('\r\n')+'\r\n';}
async function loadBTS(evt){
 const file=evt.target.files?.[0];if(!file)return;
 if(file.size>30e6){$('btsStatus').textContent='Limit: 30 MB per browser import. Use the Python BTS adapter for larger official extracts.';return;}
 try{
  const provenance=$('btsProvenance').value.trim();if(provenance.length<12)throw Error('Provide a meaningful source URL or download record before importing.');
  const rows=parseCSV(await file.text()),cols=rows.shift().map(x=>x.replace(/^\uFEFF/,'').trim().toUpperCase()),idx=k=>cols.indexOf(k);
  const carrier=['UNIQUE_CARRIER','OP_UNIQUE_CARRIER','CARRIER'].find(x=>idx(x)>=0);
  const required=['ORIGIN','DEST','PASSENGERS','SEATS','DEPARTURES_PERFORMED','YEAR','MONTH'];
  if(required.some(x=>idx(x)<0)||!carrier)throw Error('Missing one or more required BTS T-100 column names.');
  const group=new Map();let imported=0;
  rows.forEach((r,i)=>{if(!r.length)return;const a=(r[idx('ORIGIN')]||'').trim().toUpperCase(),b=(r[idx('DEST')]||'').trim().toUpperCase();if(a!=='LHR'&&b!=='LHR')return;
   const integer=k=>{const n=Number((r[idx(k)]||'').replaceAll(',',''));if(!Number.isSafeInteger(n)||n<0)throw Error(`Row ${i+2}: invalid ${k}`);return n;};
   const pax=integer('PASSENGERS'),seats=integer('SEATS'),dep=integer('DEPARTURES_PERFORMED'),yr=integer('YEAR'),mo=integer('MONTH');
   if(!Number.isInteger(mo)||mo<1||mo>12||yr<1990||yr>2100||pax>seats||(!dep&&(pax||seats)))throw Error(`Row ${i+2}: inconsistent period, capacity or departures`);
   const code=(r[idx(carrier)]||'').trim();if(!code)throw Error(`Row ${i+2}: carrier missing`);
   const pair=[a,b].sort();const key=[yr,mo,code,...pair].join('|');const prev=group.get(key)||{year:yr,month:mo,carrier:code,airport_a:pair[0],airport_b:pair[1],passengers:0,seats:0,departures:0};
   prev.passengers+=pax;prev.seats+=seats;prev.departures+=dep;group.set(key,prev);imported++;
  });
  if(!imported)throw Error('No records with origin or destination LHR found.');
  const out=[...group.values()].sort((a,b)=>a.year-b.year||a.month-b.month||a.carrier.localeCompare(b.carrier));out.forEach(r=>r.seat_load_factor=r.seats?(r.passengers/r.seats).toFixed(4):'N/A');lastBTS=out;
  $('btsStatus').textContent=`Parsed ${nfmt(imported)} structurally valid user-supplied records into ${nfmt(out.length)} carrier/period groups. Source self-declared; independently verify the extract before quoting results.`;
  const passengers=out.reduce((s,r)=>s+r.passengers,0),seats=out.reduce((s,r)=>s+r.seats,0),flights=out.reduce((s,r)=>s+r.departures,0);
  $('btsOutput').innerHTML=`<p class="adv-caveat">Uploaded source declaration (not verified): ${escape(provenance)}. Results below are conditional on file authenticity.</p><div class="adv-metrics">${[['Passengers',nfmt(passengers)],['Offered seats',nfmt(seats)],['Observed segment LF',seats?(100*passengers/seats).toFixed(1)+'%':'N/A']].map(([a,b])=>`<div class="adv-kpi"><small>${a}</small><strong>${b}</strong></div>`).join('')}</div><p class="adv-caveat">T-100 segment figures do not measure full connecting O&D flows or profits. ${nfmt(flights)} performed departures in imported filtered scope.</p><div class="adv-table-scroll"><table><thead><tr><th>YEAR-MONTH</th><th>CARRIER</th><th>MARKET</th><th>PASSENGERS</th><th>SEATS</th><th>LOAD FACTOR</th></tr></thead><tbody>${out.slice(0,80).map(r=>`<tr><td>${r.year}-${String(r.month).padStart(2,'0')}</td><td>${escape(r.carrier)}</td><td>${escape(r.airport_a)}–${escape(r.airport_b)}</td><td>${nfmt(r.passengers)}</td><td>${nfmt(r.seats)}</td><td>${r.seat_load_factor==='N/A'?'N/A':(r.seat_load_factor*100).toFixed(1)+'%'}</td></tr>`).join('')}</tbody></table></div>`;
  $('btsExport').disabled=false;
 }catch(err){lastBTS=null;$('btsStatus').textContent='Import rejected: '+err.message;$('btsOutput').textContent='No usable carrier-level source data loaded.';$('btsExport').disabled=true;}
}
install();
window.AEROLENS_V2_TEST={enumerate,pareto,oneEconomics,parseCSV,metrics,renderAdvancedQA};
})();
