from pathlib import Path
from playwright.sync_api import sync_playwright
HTML=(Path(__file__).resolve().parent.parent/'demo_standalone.html').read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--no-proxy-server'])
    page=browser.new_page(viewport={'width':1440,'height':920},accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(HTML,wait_until='domcontentloaded')
    assert page.locator('h1').first.inner_text()=='看见产业链，更要看见证据'
    assert page.locator('.data-table tbody tr').count()==5
    page.locator('[data-stage="part"]').click()
    assert page.locator('.data-table tbody tr').count()>=3
    page.locator('#clearStage').click()
    page.locator('[data-company="zj"]').first.click()
    assert '374.57' in page.locator('#modalBody').inner_text()
    page.locator('#closeModal').click()
    page.locator('[data-view="claims"]').click()
    assert page.locator('.data-table tbody tr').count()==9
    page.locator('#gradeFilter').select_option('C')
    assert page.locator('.data-table tbody tr').count()==1
    page.locator('[data-claim="C04"]').first.click()
    assert 'CPO' in page.locator('#modalBody').inner_text()
    page.locator('#closeModal').click()
    page.locator('[data-view="peers"]').click()
    assert '76' in page.locator('.score').inner_text()
    page.locator('[data-peer="tf|lite"]').click()
    assert '67' in page.locator('.score').inner_text()
    page.locator('[data-view="impact"]').click()
    assert page.locator('.path-item').count()==4
    page.locator('[data-event="trade"]').click()
    assert page.locator('.path-item').count()==3
    page.locator('[data-intensity="high"]').click()
    assert '进取' in page.locator('#app').inner_text()
    page.locator('[data-view="copilot"]').click()
    page.locator('[data-ask="新易盛CPO有收入吗？"]').click()
    page.wait_for_timeout(300)
    assert page.locator('.chat-msg').count()==3
    assert '不能说已有经核实的CPO规模收入' in page.locator('.chat-msg').last.inner_text()
    page.locator('[data-view="sources"]').click()
    assert page.locator('.source-card').count()>=10
    form=page.locator('#evidenceForm')
    form.locator('[name="company"]').select_option('xy')
    form.locator('[name="topic"]').fill('CPO收入预审测试')
    form.locator('[name="url"]').fill('https://disc.static.szse.cn/example')
    form.locator('[name="excerpt"]').fill('公司计划开展CPO相关研发和产业化推进，本次提交并不能说明已经形成CPO收入。')
    form.locator('button[type="submit"]').click()
    assert '待人工复核' in page.locator('#modalBody').inner_text()
    page.locator('#closeModal').click()
    assert page.locator('.source-card').count()>=11
    with page.expect_download() as dl:
        page.locator('#exportBtn').click()
    data=dl.value
    assert data.suggested_filename.endswith('.json')
    print('PASS 14: routes/filter/modal/grades/comparison/impact/chat/create/export')
    print('JS errors:',errors)
    assert not errors
    browser.close()
