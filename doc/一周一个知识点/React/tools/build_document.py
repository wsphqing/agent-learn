"""Build a standalone HTML document from react.md (Markdown + beautifulsoup4)."""
from pathlib import Path
import base64
import html
import re
import markdown
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'react.md').read_text()
body=markdown.markdown(source,extensions=['fenced_code','tables','toc','sane_lists'],extension_configs={'toc':{'permalink':False}})
soup=BeautifulSoup(body,'html.parser')
title=soup.h1.get_text(); soup.h1.decompose()
nav=[]
for h in soup.find_all('h2'):
    nav.append(f'<a href="#{html.escape(h["id"],quote=True)}">{html.escape(h.get_text())}</a>')
for img in soup.find_all('img'):
    original=ROOT/img['src']
    svg=original.with_suffix('.svg')
    payload=svg.read_bytes() if svg.exists() else original.read_bytes()
    mime='image/svg+xml' if svg.exists() else 'image/png'
    img['src']='data:'+mime+';base64,'+base64.b64encode(payload).decode()
    img['class']='diagram'
    img['loading']='lazy'
    img['tabindex']='0'
    img['role']='button'
    img['aria-label']='放大查看：'+img.get('alt','示意图')
    frame=soup.new_tag('figure'); img.wrap(frame)
    if frame.parent.name=='p': frame.parent.unwrap()
for table in soup.find_all('table'):
    wrap=soup.new_tag('div',attrs={'class':'table-wrap','tabindex':'0','role':'region','aria-label':'可横向滚动的表格'})
    table.wrap(wrap)
for pre in soup.find_all('pre'):
    wrapper=soup.new_tag('div',attrs={'class':'codebox'})
    pre.wrap(wrapper)
    label='TEXT'
    code=pre.find('code')
    if code:
        label=' / '.join(c.replace('language-','').upper() for c in code.get('class',[])) or 'TEXT'
    head=soup.new_tag('div',attrs={'class':'codehead'})
    span=soup.new_tag('span');span.string=label;head.append(span)
    btn=soup.new_tag('button',attrs={'class':'copy','type':'button','aria-label':'复制这段代码'})
    btn.string='复制';head.append(btn);pre.insert_before(head)

css=r'''
:root{--ink:#182c47;--muted:#5d6e83;--blue:#205dd7;--line:#dfe6ee;--paper:#fff;--wash:#f4f7fb;--nav:254px;scroll-behavior:smooth}
*{box-sizing:border-box}body{margin:0;background:var(--wash);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.9;-webkit-font-smoothing:antialiased}a{color:var(--blue);text-decoration:none;text-underline-offset:3px}a:hover{text-decoration:underline}button{font:inherit;cursor:pointer}button:focus-visible,a:focus-visible,img:focus-visible{outline:3px solid #f6a65b;outline-offset:3px}#progress{position:fixed;left:0;top:0;height:3px;width:0;background:var(--blue);z-index:30}
.sidebar{position:fixed;inset:0 auto 0 0;width:var(--nav);background:#fff;border-right:1px solid var(--line);padding:32px 20px 20px;overflow-y:auto;z-index:20}.brand{font-size:11px;letter-spacing:2px;color:var(--blue);font-weight:750}.brand strong{display:block;font-size:28px;letter-spacing:-1px;color:var(--ink);line-height:1.7}.sidebar .intro{font-size:12px;color:var(--muted);margin:12px 0 21px}.toc a{display:block;padding:9px 10px;margin:3px 0;border-radius:8px;font-size:13px;line-height:1.55;color:#53657e}.toc a.active,.toc a:hover{color:var(--blue);background:#edf3ff;text-decoration:none}.sidefoot{font-size:11px;color:#7a899d;margin:26px 10px}.mobilebar{display:none}
main{margin-left:var(--nav);padding:45px 52px 60px;min-width:0}.page{max-width:1030px;margin:auto}.hero{position:relative;padding:49px 52px;background:linear-gradient(125deg,#10284b,#1a4881);color:white;border-radius:20px;overflow:hidden;box-shadow:0 16px 48px #1f42681a}.hero:after{content:"";position:absolute;width:260px;height:260px;right:-115px;top:-110px;border:42px solid #ffffff0a;border-radius:50%}.eyebrow{color:#a9cdfa;letter-spacing:3px;font-size:12px;font-weight:650}.hero h1{font-size:53px;line-height:1.15;letter-spacing:-1px;margin:18px 0}.hero h1 span{font-size:26px;display:block;font-weight:500;letter-spacing:.1px;margin-top:15px;line-height:1.5}.hero p{max-width:620px;color:#d1e1f4;font-size:15px;margin:22px 0 26px}.pills{display:flex;gap:10px;flex-wrap:wrap}.pills span{padding:5px 12px;border:1px solid #ffffff26;border-radius:5px;background:#ffffff09;font-size:12px;color:#e4efff}.hero-actions{display:flex;align-items:center;justify-content:space-between;padding:18px 4px;color:var(--muted);font-size:12px;gap:10px}.subtle{background:#fff;border:1px solid var(--line);border-radius:7px;padding:5px 13px;color:var(--muted)}
article{background:#fff;border:1px solid var(--line);border-radius:16px;padding:35px 48px 50px;overflow:hidden}article>blockquote:first-child{margin-top:0}h2{font-size:28px;line-height:1.5;letter-spacing:-.3px;margin:76px 0 25px;padding-top:22px;border-top:2px solid #e7edf6;scroll-margin-top:32px}h2:first-of-type{margin-top:38px}h3{font-size:21px;line-height:1.6;margin:36px 0 15px;scroll-margin-top:30px}p{margin:16px 0}strong{font-weight:650}li{margin:9px 0}ul,ol{padding-left:1.5em}blockquote{border-left:3px solid #4582ed;background:#f4f8ff;color:#526681;margin:24px 0;padding:13px 20px;font-size:14px;border-radius:0 9px 9px 0}blockquote p{margin:4px 0}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.87em;padding:2px 5px;border-radius:4px;background:#eef3f9;overflow-wrap:anywhere}.codebox{margin:22px 0;border-radius:11px;overflow:hidden;background:#142338;border:1px solid #1d3453}.codehead{display:flex;justify-content:space-between;align-items:center;min-height:38px;padding:6px 14px;background:#1b2f49;color:#a9bed8;font-size:10px;letter-spacing:1.3px}.copy{line-height:1.5;font-size:11px;padding:3px 10px;color:#d4e4f9;border:1px solid #607894;border-radius:5px;background:transparent;letter-spacing:0}.copy:hover{background:#ffffff14}pre{margin:0;padding:19px 21px;overflow:auto;tab-size:4;line-height:1.75;font-size:13px;color:#e2ecf9}pre code{background:none;padding:0;color:inherit;border:0;font-size:inherit;white-space:pre;overflow-wrap:normal}
.table-wrap{margin:24px 0;overflow-x:auto;border:1px solid var(--line);border-radius:9px}table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.85}th,td{border-bottom:1px solid #e5ebf2;padding:12px 14px;text-align:left;vertical-align:top;min-width:100px}th{font-weight:650;background:#edf3fb;color:#24436c}tr:last-child td{border-bottom:0}tbody tr:nth-child(even){background:#fafbfd}td:first-child{font-weight:550}table code{font-size:.86em}.diagram{display:block;width:100%;height:auto;cursor:zoom-in;border-radius:12px}.diagram:hover{box-shadow:0 0 0 2px #d8e7fc}figure{margin:32px 0 13px}p:has(>em:only-child){font-size:13px;line-height:1.85;color:var(--muted);margin-top:10px}p:has(>em:only-child) em{font-style:normal}.footer{text-align:center;padding:32px 0 0;color:var(--muted);font-size:12px}#top{position:fixed;bottom:22px;right:22px;border:1px solid #ced9e7;border-radius:10px;background:#fff;padding:8px 13px;color:var(--blue);box-shadow:0 4px 16px #14365712;z-index:10}dialog{border:1px solid var(--line);padding:18px;border-radius:14px;max-width:96vw;max-height:94vh;background:#fff;color:var(--ink)}dialog::backdrop{background:#11223bdd;backdrop-filter:blur(4px)}.zoomhead{display:flex;justify-content:space-between;gap:20px;align-items:center;font-size:14px;margin-bottom:14px}.zoomscroll{overflow:auto;max-height:78vh}#zoomimage{display:block;width:1080px;max-width:none;height:auto}#scrim{display:none}
@media(min-width:1600px){main{padding-top:60px}.page{max-width:1130px}article{padding-left:62px;padding-right:62px}}
@media(max-width:1190px){:root{--nav:224px}main{padding:30px 25px}article{padding:26px 30px}.hero{padding:36px}.hero h1{font-size:46px}.hero h1 span{font-size:24px}}
@media(max-width:900px){:root{--nav:0px}.sidebar{width:280px;transform:translateX(-100%);transition:transform .2s}.sidebar.open{transform:none}.mobilebar{display:flex;position:sticky;top:0;background:#ffffffed;backdrop-filter:blur(12px);border-bottom:1px solid var(--line);z-index:15;padding:10px 17px;align-items:center;justify-content:space-between;font-size:13px;font-weight:650}.mobilebar button{font-size:12px}main{margin:0;padding:22px 18px 50px}h2,h3{scroll-margin-top:72px}#scrim.visible{display:block;position:fixed;inset:0;background:#152a4b55;z-index:18}.hero h1{font-size:45px}.hero{padding:30px}article{padding:23px 25px}.hero-actions{font-size:11px}}
@media(max-width:520px){body{font-size:15px;line-height:1.9}main{padding:15px 10px 50px}.hero{padding:27px 23px;border-radius:13px}.hero h1{font-size:43px}.hero h1 span{font-size:22px}.hero p{font-size:14px}.eyebrow{font-size:10px;letter-spacing:1.8px}.pills{gap:7px}.pills span{font-size:11px;padding:3px 8px}.hero-actions{align-items:flex-start;padding:14px 4px}article{padding:18px 19px;border-radius:12px}h2{font-size:24px;margin-top:58px}h3{font-size:19px}pre{font-size:12px;padding:15px}table{font-size:13px;min-width:550px}th,td{padding:10px 12px}blockquote{padding:11px 14px;font-size:13px}.diagram{border-radius:7px}figure{margin-left:-9px;margin-right:-9px}#top{font-size:12px;bottom:14px;right:14px}.zoomhead{font-size:12px}#zoomimage{width:1000px}}
@media(prefers-reduced-motion:reduce){:root{scroll-behavior:auto}.sidebar{transition:none}}
@media print{@page{size:A4;margin:16mm 15mm}body{background:#fff;font-size:11px;line-height:1.65}.sidebar,.mobilebar,#progress,#top,.hero-actions,.copy,#scrim,dialog{display:none!important}main{margin:0;padding:0}.page{max-width:none}.hero{box-shadow:none;color:#152b46;background:#fff;border:2px solid #244978;padding:24px;border-radius:0;break-after:page}.hero:after{display:none}.hero h1{font-size:42px}.hero h1 span{font-size:24px}.hero p,.eyebrow,.pills span{color:#234063}.pills span{border-color:#c6d5e7}article{border:0;padding:0;overflow:visible}h2{font-size:22px;break-before:page;margin-top:0;padding-top:12px;break-after:avoid}h3{font-size:16px;break-after:avoid}p,li{orphans:3;widows:3}blockquote{background:#f7f8fa}.codebox{background:#fafafa;border:1px solid #cdd6e1;break-inside:auto;border-radius:4px}.codehead{background:#eee;color:#456;min-height:22px;padding:3px 9px}pre{color:#152b46;font-size:8.5px;white-space:pre-wrap;padding:11px;overflow:visible}pre code{white-space:pre-wrap;word-break:break-word}.table-wrap{overflow:visible;border-radius:0}table{min-width:0;font-size:9.5px}th,td{padding:7px;min-width:0}thead{display:table-header-group}tr{break-inside:avoid}figure{break-inside:avoid;max-width:100%;margin:18px 0 8px}.diagram{max-height:155mm;object-fit:contain}a{color:#204c8c;text-decoration:none}.footer{font-size:9px}}
'''
js=r'''
const menu=document.querySelector('#menu');const side=document.querySelector('.sidebar');const scrim=document.querySelector('#scrim');
function closeNav(){side.classList.remove('open');scrim.classList.remove('visible');menu.setAttribute('aria-expanded','false');}
menu.addEventListener('click',()=>{const open=side.classList.toggle('open');scrim.classList.toggle('visible',open);menu.setAttribute('aria-expanded',String(open));});
scrim.addEventListener('click',closeNav);document.querySelectorAll('.toc a').forEach(a=>a.addEventListener('click',closeNav));document.addEventListener('keydown',e=>{if(e.key==='Escape')closeNav();});
document.querySelector('#print').addEventListener('click',()=>window.print());document.querySelector('#top').addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
document.querySelectorAll('.copy').forEach(btn=>btn.addEventListener('click',async()=>{const code=btn.closest('.codebox').querySelector('code').textContent;try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(code);}else{const area=document.createElement('textarea');area.value=code;area.style.position='fixed';area.style.opacity='0';document.body.append(area);area.select();if(!document.execCommand('copy'))throw new Error('copy failed');area.remove();}btn.textContent='已复制';}catch(e){btn.textContent='请手动选择';}setTimeout(()=>btn.textContent='复制',1600);}));
const heads=[...document.querySelectorAll('article h2')];const links=[...document.querySelectorAll('.toc a')];let scheduled=false;
function update(){const max=document.documentElement.scrollHeight-window.innerHeight;document.querySelector('#progress').style.width=(max?Math.min(100,window.scrollY/max*100):100)+'%';let active=heads[0];for(const h of heads){if(h.getBoundingClientRect().top<160)active=h;}links.forEach(a=>{const yes=decodeURIComponent(a.hash.slice(1))===active.id;a.classList.toggle('active',yes);if(yes)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});scheduled=false;}
window.addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(update);}},{passive:true});window.addEventListener('resize',update);update();
const dialog=document.querySelector('#zoom');const zoomImage=document.querySelector('#zoomimage');
function zoom(img){zoomImage.src=img.src;zoomImage.alt=img.alt;document.querySelector('#zoomtitle').textContent=img.alt;dialog.showModal();}
document.querySelectorAll('.diagram').forEach(img=>{img.addEventListener('click',()=>zoom(img));img.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();zoom(img);}});});
document.querySelector('#closezoom').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
'''
page=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="React 中文学习文档：组件、JSX、State、Hooks、虚拟 DOM、Fiber 与并发渲染原理，附 17 张原创示意图和完整示例代码。"><meta name="color-scheme" content="light"><title>{html.escape(title)}</title><style>{css}</style></head>
<body><div id="progress" aria-hidden="true"></div><div id="scrim"></div><div class="mobilebar"><span>一周一个知识点 / React</span><button id="menu" class="subtle" aria-controls="sidebar" aria-expanded="false">目录</button></div>
<aside class="sidebar" id="sidebar"><div class="brand">一周一个知识点<strong>REACT</strong></div><p class="intro">从组件思维到工程实践<br>概念 · 操作 · 原理 · 实践</p><nav class="toc" aria-label="章节目录">{''.join(nav)}</nav><div class="sidefoot">2026.09.15 · 学习手册<br>正文与示意图可离线阅读</div></aside>
<main><div class="page"><header class="hero"><div class="eyebrow">REACT / COMPONENTS / HOOKS</div><h1>React<span>从组件思维到工程实践</span></h1><p>用组件描述界面，让数据的变化自动变成界面的变化，再用完整项目把知识串起来。</p><div class="pills"><span>7 天学习路线</span><span>17 张原理示意图</span><span>3 个递进实践</span><span>16 道复盘题</span></div></header>
<div class="hero-actions"><span>面向有 HTML / CSS / JS 基础的开发者 · React 19 / Vite<br>资料核对：2026-09-15</span><button type="button" class="subtle" id="print">打印 / 保存 PDF</button></div>
<article>{soup}</article><footer class="footer">一周一个知识点 · React<br>先解释清楚，再动手验证。</footer></div></main>
<button id="top" aria-label="返回文档顶部">↑ 顶部</button><dialog id="zoom" aria-labelledby="zoomtitle"><div class="zoomhead"><span id="zoomtitle"></span><button class="subtle" id="closezoom">关闭</button></div><div class="zoomscroll"><img id="zoomimage" alt=""></div></dialog>
<script>{js}</script></body></html>'''
(ROOT/'react.html').write_text(page)
print('Built react.html:',len(page),'characters;',len(nav),'chapter links;',len(soup.find_all('img')),'embedded figures')
