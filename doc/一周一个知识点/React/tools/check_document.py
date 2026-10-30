"""QA check for the React study guide HTML (mirrors docker/check_document.py)."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parents[2]  # workspace root
doc=root/'react';qa=root/'.work'/'qa-react';qa.mkdir(exist_ok=True)
report={'checks':[],'errors':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 context=browser.new_context(viewport={'width':1440,'height':1060},device_scale_factor=1,permissions=['clipboard-read','clipboard-write'])
 page=context.new_page();errors=[];external=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:external.append(r.url) if r.url.startswith('http') else None)
 page.goto((doc/'react.html').as_uri());page.wait_for_load_state('networkidle')
 page.emulate_media(reduced_motion='reduce')
 assert page.locator('article h2').count()==16
 assert page.locator('.toc a').count()==16
 assert page.locator('img.diagram').count()==17
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 for a in page.locator('.toc a').all():
  assert page.evaluate('(id)=>document.getElementById(id)!==null',a.get_attribute('href')[1:])
 report['checks'].append('16 chapter anchors valid; desktop has no page-level horizontal overflow')
 page.screenshot(path=str(qa/'desktop-cover.png'))
 for i in [0,4,6,8,10,12,14]:
  h=page.locator('article h2').nth(i);h.scroll_into_view_if_needed();page.evaluate('(e)=>window.scrollTo(0,e.getBoundingClientRect().top+window.scrollY-30)',h.element_handle());page.screenshot(path=str(qa/f'desktop-chapter-{i}.png'))
 for i,img in enumerate(page.locator('.diagram').all()):
  img.scroll_into_view_if_needed();page.wait_for_function('(e)=>e.complete && e.naturalWidth>0',arg=img.element_handle())
 report['checks'].append('All 17 embedded figures load')
 copy=page.locator('.copy').first;copy.scroll_into_view_if_needed();expected=page.locator('.codebox code').first.inner_text();copy.click();expect(copy).to_have_text('已复制');actual=page.evaluate('navigator.clipboard.readText()');assert actual==expected,(repr(actual),repr(expected))
 report['checks'].append('Code copy writes exact code to clipboard')
 page.locator('.diagram').first.click();assert page.locator('#zoom').evaluate('(e)=>e.open');assert page.locator('#zoomimage').get_attribute('src').startswith('data:image/svg+xml');page.locator('#closezoom').click();assert not page.locator('#zoom').evaluate('(e)=>e.open')
 report['checks'].append('Figure zoom opens and closes')
 context.set_offline(True);page.reload();page.wait_for_load_state('load')
 for img in page.locator('.diagram').all():img.scroll_into_view_if_needed();page.wait_for_function('(e)=>e.complete && e.naturalWidth>0',arg=img.element_handle())
 assert not external
 report['checks'].append('Standalone file renders with network disabled; no external requests')
 page.set_viewport_size({'width':390,'height':844});page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(qa/'mobile-cover.png'))
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 page.locator('#menu').click();assert page.locator('#menu').get_attribute('aria-expanded')=='true'
 link=page.locator('.toc a').nth(8);target=link.get_attribute('href');link.click();assert page.locator('#menu').get_attribute('aria-expanded')=='false';assert page.evaluate('location.hash')==target
 page.screenshot(path=str(qa/'mobile-chapter-8.png'))
 for i in [4,6,10,14]:
  h=page.locator('article h2').nth(i);h.scroll_into_view_if_needed();page.evaluate('(e)=>window.scrollTo(0,e.getBoundingClientRect().top+window.scrollY-68)',h.element_handle());assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(qa/f'mobile-chapter-{i}.png'))
 report['checks'].append('390px mobile layout has no page overflow; menu and chapter navigation work')
 page.emulate_media(media='print');assert not page.locator('.sidebar').is_visible();assert not page.locator('.copy').first.is_visible();assert page.locator('article h2').count()==16
 report['checks'].append('Print stylesheet hides navigation and controls, retains all chapters')
 report['errors']=errors;assert not errors
 report['code_blocks']=page.locator('.codebox').count();report['chapter_count']=16;report['figures']=17
 browser.close()
Path(root/'.work'/'react-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
files=[qa/'desktop-cover.png',qa/'desktop-chapter-4.png',qa/'desktop-chapter-8.png',qa/'mobile-cover.png',qa/'mobile-chapter-8.png']
canvas=Image.new('RGB',(1540,760),'#e2e7ed');x=0
for f in files:
 if not f.exists(): continue
 im=Image.open(f);im.thumbnail((420 if 'desktop' in f.name else 220,700));canvas.paste(im,(x,25));ImageDraw.Draw(canvas).text((x+5,730),f.stem,fill='#123');x+=im.width+12
canvas.save(root/'.work'/'react-page-contact.png')
