#!/usr/bin/env python3
"""Offline structural validator for PBIP, PBIR and TMDL; NOT a Desktop runtime test."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
TOP=ROOT/'powerbi/AeroLensIntelligence'
NAME='AeroLensIntelligence'

def run():
    project=json.loads((TOP/(NAME+'.pbip')).read_text())
    assert project['artifacts'][0]['report']['path']==NAME+'.Report'
    model=TOP/(NAME+'.SemanticModel')
    report=TOP/(NAME+'.Report')
    assert json.loads((model/'definition.pbism').read_text())['version']=='4.2'
    ref=json.loads((report/'definition.pbir').read_text())['datasetReference']['byPath']['path']
    assert (report/ref).resolve()==model.resolve()
    model_def=(model/'definition/model.tmdl').read_text()
    tables=list((model/'definition/tables').glob('*.tmdl'))
    assert len(tables)==6
    tablefields={}
    for path in tables:
        src=path.read_text()
        assert re.search(r'^table '+path.stem+r'$',src,re.M)
        assert 'mode: import' in src and 'source =' in src and '#table(' in src
        assert 'in\n' in src and '    Source' in src
        assert f'ref table {path.stem}' in model_def
        cols=set(re.findall(r'^\tcolumn (.+?)$',src,re.M));mea=set(re.findall(r'^\tmeasure (.+?) = ',src,re.M))
        tablefields[path.stem]=(cols,{m.strip("'") for m in mea})
    assert sum(len(m) for c,m in tablefields.values())==26
    pages=report/'definition/pages'
    meta=json.loads((pages/'pages.json').read_text())
    assert len(meta['pageOrder'])==6
    assert meta['activePageName'] in meta['pageOrder']
    visnum=0
    for page in meta['pageOrder']:
        page_dir=pages/page;pd=json.loads((page_dir/'page.json').read_text());assert pd['name']==page
        visuals=list((page_dir/'visuals').glob('*/visual.json'));assert len(visuals)==4
        for file in visuals:
            data=json.loads(file.read_text());assert data['name']==file.parent.name
            assert data['visual']['visualType'] in ('card','clusteredBarChart','lineChart','tableEx')
            for role in data['visual']['query']['queryState'].values():
                for proj in role['projections']:
                    k=proj['field'];key='Measure' if 'Measure' in k else 'Column'
                    entity=k[key]['Expression']['SourceRef']['Entity'];field=k[key]['Property']
                    assert entity in tablefields,(entity,file)
                    assert field in tablefields[entity][1 if key=='Measure' else 0],(entity,field,file)
                    visnum+=1
    print(f'PBIP structural checks PASS: {len(tables)} tables, 26 measures, 6 pages, 24 visuals; {visnum} semantic bindings. Power BI Desktop execution not tested.')
    return True
if __name__=='__main__':run()
