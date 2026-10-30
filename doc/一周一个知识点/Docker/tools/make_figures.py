"""Generate original SVG diagrams for the Docker study guide; stdlib only."""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parents[1] / 'assets'
OUT.mkdir(exist_ok=True)
C = {'ink':'#172c48','muted':'#536982','blue':'#2563eb','bluebg':'#edf4ff','teal':'#008675','tealbg':'#e8f7f2','orange':'#b75a18','orangebg':'#fff3e6','line':'#c5d4e6','paper':'#f7faff','white':'#fff'}

def text(x,y,s,size=18,fill='ink',weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{C.get(fill,fill)}" font-weight="{weight}" text-anchor="{anchor}">{escape(s)}</text>'

def rect(x,y,w,h,fill='white',stroke='line',r=16):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}"/>'

def box(x,y,w,h,title,lines=(),tone='blue',title_size=20):
    s=rect(x,y,w,h,tone+'bg') + f'<rect x="{x}" y="{y+15}" width="4" height="{h-30}" rx="2" fill="{C[tone]}"/>'
    s+=text(x+18,y+32,title,title_size,'ink',650)
    for i,l in enumerate(lines): s+=text(x+18,y+62+i*25,l,16,'muted')
    return s

def arrow(x1,y1,x2,y2,label=None,lx=None,ly=None,dash=False):
    s=f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="{C["blue"]}" stroke-width="2.5" marker-end="url(#arrow)"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'
    if label:s+=text(lx if lx is not None else (x1+x2)/2,ly if ly is not None else (y1+y2)/2-12,label,15,'muted',anchor='middle')
    return s

def note(y,s):return rect(35,y,1010,48,'white')+text(53,y+30,s,17,'muted')

def save(name,num,title,subtitle,body,h=560):
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="{h}" viewBox="0 0 1080 {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7" fill="#2563eb"/></marker></defs>
<style>text{{font-family:"PingFang SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif}}</style>
<rect width="1080" height="{h}" rx="22" fill="#f7faff"/>
{text(35,37,'DOCKER / '+num,13,'blue',700)}{text(35,78,title,29,'ink',700)}{text(35,110,subtitle,17,'muted')}
{body}</svg>'''
    (OUT/name).with_suffix('.svg').write_text(svg)

# 1. Three models.
s=''
for x,title,sub in [(35,'虚拟机','每台来宾系统有自己的内核'),(385,'Linux 原生容器','容器共享所在主机的内核'),(735,'macOS / Windows','Linux 容器在 Linux 环境内')]:
 s+=rect(x,140,310,404)+text(x+18,176,title,22,'ink',700)+text(x+18,204,sub,16,'muted')
s+=box(52,225,130,73,'应用 A',[],title_size=18)+box(198,225,130,73,'应用 B',[],title_size=18)
s+=box(52,314,130,92,'来宾 OS',['内核 + 依赖'],'teal',18)+box(198,314,130,92,'来宾 OS',['内核 + 依赖'],'teal',18)
s+=box(52,423,276,93,'Hypervisor / 硬件',['虚拟化硬件与系统'],'orange',18)
s+=box(402,225,130,111,'容器 A',['应用 + 依赖'],'blue',18)+box(548,225,130,111,'容器 B',['应用 + 依赖'],'blue',18)
s+=box(402,354,276,70,'共享 Linux 内核',[],'teal',19)+box(402,443,276,73,'宿主机硬件',[],'orange',19)
s+=box(752,225,276,73,'容器：应用 + 依赖',[],title_size=19)+box(752,314,276,92,'Linux 虚拟化环境',['Linux 内核 + 容器引擎'],'teal',19)+box(752,423,276,93,'macOS / Windows 主机',['虚拟化支持 + 硬件'],'orange',19)
s+=note(565,'镜像封装用户态依赖；常规 Linux 容器不携带并启动一个独立的 Linux 内核。')
save('01-containers-vm','01','容器与虚拟机：隔离在哪一层','从内核归属看差异，比“容器是一台小电脑”的类比更准确。',s,638)

# 2. Lifecycle.
s=box(35,165,220,145,'01 源码与构建说明',['应用代码','Dockerfile / 锁文件','构建上下文'])
s+=box(302,165,220,145,'02 构建镜像',['BuildKit','只读层 + 默认配置','本地制品'])
s+=box(569,165,220,145,'03 镜像仓库',['清单 / 配置 / 层','tag 指向内容','digest 标识内容'])
s+=box(836,165,209,145,'04 创建容器',['启动应用进程','网络 + 可写层','挂载 + 资源限制'],'teal')
s+=arrow(255,240,302,240,'build',279,225)+arrow(522,240,569,240,'push',545,225)+arrow(789,240,836,240,'pull',812,225)
s+=box(571,362,474,86,'运行时输入',['环境配置 · 密钥 · 端口 · 数据卷'],'orange')+arrow(940,362,940,310)
s+=text(46,371,'常见更新路径',19,'ink',700)+text(46,405,'修改源码 → 重新构建 → 更新镜像 → 重建容器',17,'muted')
s+=note(473,'镜像可复用，容器可替换；配置和持久数据需要单独管理。')
save('02-lifecycle','02','从源码到运行服务','构建、分发和运行是不同阶段；运行中的容器不会自动跟随源码更新。',s,546)

# 3. Runtime.
s=box(35,150,205,108,'Docker CLI',['解析 docker 命令','调用 Engine API'])+box(295,150,205,108,'dockerd',['管理镜像与配置','网络 / 卷 / 容器'])+box(555,150,205,108,'containerd',['运行管理','协调容器任务'])+box(815,150,230,108,'shim + runc',['生命周期桥接','创建与启动进程'])
s+=arrow(240,204,295,204)+arrow(500,204,555,204)+arrow(760,204,815,204)
s+=box(295,380,205,104,'BuildKit',['构建依赖图','缓存 / 构建执行'],'orange')+box(35,380,205,104,'镜像制品',['只读层','配置与清单'],'orange')
s+=arrow(398,258,398,380,'构建路径',451,326)+arrow(295,430,240,430)
s+=box(555,380,490,104,'Linux 内核 + 应用进程',['namespaces · cgroups · 挂载 · 网络 · 安全约束'],'teal')+arrow(930,258,930,380,'运行路径',977,326)
s+=note(510,'runc 完成启动后通常退出；应用进程继续运行，shim 维持相关任务管理。')
save('05-runtime','05','一次 docker run 背后的协作','Docker 提供管理体验，低层运行时通过 Linux 内核机制创建容器环境。',s,582)

# 4. Layers.
s=box(140,155,350,100,'容器 A 的可写层',['A 的文件变化与临时状态'],'orange')+box(590,155,350,100,'容器 B 的可写层',['B 的文件变化与临时状态'],'orange')
s+=arrow(315,305,315,255)+arrow(765,305,765,255)
s+=box(140,305,800, 60,'只读层 3：应用文件',[],title_size=20)
s+=box(140,380,800,60,'只读层 2：语言运行时与依赖',[],title_size=20)
s+=box(140,455,800,60,'只读层 1：基础用户态文件系统',[],title_size=20)
s+=note(544,'Copy-on-Write：对共享只读内容的修改形成私有变化；共享卷是另一条数据路径。')
save('06-layers','06','共享镜像层，隔离容器修改','这是分层与写时复制的概念示意，不对应所有存储后端的具体目录布局。',s,616)

# 5. Network.
s=rect(690,143,355,386,'white')+text(710,176,'Compose 自定义网络',20,'ink',700)
s+=box(35,224,230,116,'宿主机浏览器',['localhost = 本机','GET /api/visits'])+box(345,224,265,116,'宿主机发布端口',['127.0.0.1:8080','转发到 web:80'],'orange')
s+=box(715,201,305,78,'Nginx / web:80',[],title_size=21)+box(715,326,305,78,'API / api:8000',[],title_size=21)+box(715,450,305, 60,'DB / db:5432',[],'teal',21)
s+=arrow(265,280,345,280,'HTTP',305,262)+arrow(610,280,715,240)
s+=arrow(865,279,865,326,'内部 DNS',958,308)+arrow(865,404,865,450,'内部连接',958,432)
s+=note(553,'浏览器不在 Docker 网络里；它不能直接把 api 或 db 当作可解析的主机名。')
save('03-network','03','localhost 取决于请求从哪里发出','发布端口解决宿主机访问；服务名解析解决同一容器网络内的访问。',s,626)

# 6. Storage.
s=''
items=[(35,'容器可写层',['位置：容器文件系统','写入临时状态','重启同一容器通常保留'],['删除容器后丢失','适合：可丢弃文件'],'blue'),(295,'命名卷 Volume',['位置：Docker 管理','独立存储对象','可重新挂载给新容器'],['明确删卷才移除','适合：数据库 / 模型'],'teal'),(555,'绑定挂载 Bind',['位置：指定主机路径','容器直接访问该路径','可配置只读'],['主机文件独立存在','适合：源码 / 配置'],'blue'),(815,'tmpfs',['位置：内存文件系统','不做持久保存','占用主机内存资源'],['停止后不保留数据','适合：短期临时文件'],'orange')]
for x,t,ls,bottom,tone in items:
 s+=box(x,160,230,296,t,ls,tone,20)
 s+=text(x+18,356,bottom[0],17,tone,650)+text(x+18,388,bottom[1],15,'muted')
s+=note(492,'持久化 ≠ 备份。备份要能恢复；数据库优先使用数据库支持的一致性备份方法。')
save('04-storage','04','四种存储，四种生命周期','先判断数据应该活多久，再决定写到哪里。',s,565)

# 7. Fullstack.
s=rect(277,147,768,199,'white')+text(298,171,'Compose 项目网络：服务名发现，API 与 DB 不发布宿主机端口',17,'muted')
s+=box(35,187,190,92,'浏览器',['GET / POST'],'orange')+box(310,187,190,92,'Nginx',['web:80'])+box(578,187,190,92,'Python API',['api:8000'])+box(845,187,180,92,'PostgreSQL',['db:5432'],'teal')
s+=arrow(225,232,310,232,'本机 8080',268,166)+arrow(500,232,578,232,'/api/',538,170)+arrow(768,232,845,232,'SQL',806,170)
s+=box(310,429,385,107,'密码文件 / Compose secrets',['只授予 API 和数据库服务','容器中从 /run/secrets 读取'],'orange')
s+=box(795,429,250,107,'命名卷 db_data',['数据库数据文件','跨容器重建保留'],'teal')
s+=arrow(590,429,673,279,dash=True)+arrow(935,279,935,429,'持久写入',993,387)
s+=text(36,392,'启动顺序',18,'ink',700)+text(36,425,'DB healthy',17,'muted')+text(36,454,'↓ API healthy',17,'muted')+text(36,483,'↓ 启动 Web',17,'muted')
s+=note(565,'验收动作：点击加一 → down → up → 再读取计数；保留命名卷时计数应保持。')
save('07-fullstack','07','全栈实践：请求、依赖与数据','静态页面 → 反向代理 → API → PostgreSQL，一条链路练习核心概念。',s,638)

# 8. AI.
s=box(35,175,240,115,'调用方 / 业务 API',['请求 prompt / 参数','接收 JSON 或流式响应'])+box(420,175,245,115,'Ollama 容器',['推理服务程序','监听容器 11434'])+box(800,175,245,115,'模型数据卷',['模型权重与缓存','/root/.ollama'],'teal')
s+=arrow(275,230,420,230,'HTTP API',347,211)+arrow(800,230,665,230,'加载模型',732,211)
s+=box(35,400,290,115,'服务镜像',['程序与用户态运行库','更新服务后可复用模型'])+box(420,400,625,115,'宿主环境：CPU / 内存 / GPU / 驱动',['CPU 可入门；GPU 需要兼容设备、宿主机驱动和运行时支持','macOS Docker Desktop 无法靠 --gpus all 使用 Apple Metal'],'orange')
s+=arrow(270,400,456,290,'创建服务',337,345)+arrow(543,400,543,290,'计算资源',603,348)
s+=note(548,'三个阶段分别验收：服务可访问 → 模型已下载 → 实际推理成功。')
save('08-ai','08','AI 服务：镜像、模型与硬件分开管理','模型文件大小不等于运行内存；容器化也不会自动提供 GPU 加速。',s,623)
print('Generated 8 original SVG diagrams in',OUT)
