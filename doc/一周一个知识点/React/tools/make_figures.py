"""Generate original SVG diagrams for the React study guide; stdlib only."""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parents[1] / 'assets'
OUT.mkdir(exist_ok=True)
C = {'ink':'#172c48','muted':'#536982','blue':'#2563eb','bluebg':'#edf4ff','teal':'#008675','tealbg':'#e8f7f2','orange':'#b75a18','orangebg':'#fff3e6','purple':'#6d28d9','purplebg':'#f1ecfd','red':'#b91c1c','redbg':'#fdecec','line':'#c5d4e6','paper':'#f7faff','white':'#fff'}

def text(x,y,s,size=18,fill='ink',weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{C.get(fill,fill)}" font-weight="{weight}" text-anchor="{anchor}">{escape(s)}</text>'

def rect(x,y,w,h,fill='white',stroke='line',r=16):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}"/>'

def box(x,y,w,h,title,lines=(),tone='blue',title_size=20):
    s=rect(x,y,w,h,tone+'bg') + f'<rect x="{x}" y="{y+15}" width="4" height="{h-30}" rx="2" fill="{C[tone]}"/>'
    s+=text(x+18,y+32,title,title_size,'ink',650)
    for i,l in enumerate(lines): s+=text(x+18,y+62+i*25,l,16,'muted')
    return s

def arrow(x1,y1,x2,y2,label=None,lx=None,ly=None,dash=False,color='blue'):
    s=f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="{C[color]}" stroke-width="2.5" marker-end="url(#arrow)"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'
    if label:s+=text(lx if lx is not None else (x1+x2)/2,ly if ly is not None else (y1+y2)/2-12,label,15,'muted',anchor='middle')
    return s

def note(y,s):return rect(35,y,1010,48,'white')+text(53,y+30,s,17,'muted')

def save(name,num,title,subtitle,body,h=560):
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="{h}" viewBox="0 0 1080 {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7" fill="#2563eb"/></marker></defs>
<style>text{{font-family:"PingFang SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif}}</style>
<rect width="1080" height="{h}" rx="22" fill="#f7faff"/>
{text(35,37,'REACT / '+num,13,'blue',700)}{text(35,78,title,29,'ink',700)}{text(35,110,subtitle,17,'muted')}
{body}</svg>'''
    (OUT/name).with_suffix('.svg').write_text(svg)

# 1. React's position in the web stack.
s=''
for x,title,sub in [(35,'浏览器三件套','结构 / 样式 / 行为'),(385,'React','用组件描述界面'),(735,'用户看到的页面','组合后的真实结果')]:
 s+=rect(x,140,310,404)+text(x+18,176,title,22,'ink',700)+text(x+18,204,sub,16,'muted')
s+=box(52,225,130,92,'HTML',['结构语义'],'orange',18)+box(198,225,130,92,'CSS',['样式与布局'],'teal',18)
s+=box(52,333,276,73,'JavaScript',['逻辑、事件、数据、DOM 操作'],'blue',18)
s+=box(402,225,130,111,'组件 A',['JSX + 样式 + 状态'],'blue',18)+box(548,225,130,111,'组件 B',['JSX + 样式 + 状态'],'blue',18)
s+=box(402,354,276,70,'组件树（复用与组合）',[],'purple',19)+box(402,443,276,73,'React 渲染到真实 DOM',[],'orange',19)
s+=box(752,225,276,92,'静态页面',['HTML / CSS / 图片'],'teal',19)+box(752,333,276,92,'交互界面',['事件、状态、数据'],'orange',19)+box(752,443,276,73,'浏览器渲染与绘制',[],'blue',19)
s+=note(565,'React 不替代 HTML 与 CSS：它负责用组件描述界面、把状态变成 DOM。')
save('01-react-position','01','React 在 Web 技术栈中的位置','把界面拆成可复用的组件，用声明式方式描述页面结果。',s,638)

# 2. Component tree.
s=box(395,150,290,92,'App（根组件）',['组合页面结构'],'purple',22)
s+=box(155,320,215,100,'Header',['标题与导航'],'blue',19)+box(430,320,215,100,'TodoPanel',['业务区域'],'blue',19)+box(705,320,215,100,'Footer',['版权与链接'],'blue',19)
s+=arrow(490,242,262,320,'包含',376,282)+arrow(540,242,537,320)+arrow(540,242,812,320,'包含',676,282)
s+=box(155,480,215,88,'Logo / Nav',['再拆小组件'],'teal',18)+box(430,480,215,88,'TodoInput',['输入新增'],'teal',18)+box(705,480,215,88,'TodoList',['列表渲染'],'teal',18)
s+=arrow(262,420,262,480)+arrow(537,420,537,480)+arrow(812,420,812,480)
s+=note(592,'页面 = 组件树；组合优于继承，一个组件只负责一个清晰的职责。')
save('02-component-tree','02','页面即组件树','从上到下逐层组合，每个组件输入 Props、维护自己的状态。',s,665)

# 3. JSX compile pipeline.
s=box(35,165,240,150,'JSX 源码',['<h1>你好</h1>','<Button onClick={fn}/>'],'purple',21)
s+=box(335,165,240,150,'React.createElement',['描述界面的普通对象','React 元素（element）'],'blue',21)
s+=box(635,165,240,150,'虚拟 DOM 树',['元素组成的树','可比较、可复用'],'teal',21)
s+=box(935,165,135,150,'真实 DOM',['浏览器节点','页面上的结果'],'orange',19)
s+=arrow(275,240,335,240,'编译',305,222)+arrow(575,240,635,240,'创建',605,222)+arrow(875,240,935,240,'渲染',905,222)
s+=text(46,386,'组件函数',19,'ink',700)+text(46,420,'UI 是数据的函数：render(state) → 元素 → DOM',17,'muted')
s+=note(473,'JSX 不是 HTML：它是 JavaScript 的语法扩展，最终编译为 React 元素。')
save('03-jsx-compile','03','从 JSX 到真实 DOM','写 JSX、编成元素、构建虚拟树，再交给浏览器渲染。',s,546)

# 4. One-way data flow.
s=box(340,150,400,96,'App：状态 owner（数据源）',['useState 保存数据','setState 触发更新'],'purple',21)
s+=box(120,330,200,104,'子组件 A',['props 只读接收','事件回调上报'],'blue',19)+box(460,330,200,104,'子组件 B',['props 只读接收','事件回调上报'],'blue',19)+box(760,330,200,104,'子组件 C',['props 只读接收','事件回调上报'],'blue',19)
s+=arrow(455,246,220,330,'props 数据向下',337,288)+arrow(520,246,560,330,'props',540,290)+arrow(520,246,860,330,'props',690,290)
s+=arrow(220,434,455,498,'事件向上',337,470,dash=True)+arrow(560,434,520,498,'回调',540,470,dash=True)+arrow(860,434,520,498,'回调',690,470,dash=True)
s+=box(340,498,400,96,'状态提升到共同父组件',['多个子组件共享同一份数据','修改集中在父组件'],'teal',20)
s+=text(46,398,'单向数据流',19,'ink',700)+text(46,432,'数据沿组件树向下流动；修改通过事件回调向上传递。',17,'muted')
s+=note(620,'State 是组件私有的；需要共享时提升到最近的共同父组件。')
save('04-dataflow','04','单向数据流与状态提升','理解数据从哪来、往哪去，是组件设计的第一课。',s,693)

# 5. Lifecycle & effects.
s=''
for x,title,lines,tone in [(35,'挂载 Mount',['组件首次出现','执行 effect（如请求）','清理函数暂存'],'blue'),(395,'更新 Update',['props / state 变化','组件重新渲染','依赖变化时重跑 effect'],'orange'),(755,'卸载 Unmount',['组件从树中移除','执行清理函数','取消订阅 / 定时器'],'teal')]:
 s+=box(x,160,290,180,title,lines,tone,21)
s+=arrow(325,250,395,250,'',360,235)+arrow(685,250,755,250,'',720,235)
s+=text(46,415,'useEffect(fn, deps)',19,'ink',700)+text(46,449,'deps 为空：只执行一次；deps 变化：对应更新后重跑；返回清理函数。',17,'muted')
s+=note(492,'副作用指渲染之外的“外部动作”：请求、订阅、定时器、直接操作 DOM。')
save('05-lifecycle','05','组件生命周期与副作用','理解组件从挂载到卸载的三个阶段，以及 effect 的时机。',s,565)

# 6. Virtual DOM & reconciliation.
s=box(35,155,300,120,'上一次虚拟 DOM',['组件状态 S1 的元素树','保存为可比较快照'],'blue',20)
s+=box(395,155,300,120,'这一次虚拟 DOM',['状态 S2 重新生成的树','与旧树逐层比较'],'orange',20)
s+=box(755,155,300,120,'差异结果（diff）',['仅变化的节点','插入 / 更新 / 删除'],'purple',20)
s+=arrow(335,215,395,215,'对比',365,197)+arrow(695,215,755,215,'差异',725,197)
s+=box(395,380,660,100,'React 只把变化提交给真实 DOM',['最小化 DOM 操作 → 减少重排与重绘','key 帮助 React 识别列表中哪些元素保持不变'],'teal',21)
s+=arrow(455,275,455,380,'仅提交变化',509,330)
s+=text(46,438,'为什么用虚拟 DOM',19,'ink',700)+text(46,472,'直接在浏览器操作 DOM 昂贵；先改内存中的对象，再一次批量提交。',17,'muted')
s+=note(513,'虚拟 DOM 是手段而非目标：目标是“用最小代价让界面与状态一致”。')
save('06-virtual-dom','06','虚拟 DOM 与协调（diff）','状态变化 → 重新生成元素树 → 比较差异 → 批量更新真实 DOM。',s,586)

# 7. Render & commit.
s=box(35,165,230,130,'触发渲染',['初次挂载','setState / 父组件更新','组件内状态变化'],'orange',20)
s+=box(330,165,230,130,'render 阶段',['调用组件函数','生成新的元素树','React 内部计算差异'],'blue',20)
s+=box(625,165,230,130,'commit 阶段',['把变化写入真实 DOM','执行 layout effect','触发 ref 回调'],'purple',20)
s+=box(880,165,165,130,'浏览器绘制',['重排 / 重绘','用户看到新界面'],'teal',19)
s+=arrow(265,230,330,230)+arrow(560,230,625,230)+arrow(855,230,880,230)
s+=text(46,395,'一条更新链路',19,'ink',700)+text(46,429,'setState → 组件函数重新执行 → 新元素树 → 差异 → 提交 DOM。',17,'muted')
s+=note(472,'渲染阶段可能被打断（并发特性）；commit 阶段按顺序提交给 DOM。')
save('07-render-flow','07','一次状态更新如何到达界面','把“数据变化”翻译成“界面变化”的两阶段过程。',s,545)

# 8. Hooks overview.
s=text(36,176,'常用 Hooks',19,'ink',700)
items=[(35,195,'useState',['组件内可变状态','返回 [值, 更新函数]'],'blue'),(295,195,'useEffect',['副作用时机','依赖数组控制执行'],'orange'),(555,195,'useRef',['跨渲染保存值','不触发重新渲染'],'teal'),(815,195,'useMemo',['缓存计算结果','依赖不变则复用'],'purple')]
for x,y,t,ls,tone in items:s+=box(x,y,230,118,t,ls,tone,20)
items2=[(35,395,'useCallback',['缓存函数引用','配合 memo 使用'],'blue'),(295,395,'useContext',['跨层级共享数据','避免逐层传 props'],'teal'),(555,395,'自定义 Hook',['以 use 开头','封装可复用逻辑'],'purple'),(815,395,'规则',['顶层调用','不能在条件 / 循环中调用'],'orange')]
for x,y,t,ls,tone in items2:s+=box(x,y,230,118,t,ls,tone,20)
s+=note(553,'Hooks 让函数组件拥有状态与副作用能力；顺序稳定是它们工作的前提。')
save('08-hooks','08','Hooks：函数组件的工具箱','按场景选工具，而不是记住每一个 API 的细节。',s,626)

# 9. Todo practice architecture.
s=rect(277,147,768,199,'white')+text(298,171,'状态从 App 流向列表与统计；事件从底部组件向上回调',17,'muted')
s+=box(35,187,190,92,'App',['todos 状态','useState + 派生'],'purple',21)+box(310,187,190,92,'TodoInput',['输入框','提交事件'],'blue',19)+box(578,187,190,92,'TodoList',['map 渲染列表','key 定位元素'],'teal',19)+box(845,187,180,92,'TodoItem',['勾选 / 删除','每行一个组件'],'orange',18)
s+=arrow(225,232,310,232,'新增',268,168)+arrow(500,232,578,232,'数据',538,170)+arrow(768,232,845,232,'渲染',806,170)
s+=box(310,429,385,107,'派生数据',['剩余未完成数','已完成统计'],'blue')
s+=box(795,429,250,107,'更新策略',['不可直接改原数组','用新数组替换 state'],'orange')
s+=text(36,392,'组件边界',18,'ink',700)+text(36,425,'每个组件只关心自己的职责',17,'muted')+text(36,454,'状态放最小共同父组件',17,'muted')
s+=note(565,'练习验收：增、删、勾选都生效；刷新页面后状态重置（持久化见实践二）。')
save('09-todo','09','Todo 实践：组件拆分与状态流向','一个小项目把 JSX、Props、State、列表渲染串起来。',s,638)

# 10. Frontend-backend interaction.
s=box(35,175,240,115,'React 组件',['发起请求','展示数据 / 加载态'],'purple',21)+box(420,175,245,115,"fetch('/api/todos')",['GET / POST / DELETE','返回 Promise'],'blue',20)+box(800,175,245,115,'后端 API 服务',['处理业务逻辑','读写数据库'],'teal',20)
s+=arrow(275,230,420,230,'HTTP 请求',347,211)+arrow(800,230,665,230,'HTTP 响应',732,211)
s+=box(35,400,290,115,'请求三态',['loading：加载中','data：成功数据','error：失败信息'],'orange',20)
s+=box(420,400,625,115,'开发注意事项',['同源或配置代理，避免跨域困扰','请求参数与响应结构要约定好','错误与重试是体验的一部分'],'blue',20)
s+=arrow(270,400,456,290,'发起请求',337,345)+arrow(543,400,543,290,'状态更新',603,348)
s+=note(548,'浏览器不能直接读数据库：所有数据都通过 API 进出。')
save('10-api','10','React 与后端：请求的完整链路','组件发起请求、后端返回数据、组件根据三态渲染界面。',s,623)

# 11. Router.
s=box(35,165,220,145,'浏览器地址栏',['/ 或 /todos','刷新 / 前进后退'],'orange',20)
s+=box(302,165,220,145,'React Router',['匹配 URL 到路由表','切换页面组件'],'blue',20)
s+=box(569,165,220,145,'页面组件',['HomePage','TodoPage / DetailPage'],'teal',20)
s+=box(836,165,209,145,'共享布局',['导航栏','Outlet 内容区'],'purple',19)
s+=arrow(255,240,302,240,'URL',279,222)+arrow(522,240,569,240,'匹配',545,222)+arrow(789,240,836,240,'渲染',812,222)
s+=text(46,371,'为什么需要路由',19,'ink',700)+text(46,405,'单页应用只有一个 HTML；用 URL 驱动组件切换，并支持直接访问与刷新。',17,'muted')
s+=note(473,'部署到服务器时要配置 SPA 回退：未匹配路径统一返回 index.html。')
save('11-router','11','路由：URL 驱动页面切换','路由表把地址映射到组件，SPA 因此拥有多个“页面”。',s,546)

# 12. Build & deploy.
s=box(35,165,220,145,'01 源码与配置',['组件与业务代码','package.json / 依赖','Vite 配置'],'blue',21)
s+=box(302,165,220,145,'02 开发服务器',['npm run dev','热更新（HMR）','本地调试'],'teal',20)
s+=box(569,165,220,145,'03 生产构建',['npm run build','打包 + 压缩','生成 dist/ 静态文件'],'orange',20)
s+=box(836,165,209,145,'04 部署托管',['静态服务器 / CDN','配置 SPA 回退','HTTPS 访问'],'purple',19)
s+=arrow(255,240,302,240,'dev',279,222)+arrow(522,240,569,240,'build',545,222)+arrow(789,240,836,240,'upload',812,222)
s+=box(571,362,474,86,'构建产物是纯静态文件',['可交给 Nginx / GitHub Pages / CDN 等任意静态托管'],'blue')
s+=text(46,371,'构建 ≠ 部署',19,'ink',700)+text(46,405,'dist 目录里的文件可以单独复制分享；部署只是把它放到能访问的地方。',17,'muted')
s+=note(473,'环境变量：构建时注入的配置会在打包时写进产物；运行时注入需要专门方案。')
save('12-build','12','从源码到线上页面','开发、构建、部署三个阶段各做一件事；dist 是交付物。',s,546)

# 13. Fiber architecture.
s=rect(35,150,240,330,'white')+text(55,180,'组件树（元素）',19,'ink',700)
s+=box(55,205,200,52,'App',[],'purple',18)+box(55,278,200,52,'Header',[],'blue',17)+box(55,351,200,52,'Panel',[],'blue',17)+box(55,424,200,52,'Footer',[],'blue',17)
s+=arrow(155,257,155,278)+arrow(155,330,155,351)+arrow(155,403,155,424)
s+=text(46,528,'组件树 = 嵌套关系',17,'muted')+text(46,560,'Fiber 树 = 工作单元链表',17,'muted')
s+=arrow(275,315,340,315,'编译 + 创建',308,297)
s= s+rect(340,150,705,330,'white')+text(360,180,'Fiber 节点链表（可中断的工作单元）',19,'ink',700)
s+=box(360,205,140,90,'fiber(App)',['child / return 指针'],'purple',17)
s+=box(540,205,140,90,'fiber(Header)',['child / return'],'blue',16)+box(720,205,140,90,'fiber(Panel)',['child / sibling / return'],'blue',16)+box(900,205,100,90,'fiber(Footer)',['sibling / return'],'blue',14)
s+=arrow(500,250,540,250)+arrow(680,250,720,250)+arrow(860,250,900,250)
s+=box(540,340,140,80,'fiber(Item1)',['child / return'],'teal',16)+box(720,340,140,80,'fiber(Item2)',['return'],'teal',16)
s+=arrow(790,295,610,340,'child',700,312,dash=True)+arrow(680,380,720,380,'sibling',700,365)
s+=text(360,470,'return 指针指回父节点，供渲染完成后向上回溯；每个节点都携带状态、副作用与更新队列。',17,'muted')
s+=note(513,'React 15 的递归渲染一旦开始不能中断；Fiber 把渲染拆成小工作单元，为暂停、恢复与优先级调度打下基础。')
save('13-fiber-arch','13','Fiber：可中断的渲染工作单元','组件树描述“是什么”，Fiber 链表描述“怎么一步步算出来”。',s,586)

# 14. Double buffering.
s=text(46,175,'current 树（用户当前看到的界面）',19,'ink',700)
s+=box(100,195,160,52,'div',[],'blue',17)+box(300,195,160,52,'Header',[],'blue',16)+box(500,195,160,52,'List',[],'blue',16)
s+=box(720,195,160,52,'Footer',[],'blue',16)
s+=arrow(260,221,300,221)+arrow(460,221,500,221)+arrow(660,221,720,221)
s+=text(46,330,'workInProgress 树（本次更新正在构建）',19,'ink',700)
s+=box(100,350,160,52,'div',[],'orange',17)+box(300,350,160,52,'Header',[],'orange',16)+box(500,350,160,52,'List',[],'orange',16)
s+=box(720,350,160,52,'Footer',[],'orange',16)
s+=arrow(260,376,300,376)+arrow(460,376,500,376)+arrow(660,376,720,376)
s+=arrow(180,247,180,350,'render 阶段\n构建新树',240,300,dash=True)+arrow(800,247,800,350,'render 阶段\n构建新树',872,300,dash=True)
s+=arrow(500,402,500,470,'commit：一次性切换 current 指针',660,440)
s+=note(505,'用户只看到提交后的结果：渲染中途被丢弃、被打断，屏幕上的 current 树都不会出现“半成品”。')
save('14-double-buffer','14','双缓存：渲染不被打断才能提交','两棵树交替使用：一棵展示，一棵构建；提交时整体切换。',s,578)

# 15. Hooks linked list.
s=box(35,170,310,100,'组件函数执行',['每渲染一次就执行一次','Hooks 按顺序被调用'],'purple',21)
s+=box(395,170,310,100,'fiber.memoizedState',['指向 hook 链表头','保存每个 hook 的数据'],'blue',21)
s+=box(755,170,300,100,'hook 节点链表',['useState → useEffect → useRef','每个节点保存状态 / 依赖'],'teal',20)
s+=arrow(345,220,395,220,'挂载',370,203)+arrow(705,220,755,220,'遍历',730,203)
s+=box(35,390,310,100,'再次执行',['按相同顺序访问链表','复用已有节点'],'blue',20)
s+=box(395,390,310,100,'读取 / 更新',['useState 返回新值','useEffect 检查依赖'],'teal',20)
s+=box(755,390,300,100,'顺序错位 = 数据错位',['条件 / 循环中调用','React 无法对应状态'],'orange',20)
s+=arrow(190,270,190,390,'下一次渲染',263,330)+arrow(550,270,550,390,'同一链表',613,330)
s+=note(513,'Hooks 没有魔法：它们就是挂在 fiber 上的有序链表。顺序稳定，才能把“第几个调用”对应到“第几份状态”。')
save('15-hooks-list','15','Hooks 的实现：按调用顺序挂链表','函数组件没有实例，状态存在 fiber 节点的链表中；顺序即身份。',s,586)

# 16. Synthetic events.
s=rect(35,150,1010,215,'white')+text(55,178,'浏览器 DOM 树',19,'ink',700)
s+=box(60,205,180,70,'#root（容器）',['事件委托挂载点'],'purple',17)
s+=box(320,205,140,70,'button A',['onClick'],'blue',16)+box(540,205,140,70,'button B',['onClick'],'blue',16)+box(760,205,140,70,'button C',['onClick'],'blue',16)
s+=arrow(390,275,240,275,'冒泡',315,258)+arrow(610,275,240,275,'冒泡',425,258)+arrow(830,275,240,275,'冒泡',535,258)
s+=box(395,400,650,100,'React 合成事件系统',['在 root 上统一监听原生事件','按 fiber 树模拟组件间的冒泡传播','提供跨浏览器一致的 event 对象'],'blue',20)
s+=arrow(240,275,240,400,'统一处理',305,340)
s+=text(46,540,'收益',19,'ink',700)+text(46,574,'监听器数量少、接口一致；事件优先级可被调度器感知（点击高优先级，滚动低优先级）。',17,'muted')
s+=note(606,'合成事件对象在事件处理结束后会被复用；不要在异步回调里长期保存它，需要时先取出字段。')
save('16-events','16','合成事件：委托到 root 再分发','原生事件先冒泡到根容器，React 再按组件树把事件“派发”给对应组件。',s,678)

# 17. Scheduler & concurrency.
s=rect(35,150,1010,150,'white')+text(55,178,'渲染工作单元的时间切片（示意）',19,'ink',700)
s+=box(60,205,180,70,'更新 A（点击）',['紧急 · 高优先级'],'orange',17)
s+=box(320,205,480,70,'更新 B（大列表）',['useTransition 标记为低优先级'],'blue',17)
s+=box(880,205,130,70,'更新 C',['普通'],'teal',16)
s+=arrow(240,240,320,240,'打断',280,222)+arrow(800,240,880,240)
s+=text(46,360,'时间轴：高优先级插入，低优先级让路',19,'ink',700)
s+=rect(46,380,996,72,'white')
s+=rect(60,392,120,48,fill='#b91c1c',stroke='line')+text(75,422,'A',19,'white',700)
s+=rect(200,392,300,48,fill='#2563eb',stroke='line')+text(230,422,'B：渲染一部分',17,'white')
s+=rect(520,392,120,48,fill='#b91c1c',stroke='line')+text(535,422,'A 再插入',17,'white')
s+=rect(660,392,140,48,fill='#008675',stroke='line')+text(690,422,'B 重新渲染',17,'white')
s+=text(46,492,'配合 Suspense',19,'ink',700)+text(46,526,'低优先级更新未就绪时先显示 fallback（加载占位），数据到达后再替换。',17,'muted')
s+=note(558,'并发不是“同时执行”，而是“渲染可中断、按优先级调度”，让输入响应不被大任务卡住。')
save('17-scheduler','17','并发渲染与优先级调度','紧急更新可以打断低优先级渲染；被打断的工作可以丢弃重做。',s,631)

print('Generated 17 original SVG diagrams in',OUT)
