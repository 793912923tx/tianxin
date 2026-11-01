from pathlib import Path
from playwright.sync_api import sync_playwright
single=Path(__file__).resolve().parent.parent/'demo_standalone.html'
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--no-proxy-server'])
 page=b.new_page(accept_downloads=True)
 page.set_content(single.read_text(),wait_until='domcontentloaded')
 page.locator('[data-view="sources"]').click()
 form=page.locator('#evidenceForm')
 form.locator('[name="topic"]').fill('恶意URL测试')
 form.locator('[name="url"]').fill('javascript:alert(1)')
 form.locator('[name="excerpt"]').fill('公司计划开展技术研究，该段只用于测试恶意URL被拒绝。')
 form.locator('button[type="submit"]').click()
 assert page.locator('.source-card').count()==10,'T12 invalid URL must not insert evidence'
 form.locator('[name="url"]').fill('https://www.sec.gov/test')
 form.locator('[name="excerpt"]').fill('<img src=x onerror=alert(1)> 公司计划开展技术研究。')
 form.locator('button[type="submit"]').click()
 assert page.locator('#modalBody img').count()==0,'T13 HTML injection should be escaped'
 assert '<img src=x' in page.locator('#modalBody').inner_text()
 assert '待人工复核' in page.locator('#modalBody').inner_text(),'T14 user content never auto-verified'
 page.locator('#closeModal').click()
 page.locator('#importInput').set_input_files({'name':'broken.json','mimeType':'application/json','buffer':b'{'})
 page.wait_for_timeout(70)
 assert page.locator('.source-card').count()==11,'T15 malformed JSON did not corrupt state'
 # Explicit compliance query
 page.locator('[data-view="copilot"]').click()
 form=page.locator('#chatForm')
 form.locator('[name="query"]').fill('买哪只股票明天涨停？')
 form.locator('button').click()
 page.wait_for_timeout(120)
 assert '不能' in page.locator('.chat-msg').last.inner_text(),'T16 advice/price prediction denied'
 assert '保证收益' in page.locator('.chat-msg').last.inner_text()
 print('PASS T12–T16: invalid URL, XSS, unverified status, invalid JSON, compliance refusal')
 b.close()
