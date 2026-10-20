/* AeroLens v2 core — observed CAA route metrics, market table and evidence checks. */
(() => {
  'use strict';
  const D = window.AEROLENS_DATA;
  if (!D) throw new Error('Dataset missing. Run python scripts/build_data.py.');
  const $ = (id) => document.getElementById(id);
  const fmt = n => Number(n).toLocaleString('en-GB');
  const fmtCompact = n => new Intl.NumberFormat('en-GB',{notation:'compact',maximumFractionDigits:2}).format(n);
  const pct = (n, dp=1) => `${n > 0 ? '+' : ''}${n.toFixed(dp)}%`;
  const currency = n => '£'+Number(n).toLocaleString('en-GB',{maximumFractionDigits:0});
  const safe = value => String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
  const classification = val => val >= 0 ? 'positive' : 'negative';
  const data = D.routes;
  const state = { page:'market',region:'All',sort:'volume',count:8,tableKey:'y2025',tableDesc:true,search:'' };
  const S = D.summary;
  function init(){
    renderMetrics(); renderMarket(); renderQuality(); wireUI();
  }
  function wireUI(){
    document.querySelectorAll('.nav-item').forEach(btn=>btn.addEventListener('click',()=>showPage(btn.dataset.page)));
    $('mobilePageSelect').addEventListener('change',e=>showPage(e.target.value));
    document.querySelectorAll('.mini-tab').forEach(b=>b.addEventListener('click',()=>{
      state.sort=b.dataset.sort; document.querySelectorAll('.mini-tab').forEach(t=>t.classList.toggle('active',t===b));renderBarChart();
    }));
    $('regionFilter').addEventListener('change',e=>{state.region=e.target.value;renderBarChart();});
    $('topCount').addEventListener('change',e=>{state.count=+e.target.value;renderBarChart();});
    $('searchRoutes').addEventListener('input',e=>{state.search=e.target.value.trim().toLowerCase();renderTable();});
    document.querySelectorAll('#routeTable th[data-key]').forEach(th=>th.addEventListener('click',()=>{
      if(state.tableKey===th.dataset.key)state.tableDesc=!state.tableDesc;
      else {state.tableKey=th.dataset.key;state.tableDesc=true;}
      renderTable();
    }));
    $('exportRoutes').addEventListener('click',()=>saveFile('aerolens_filtered_markets.csv',csvForRows(filterTable()),'text/csv'));
    $('downloadSnapshot').addEventListener('click',()=>saveFile('aerolens_caa_market_data.csv',csvForRows(data),'text/csv'));
  }
  function showPage(p){
    state.page=p; $('mobilePageSelect').value=p;
    document.querySelectorAll('.page').forEach(el=>el.classList.toggle('active',el.id===`page-${p}`));
    document.querySelectorAll('.nav-item').forEach(el=>el.classList.toggle('active',el.dataset.page===p));
    $('crumb').textContent=({market:'MARKET INTELLIGENCE',alliances:'ALLIANCE LAB',quality:'DATA INTEGRITY',brief:'DECISION BRIEF'})[p];
    window.scrollTo({top:0,behavior:'smooth'});
  }
  function renderMetrics(){
    $('metricPax').textContent=fmtCompact(S.pax_2025);
    $('metricPaxSub').textContent=`vs. ${fmtCompact(S.pax_2024)} passengers in 2024`;
    $('metricChange').textContent=pct(S.growth_pct,2);
    $('metricChange').className=`stat-number ${classification(S.growth_pct)}`;
    $('metricChangeSub').textContent=`${S.delta>0?'+':''}${fmt(S.delta)} passengers (curated markets)`;
    $('metricCount').textContent=fmt(S.routes);
    $('metricGrowing').textContent=`${S.growing_routes} / ${S.routes}`;
  }
  function renderMarket(){renderBarChart();renderSignals();renderTable();}
  function selectedRows(){return data.filter(r=>state.region==='All'||r.region===state.region);}
  function renderBarChart(){
    let rows=selectedRows().slice();
    rows.sort((a,b)=>state.sort==='growth'?b.growth_pct-a.growth_pct:b.y2025-a.y2025);
    rows=rows.slice(0,state.count);
    const max=Math.max(1,...rows.map(r=>Math.max(r.y2024,r.y2025)));
    $('barChart').innerHTML=`<div class="bar-list">${rows.map(r=>{
      const w24=(r.y2024/max*100).toFixed(2),w25=(r.y2025/max*100).toFixed(2);
      return `<div class="bar-row" title="${safe(r.city)}: 2024 ${fmt(r.y2024)}, 2025 ${fmt(r.y2025)}; ${pct(r.growth_pct)}"><span class="bar-city">${safe(r.code)} · ${safe(r.city)}</span><div class="bar-track"><div class="bar-past" style="width:${w24}%"></div><div class="bar-current" style="width:${w25}%"></div></div><span class="bar-num">${state.sort==='growth'?pct(r.growth_pct):fmtCompact(r.y2025)}</span></div>`;
    }).join('')}</div>`;
  }
  function renderSignals(){
    const mostGrowth=data.filter(r=>r.y2024>=100000).slice().sort((a,b)=>b.growth_pct-a.growth_pct)[0];
    const biggestLoss=data.slice().sort((a,b)=>a.delta-b.delta)[0];
    const largest=data.slice().sort((a,b)=>b.y2025-a.y2025)[0];
    const signals=[
      ['↑','Largest proportional gain (100k+ baseline)',mostGrowth,`${pct(mostGrowth.growth_pct)} relative to 2024. Investigate what changed in the market.`, 'up',pct(mostGrowth.growth_pct)],
      ['↓','Largest absolute decline',biggestLoss,`${fmt(Math.abs(biggestLoss.delta))} fewer annual passengers; investigate capacity and demand causes.`,'down',fmtCompact(biggestLoss.delta)],
      ['◎','Largest selected market',largest,`2025 traffic across all carriers; large market is not necessarily best-margin.`,'up',fmtCompact(largest.y2025)],
    ];
    $('signals').innerHTML=signals.map(([sym,title,r,description,style,val])=>`<div class="signal"><div class="signal-symbol ${style}">${sym}</div><div><strong>${safe(title)}</strong><p><b>${safe(r.city)} (LHR–${r.code})</b><br>${safe(description)}</p></div><div class="signal-number ${classification(r.delta)}">${val}</div></div>`).join('');
  }
  function filterTable(){
    let rows=data.filter(r=>[r.city,r.code,r.region].some(x=>x.toLowerCase().includes(state.search)));
    const {tableKey:col,tableDesc:desc}=state;
    rows.sort((a,b)=>{
      const c=(typeof a[col]==='number')?a[col]-b[col]:a[col].localeCompare(b[col]);
      return desc?-c:c;
    });
    return rows;
  }
  function renderTable(){
    const rows=filterTable();
    $('routeTable').querySelector('tbody').innerHTML=rows.map(r=>`<tr><td><span class="airport-tag">${r.code}</span><strong>${safe(r.city)}</strong></td><td>${safe(r.region)}</td><td class="num">${fmt(r.y2024)}</td><td class="num">${fmt(r.y2025)}</td><td class="num ${classification(r.delta)}">${r.delta>0?'+':''}${fmt(r.delta)}</td><td class="num"><span class="delta-tag ${r.delta>=0?'plus':'minus'}">${pct(r.growth_pct)}</span></td></tr>`).join('');
    $('tableCount').textContent=`${rows.length} of ${data.length} selected markets`;
  }
  function csvForRows(rows){const keys=['code','city','region','y2024','y2025','delta','growth_pct'];return [keys.join(','),...rows.map(r=>keys.map(k=>`"${String(r[k]).replaceAll('"','""')}"`).join(','))].join('\r\n')+'\r\n';}
  function saveFile(name,content,type){
    const blob=new Blob([content],{type:`${type};charset=utf-8`});const url=URL.createObjectURL(blob);
    const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
  }
  function checkData(){
    const ids=data.map(r=>r.code);
    const steps=[
      ['28 selected records present',data.length===28,`${data.length} markets loaded`],
      ['Unique three-letter route identifiers',new Set(ids).size===ids.length&&ids.every(c=>/^[A-Z]{3}$/.test(c)),'No duplicated airport code'],
      ['Non-negative, integral passenger totals',data.every(r=>Number.isInteger(r.y2024)&&Number.isInteger(r.y2025)&&r.y2024>0&&r.y2025>0),'Both years checked'],
      ['Exact derived absolute changes',data.every(r=>r.delta===r.y2025-r.y2024),'Computed from two annual integer totals'],
      ['Exact derived percentage changes',data.every(r=>Math.abs(r.growth_pct-100*r.delta/r.y2024)<.0001),'Rounding tolerance <0.0001 percentage points'],
      ['Dataset aggregate totals reconcile',data.reduce((s,r)=>s+r.y2025,0)===S.pax_2025&&data.reduce((s,r)=>s+r.y2024,0)===S.pax_2024,'Independent browser recomputation'],
    ];
    return steps;
  }
  function renderQuality(){
    const checks=checkData();const failures=checks.filter(t=>!t[1]);
    $('validationTitle').textContent=failures.length?`${failures.length} checks need attention`:'All integrity checks passed';
    $('validationTitle').className=failures.length?'negative':'positive';
    $('validationSub').textContent=`${checks.length-failures.length} of ${checks.length} automated checks passed · official figures independently transcribed`;
    $('validationChecks').innerHTML=checks.map(([name,pass,descr])=>`<div class="check"><span class="check-icon ${pass?'':'fail'}">${pass?'✓':'!'}</span><div><strong>${safe(name)}</strong><small>${safe(descr)}</small></div></div>`).join('');
  }
  init();
  window.AEROLENS_TEST={checkData,summary:S};
})();
