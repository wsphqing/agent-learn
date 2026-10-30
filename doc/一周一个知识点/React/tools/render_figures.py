"""Render React study guide SVG diagrams to PNG (Chrome headless)."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]/'assets'
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 page=browser.new_page(viewport={'width':1120,'height':720},device_scale_factor=1.5)
 for f in sorted(root.glob('*.svg')):
  page.goto(f.as_uri());page.evaluate('document.fonts.ready')
  page.locator('svg').screenshot(path=str(f.with_suffix('.png')))
  print(f.name)
 browser.close()
thumbs=[]
for f in sorted(root.glob('*.png')):
 im=Image.open(f).convert('RGB');im.thumbnail((540,330))
 canvas=Image.new('RGB',(560,355),'#e1e7ef');canvas.paste(im,((560-im.width)//2,10));ImageDraw.Draw(canvas).text((12,336),f.stem,fill='#17314b');thumbs.append(canvas)
contact=Image.new('RGB',(1120,355*6),'white')
for i,im in enumerate(thumbs):contact.paste(im,((i%2)*560,(i//2)*355))
out=Path(__file__).resolve().parents[2]/'.work'/'react-diagram-contact.png'
contact.save(out)
print('Contact sheet:',out)
