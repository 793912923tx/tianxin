from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright
from subprocess import run
base=Path(__file__).resolve().parent.parent
single=(base/'demo_standalone.html').read_text()
folder=base/'demo'/'frames';folder.mkdir(parents=True,exist_ok=True)
font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
if not Path(font_path).exists():
 from subprocess import check_output
 font_path=check_output('fc-match -f "%{file}" "Noto Sans CJK SC"',shell=True,text=True).strip()
font=ImageFont.truetype(font_path,32)
font2=ImageFont.truetype(font_path,22)
font3=ImageFont.truetype(font_path,18)
scenes=[]
def grab(p,title,sub,seconds=8):
 p.wait_for_timeout(100)
 n=len(scenes)+1
 shot=folder/f'raw_{n:02}.png'
 p.screenshot(path=str(shot),full_page=False,animations='disabled')
 scenes.append((shot,title,sub,seconds))
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--no-proxy-server'])
 pg=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
 pg.set_content(single,wait_until='domcontentloaded')
 grab(pg,'01  从产业链开始研究','四层产业链与五家中美公司；每一个收入数字都保留披露口径。',8)
 pg.locator('[data-stage="module"]').click()
 grab(pg,'02  按产业链环节筛选','点击高速光模块环节；跨层公司可以多重归属，但不重复加总收入。',7)
 pg.locator('[data-company="zj"]').first.click()
 grab(pg,'03  穿透公司到业务与出处','打开中际旭创：光通信收发模块收入、报告期、机会与风险逐一呈现。',8)
 pg.locator('#closeModal').click()
 pg.locator('[data-view="claims"]').click()
 grab(pg,'04  概念关系不是二元判断','A已披露收入 / B批量交付 / C研发计划 / D第三方表态 / E证据不足。',8)
 pg.locator('#gradeFilter').select_option('C')
 grab(pg,'05  筛选仅有研发或规划的主张','“光互联产品有收入”并不能证明“CPO有已核验收入”。',7)
 pg.locator('[data-claim="C04"]').click()
 grab(pg,'06  查看CPO反例的原文证据','新易盛经营计划仅支持研发与产业化推进；不可推断已有规模销售。',8)
 pg.locator('#closeModal').click()
 pg.locator('[data-view="peers"]').click()
 grab(pg,'07  中外可比 ≠ 数值直接可比','中际旭创对Coherent：技术与需求可比，产品收入与分部收入不可直比。',8)
 pg.locator('[data-peer="tf|lite"]').click()
 grab(pg,'08  换一组上游公司核对边界','天孚对Lumentum：器件角色有交集，Components却是更宽的披露范围。',7)
 pg.locator('[data-view="impact"]').click()
 grab(pg,'09  海外AI投资上修的传导路径','资本开支 → 交换端口 → 光模块需求 → 收入、毛利与上游器件订单。',9)
 pg.locator('[data-event="trade"]').click()
 grab(pg,'10  政策影响也必须有条件','贸易规则变化先触及跨境供货与成本，再通过毛利率、存货等财务科目体现。',8)
 pg.locator('[data-view="copilot"]').click()
 pg.locator('[data-ask="新易盛CPO有收入吗？"]').click()
 pg.wait_for_timeout(200)
 grab(pg,'11  AI助研必须能回答“不确定”','离线证据检索返回S02、S06，明确没有可核验的CPO独立营收。',9)
 pg.locator('[data-view="sources"]').click()
 grab(pg,'12  任何结论都能追溯原始材料','证据库保留来源编号、公告日期、财报期、原始URL与定位信息。',8)
 form=pg.locator('#evidenceForm')
 form.locator('[name="company"]').select_option('xy')
 form.locator('[name="topic"]').fill('CPO研发新材料')
 form.locator('[name="url"]').fill('https://disc.static.szse.cn/test-example')
 form.locator('[name="excerpt"]').fill('公司计划围绕CPO新技术开展研发投入与产业化探索，不能由此确认任何CPO收入。')
 form.locator('[name="notes"]').fill('模拟更新案例，无真实新增公告')
 form.locator('button[type="submit"]').click()
 grab(pg,'13  可更新，但不能自动“变真”','新材料预审为C级；系统明确标记“待人工复核”，支持JSON留痕导出。',9)
 browser.close()
for i,(img,title,sub,seconds) in enumerate(scenes,1):
 canvas=Image.new('RGB',(1600,900),(17,30,43))
 d=ImageDraw.Draw(canvas)
 # faint teal accent and line
 d.rounded_rectangle((55,30,155,36),radius=3,fill=(108,222,194))
 d.text((58,48),title,font=font,fill=(241,249,250))
 d.text((60,94),sub,font=font2,fill=(159,185,196))
 screenshot=Image.open(img).convert('RGB').resize((1360,765),Image.Resampling.LANCZOS)
 canvas.paste(screenshot,(120,130))
 d.rounded_rectangle((121,130,1478,895),radius=6,outline=(76,107,119),width=2)
 d.rectangle((1280,49,1540,83),fill=(29,63,75))
 d.text((1300,55),f'{i:02d} / {len(scenes):02d}   CASE DEMO',font=font3,fill=(151,220,203))
 dest=folder/f'frame_{i:02}.png'
 canvas.save(dest,optimize=True)
conc=base/'demo'/'frames'/'playlist.ffconcat'
lines=['ffconcat version 1.0']
for i,(_,_,_,secs) in enumerate(scenes,1):
 lines+=['file '+str(folder/f'frame_{i:02}.png'),f'duration {secs}']
lines+=['file '+str(folder/f'frame_{len(scenes):02}.png')]
conc.write_text('\n'.join(lines)+'\n')
out=base/'demo'/'OpticScope_AI_功能演示.mp4'
args=['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(conc),'-vf','fps=12,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','24','-movflags','+faststart',str(out)]
run(args,check=True,timeout=180)
print('Video:',out, 'scenes=',len(scenes),'seconds=',sum(s[-1] for s in scenes),'bytes=',out.stat().st_size)
