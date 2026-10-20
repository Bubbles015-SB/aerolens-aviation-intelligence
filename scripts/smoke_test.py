#!/usr/bin/env python3
"""Browser QA, optional: pip install playwright; use local Chromium.

This harness inlines CSS/scripts into about:blank to work in environments
that disable local file:// and loopback browsing. The shipped app itself
can be opened directly from index.html without any build or server.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text(encoding='utf-8')
html=html.replace('<link rel="stylesheet" href="assets/style.css" />',
                  '<style>'+(ROOT/'assets/style.css').read_text(encoding='utf-8')+'</style>')
html=html.replace('<script src="assets/data.js"></script>',
                  '<script>'+(ROOT/'assets/data.js').read_text(encoding='utf-8')+'</script>')
html=html.replace('<script src="assets/app.js"></script>',
                  '<script>'+(ROOT/'assets/app.js').read_text(encoding='utf-8')+'</script>')

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1512,'height':1040},device_scale_factor=1,accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda err: errors.append(str(err)))
    page.set_content(html,wait_until='load')
    assert page.title()=='AeroLens — Transatlantic Market Intelligence'
    assert page.locator('#metricPax').inner_text()=='17.13M'
    assert page.locator('#metricCount').inner_text()=='28'
    assert page.locator('#routeTable tbody tr').count()==28
    (ROOT/'media').mkdir(exist_ok=True)
    page.screenshot(path=str(ROOT/'media/market-dashboard.png'),full_page=True)

    page.locator('#regionFilter').select_option('West')
    assert page.locator('.bar-row').count()==8
    page.locator('[data-sort="growth"]').click()
    assert 'AUS' not in page.locator('.bar-chart').inner_text()  # Austin is South
    page.locator('#searchRoutes').fill('Boston')
    assert page.locator('#routeTable tbody tr').count()==1
    page.locator('#searchRoutes').fill('')

    page.locator('[data-page="alliances"]').click()
    assert page.locator('#itinerarySubtitle').inner_text().startswith('LHR → MIA')
    assert page.locator('.itin').count()==2
    page.screenshot(path=str(ROOT/'media/alliance-lab.png'),full_page=True)
    page.locator('#minConnect').fill('165')
    assert page.locator('.itin').count()==0
    page.locator('#minConnect').fill('60')

    page.locator('[data-page="quality"]').click()
    assert page.locator('#validationTitle').inner_text()=='All integrity checks passed'
    assert page.locator('.check').count()==7

    page.locator('[data-page="brief"]').click()
    assert page.locator('#modelPax').inner_text()=='128,810'
    page.screenshot(path=str(ROOT/'media/decision-brief.png'),full_page=True)
    page.locator('#captureShare').fill('10')
    assert page.locator('#modelPax').inner_text()=='322,024'
    page.locator('#briefMarket').select_option('ATL')
    assert 'Atlanta' in page.locator('#memoBody').inner_text()

    # Responsive smoke check on a common phone viewport.
    mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    mobile.on('pageerror',lambda err: errors.append(str(err)))
    mobile.set_content(html,wait_until='load')
    assert mobile.locator('#metricPax').inner_text()=='17.13M'
    mobile.locator('#mobilePageSelect').select_option('alliances')
    assert mobile.locator('#page-alliances').is_visible()
    mobile.locator('#mobilePageSelect').select_option('market')
    # A zero-width sidebar is intentionally hidden on small screens; dashboard remains readable.
    mobile.screenshot(path=str(ROOT/'media/mobile-dashboard.png'),full_page=True)
    assert not errors, errors
    print('PASS: market metrics, route search, filters, alliance scenario, quality checks, scenario model, responsive layout')
    print('Saved four screenshots to',ROOT/'media')
    browser.close()
