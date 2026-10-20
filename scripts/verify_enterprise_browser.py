#!/usr/bin/env python3
"""Interactive Chromium smoke/regression checks for v3 pages + screenshot captures."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def inline_page():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    for css in ('style.css','enterprise.css'):
        html=html.replace(f'<link rel="stylesheet" href="assets/{css}" />','<style>'+(ROOT/'assets'/css).read_text(encoding='utf-8')+'</style>')
    for js in ('data.js','app.js','advanced_data.js','advanced.js','enterprise_data.js','enterprise.js'):
        html=html.replace(f'<script src="assets/{js}"></script>','<script>'+(ROOT/'assets'/js).read_text(encoding='utf-8')+'</script>')
    return html
media=ROOT/'media';media.mkdir(exist_ok=True)
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu','--no-proxy-server'])
    page=browser.new_page(viewport={'width':1480,'height':1020},device_scale_factor=1)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(inline_page(),wait_until='load')
    page.wait_for_timeout(800)
    assert page.locator('#page-market').is_visible(),'Market missing'
    assert page.locator('#metricPax').inner_text()!='—'
    assert page.locator('.nav-item').count()>=9
    page.locator('button[data-page="fleet"]').click()
    assert page.locator('#page-fleet').is_visible()
    assert page.locator('#fpStatus').inner_text().startswith('EXACT')
    assert '£' in page.locator('#fpKpis').inner_text()
    page.screenshot(path=str(media/'v3_fleet_portfolio.png'),full_page=True)
    before=page.locator('#fpKpis').inner_text()
    page.locator('#fpFare').fill('65');page.locator('#fpFare').dispatch_event('input')
    assert page.locator('#fpKpis').inner_text()!=before,'Model failed to respond to fare slider'
    page.locator('button[data-page="sustain"]').click()
    assert page.locator('#page-sustain').is_visible()
    assert 'CO₂' in page.locator('#suKpis').inner_text()
    page.screenshot(path=str(media/'v3_sustainability.png'),full_page=True)
    old=page.locator('#suKpis').inner_text()
    page.locator('#suFuel').fill('7000');page.locator('#suFuel').dispatch_event('input')
    assert page.locator('#suKpis').inner_text()!=old,'Fuel slider failed to update model'
    page.locator('button[data-page="assurance"]').click()
    assert page.locator('#page-assurance').is_visible()
    assert 'blocked' in page.locator('#asKPIs').inner_text().lower(), page.locator('#asKPIs').inner_text()
    page.locator('#asFilter').select_option('critical')
    assert page.locator('#asTable tbody tr').count()>0
    page.screenshot(path=str(media/'v3_assurance.png'),full_page=True)
    page.locator('button[data-page="forecast"]').click()
    assert page.locator('#page-forecast').is_visible()
    page.locator('#fcDemo').click()
    assert 'SYNTHETIC' in page.locator('#fcStatus').inner_text()
    assert page.locator('#fcTable tbody tr').count()==6
    page.screenshot(path=str(media/'v3_forecast.png'),full_page=True)
    page.locator('button[data-page="alliances"]').click()
    assert page.locator('#page-alliances').is_visible()
    assert page.locator('#advItin').inner_text().strip(), 'Prior network engine broke'
    page.locator('button[data-page="capacity"]').click()
    assert page.locator('#page-capacity').is_visible()
    # Responsive + mobile nav
    mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    mobile.on('pageerror',lambda e:errors.append(str(e)))
    mobile.set_content(inline_page(),wait_until='load')
    mobile.locator('#mobilePageSelect').select_option('assurance')
    assert mobile.locator('#page-assurance').is_visible()
    mobile.screenshot(path=str(media/'v3_mobile.png'),full_page=True)
    browser.close()
if errors:raise AssertionError('Page JS errors: '+repr(errors))
print('PASS: all four v3 pages, interactive inputs, prior v2 modules, desktop/mobile browser checks. Screenshots generated.')
