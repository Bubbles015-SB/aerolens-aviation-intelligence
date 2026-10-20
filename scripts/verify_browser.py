#!/usr/bin/env python3
"""Optional real Chromium interaction tests and screenshot generation.

Works in restrictive environments by inlining local source assets into a
Playwright document. App is independently runnable as regular index.html.
Requires playwright and Chromium; excluded from Python stdlib CI.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def inline_page():
 html=(ROOT/'index.html').read_text(encoding='utf-8')
 html=html.replace('<link rel="stylesheet" href="assets/style.css" />',
                   '<style>'+ (ROOT/'assets/style.css').read_text(encoding='utf-8') +'</style>')
 for script in ['data.js','app.js','advanced_data.js','advanced.js']:
  html=html.replace(f'<script src="assets/{script}"></script>',
                    '<script>'+ (ROOT/'assets'/script).read_text(encoding='utf-8') +'</script>')
 return html

def test():
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--no-proxy-server'])
  page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content(inline_page(),wait_until='load')
  assert page.locator('#metricCount').inner_text()=='28'
  assert page.locator('#advItin').inner_text().count('LHR')>0
  page.locator('[data-page="alliances"]').click()
  assert 'No valid itineraries' in page.locator('#advItin').inner_text()
  assert 'LHR → JFK → MIA' in page.locator('#advItin').inner_text()
  page.locator('#advDest').select_option('RDU');assert 'RDU' in page.locator('#advItin').inner_text()
  page.locator('#advBuffer').fill('90')
  assert '90 min' in page.locator('#advBufferLabel').inner_text()
  page.locator('#advBuffer').fill('15');page.locator('#advDest').select_option('MIA')
  page.screenshot(path=str(ROOT/'media/advanced-network.png'),full_page=True)
  page.locator('[data-page="brief"]').click()
  assert '95.3%' in page.locator('#ecoKpis').inner_text()
  page.locator('#ecoShare').fill('12')
  assert '100.0%' in page.locator('#ecoKpis').inner_text()
  assert page.locator('#ecoDistribution .adv-histogram i').count()==20
  page.locator('#ecoShare').fill('5')
  page.screenshot(path=str(ROOT/'media/advanced-commercial.png'),full_page=True)
  page.locator('[data-page="quality"]').click()
  assert page.locator('#advQa .adv-qa-row').count()==5
  page.locator('[data-page="capacity"]').click()
  assert page.locator('#btsExport').is_disabled()
  sample='YEAR,MONTH,ORIGIN,DEST,UNIQUE_CARRIER,PASSENGERS,SEATS,DEPARTURES_PERFORMED\n2025,1,LHR,JFK,AA,80,100,1\n2025,1,JFK,LHR,AA,70,100,1\n'
  page.locator('#btsProvenance').fill('Synthetic validation fixture - NOT actual BTS data')
  page.locator('#btsFile').set_input_files({'name':'authentic_format_test.csv','mimeType':'text/csv','buffer':sample.encode()})
  assert 'Parsed 2 structurally valid user-supplied records' in page.locator('#btsStatus').inner_text()
  assert '75.0%' in page.locator('#btsOutput').inner_text()
  assert page.locator('#btsExport').is_enabled()
  page.screenshot(path=str(ROOT/'media/advanced-capacity.png'),full_page=True)
  mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
  mobile.on('pageerror',lambda e:errors.append('MOBILE: '+str(e)))
  mobile.set_content(inline_page(),wait_until='load')
  mobile.locator('#mobilePageSelect').select_option('alliances')
  assert mobile.locator('#page-alliances').get_attribute('class').find('active')>=0
  mobile.screenshot(path=str(ROOT/'media/advanced-mobile.png'),full_page=True)
  assert not errors,errors
  print('Browser tests passed: 2 viewports, 5 modules, UTC graph interactions, economics stress, authentic-shape CSV adapter.')
  browser.close()

if __name__=='__main__':test()
