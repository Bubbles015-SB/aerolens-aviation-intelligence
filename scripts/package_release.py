#!/usr/bin/env python3
"""Build distributable offline single HTML and two reproducible source archives."""
from pathlib import Path
import base64,hashlib,json,zipfile,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent
SINGLE=OUT/'AeroLens_3_Standalone_Dashboard.html'
BUNDLE=OUT/'AeroLens_3_Complete_Repository.zip'
BI=OUT/'AeroLens_3_Editable_PowerBI_PBIP.zip'

html=(ROOT/'index.html').read_text(encoding='utf-8')
for css in ['style.css','enterprise.css']:
    path=ROOT/'assets'/css
    marker=f'<link rel="stylesheet" href="assets/{css}" />'
    assert marker in html,marker
    html=html.replace(marker,'<style>\n'+path.read_text(encoding='utf-8')+'\n</style>')
for script in ['data.js','app.js','advanced_data.js','advanced.js','enterprise_data.js','enterprise.js']:
    marker=f'<script src="assets/{script}"></script>'
    assert marker in html,marker
    js=(ROOT/'assets'/script).read_text(encoding='utf-8')
    # Browser parses script sections from HTML; no literal closing tag allowed inside JS.
    assert '</script' not in js.lower()
    html=html.replace(marker,'<script>\n'+js+'\n</script>')
icon=ROOT/'assets/favicon.svg'
html=html.replace('href="assets/favicon.svg"','href="data:image/svg+xml;base64,'+base64.b64encode(icon.read_bytes()).decode()+'"')
for file,mime in [('data/raw/caa_lhr_us_annual_2025_2024_curated.csv','text/csv'),
                  ('data/advanced/synthetic_time_aware_schedule.json','application/json'),
                  ('data/derived/route_summary.csv','text/csv')]:
    marker='href="'+file+'"'
    if marker in html:
        path=ROOT/file
        value=base64.b64encode(path.read_bytes()).decode('ascii')
        html=html.replace(marker,f'href="data:{mime};base64,{value}"')
html=html.replace('</head>','<meta name="application-name" content="AeroLens 3" /></head>',1)
SINGLE.write_text(html,encoding='utf-8')
assert '<script src="' not in html and 'assets/style.css' not in html

excluded={'.pyc','.pyo','.DS_Store'}
def include(p):
    return not any(part=='__pycache__' or part=='.pytest_cache' or part=='.git' for part in p.parts) and p.suffix not in excluded

files=sorted(p for p in ROOT.rglob('*') if p.is_file() and include(p.relative_to(ROOT)))
with zipfile.ZipFile(BUNDLE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for file in files:z.write(file,arcname='AeroLens_3_Enterprise/'+file.relative_to(ROOT).as_posix())
pbiroot=ROOT/'powerbi'
with zipfile.ZipFile(BI,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for file in sorted(pbiroot.rglob('*')):
        if file.is_file() and include(file.relative_to(pbiroot)):
            z.write(file,arcname='AeroLens_3_PowerBI/'+file.relative_to(pbiroot).as_posix())
    for file in ['docs/POWERBI_DESKTOP_CHECKLIST.md','docs/SOURCE_REGISTER.md','docs/VALIDATION_AND_LIMITS.md']:
        z.write(ROOT/file,arcname='AeroLens_3_PowerBI/'+file)
    for file in sorted((ROOT/'data/bi').glob('*.csv')):
        z.write(file,arcname='AeroLens_3_PowerBI/data/bi/'+file.name)
manifest={
 'release':'3.0.0','project':'AeroLens Aviation and Aerospace Decision Intelligence',
 'classification':'AI-assisted independent portfolio; observed CAA only, remaining operational/finance scenarios',
 'python_tests_passed':45,'powerbi_tables':6,'powerbi_dax_measures':26,'powerbi_report_pages':6,'powerbi_native_visuals':24,
 'desktop_powerbi_runtime_validation':'NOT PERFORMED; requires Windows Power BI Desktop',
 'exports':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [SINGLE,BUNDLE,BI]},
}
(OUT/'AeroLens_3_Release_Manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for p in [SINGLE,BUNDLE,BI]:print(f'{p.name}: {p.stat().st_size:,} bytes, SHA256 {manifest["exports"][p.name]["sha256"][:16]}')
