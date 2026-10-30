# 第 3 章 · 亲手做一个镜像：Dockerfile

> 本章目标：学会写 Dockerfile，把你自己的 Node 应用打包成镜像。**实战项目从这里正式启动。**

---

## 3.1 为什么不能只用别人的镜像

前两章我们一直在用 `nginx`、`postgres` 这些**现成的**镜像。但你自己的项目（那段 Express 代码、那个 Vue 应用）Docker Hub 上可没有，得**自己打包成镜像**。

怎么打包？你得告诉 Docker：用什么基础环境、把哪些代码放进去、怎么装依赖、启动时跑什么命令。这份"打包说明书"就是 **Dockerfile**。

---

## 3.2 Dockerfile 是什么

> **Dockerfile = 一份文本写的"自动化装机说明书"。**

生活类比：你请人帮你配一台新电脑，留了张纸条："①装 Windows ②装 Node ③把我的项目拷到 D 盘 ④双击 start.bat 启动"。Dockerfile 就是这张纸条，只不过执行者是 Docker，而且**每次执行结果都一模一样**。

它的好处：

- **可复现**：同一个 Dockerfile，今天构建、明天构建、在任何机器上构建，结果一致。
- **可追溯**：环境怎么搭的，白纸黑字写在 Dockerfile 里，不再是"我当时好像装了啥忘了"。
- **版本化**：Dockerfile 是文本，可以提交进 Git，跟代码一起管理。

---

## 3.3 指令逐个精讲

Dockerfile 由一行行**指令**组成，每条指令通常产生一个镜像层（回顾 2.4 分层）。下面是最常用的指令，边讲边给例子。

```dockerfile
# 这是注释，以 # 开头

FROM node:20-alpine
# FROM：指定【基础镜像】，必须是第一条有效指令。
#   这里基于官方 node:20-alpine（内置 Node 20 的精简系统）。一切从它之上开始搭。

WORKDIR /app
# WORKDIR：设置【工作目录】，相当于 cd /app。之后的 COPY、RUN、CMD 都以此为当前目录。
#   如果 /app 不存在会自动创建。强烈建议用它，别在根目录 / 下瞎放文件。

COPY package*.json ./
# COPY：把【构建上下文】里的文件复制进镜像。
#   package*.json 匹配 package.json 和 package-lock.json
#   ./ 指当前工作目录（即 /app）
#   ★ 为什么先只拷这两个文件？为了利用缓存，第 4 章会详解。

RUN npm ci
# RUN：在构建镜像时【执行一条命令】，结果固化成一层。
#   npm ci 按 lock 文件精确安装依赖（比 npm install 更适合构建，可复现）。
#   这一步产生的 node_modules 会被打进镜像层。

COPY . .
# 把项目【其余所有文件】拷进镜像。
#   第一个 . = 构建上下文（你本机项目目录）
#   第二个 . = 镜像里的工作目录 /app

ENV NODE_ENV=production PORT=3000
# ENV：设置【环境变量】，容器运行时也能读到。
#   这里设了 NODE_ENV 和 PORT 两个。

EXPOSE 3000
# EXPOSE：【声明】容器会监听 3000 端口。
#   ⚠️ 注意：它只是【文档性声明/元数据】，并不会真的帮你把端口映射出去！
#   想从外面访问，运行时仍要自己写 -p 3000:3000。EXPOSE 更多是给人看、给工具用。

CMD ["node", "server.js"]
# CMD：容器启动时【默认执行的命令】。这就是容器的"主进程"。
#   用 JSON 数组写法（叫 exec 形式），推荐！详见 3.5。
```

几条还没出场但常见的指令：

```dockerfile
ARG VERSION=1.0        # 构建期变量，只在 build 时存在，可用 --build-arg 覆盖。区别于 ENV（运行期也在）
ENTRYPOINT ["node"]    # 入口，和 CMD 配合，见 3.5
USER node              # 切换运行用户，别用 root 跑应用（安全，见第10章）
HEALTHCHECK ...        # 健康检查，告诉 Docker 怎么判断容器"真的健康"
```

---

## 3.4 ⚠️ 对比表：COPY vs ADD

两个都能"把文件放进镜像"，长得像，区别要记清：

| | `COPY` | `ADD` |
|--|--------|-------|
| 复制本地文件/目录 | ✅ | ✅ |
| 自动解压本地 tar 压缩包 | ❌ | ✅（会自动解压） |
| 支持从 URL 下载 | ❌ | ✅（但不推荐） |
| 行为可预测性 | 高（就是单纯复制） | 低（有"隐藏魔法"） |

**最佳实践：默认永远用 `COPY`。** 它行为单纯、可预测。只有在你**确实需要自动解压本地 tar 包**时才用 `ADD`。从 URL 下载文件请用 `RUN curl/wget`（更可控，还能在同层清理缓存）。

> 💡 记忆：`ADD` 有"自动解压 + 下载"的额外魔法，但魔法往往带来意外。**能用 COPY 就别用 ADD。**

---

## 3.5 ⚠️ 对比表：CMD vs ENTRYPOINT

这是 Dockerfile 里最烧脑的一对，但用"餐厅"类比就清楚了：

- **ENTRYPOINT** = 这家店"固定就是做这件事"（比如"我们是面馆"）。
- **CMD** = 默认的"今日推荐"，**可以被顾客点单覆盖**。

核心区别：

| | `CMD` | `ENTRYPOINT` |
|--|-------|--------------|
| 定位 | 容器启动的**默认命令/默认参数** | 容器的**固定入口程序** |
| 能否被 `docker run` 后面的参数覆盖 | ✅ 整个被覆盖 | ❌ 不被覆盖（后面的参数会作为**它的参数**追加） |
| 典型用途 | "默认跑这个，但允许换" | "这个容器就是干这个的" |

看四种组合的实际效果（假设镜像里 `docker run myimg [后面的东西]`）：

```dockerfile
# 组合A：只有 CMD
CMD ["node", "server.js"]
#   docker run myimg            → 执行 node server.js
#   docker run myimg npm test   → ★ 被覆盖，执行 npm test（CMD 整个被换掉）

# 组合B：只有 ENTRYPOINT
ENTRYPOINT ["node"]
#   docker run myimg            → 执行 node（没参数，可能进 REPL）
#   docker run myimg server.js  → ★ 执行 node server.js（server.js 作为 node 的参数追加）

# 组合C：ENTRYPOINT + CMD（最常见的专业写法）
ENTRYPOINT ["node"]
CMD ["server.js"]
#   docker run myimg            → node server.js（ENTRYPOINT + CMD 默认参数）
#   docker run myimg app.js     → node app.js（ENTRYPOINT 固定，CMD 的默认参数被 app.js 覆盖）
```

**给你的实用建议**：

- **新手/大多数应用**：只用 `CMD ["node", "server.js"]` 就够了，简单直接。
- **做工具型镜像**（容器本质是个命令行工具，比如一个 `ffmpeg` 镜像）：用 `ENTRYPOINT` 固定工具，`CMD` 给默认参数。
- ⚠️ **务必用 JSON 数组形式** `["node", "server.js"]`（exec 形式），**不要**写成 `CMD node server.js`（shell 形式）。shell 形式会套一层 `/bin/sh -c`，导致**进程 PID 不是你的程序、收不到 stop 信号、无法优雅退出**。这是个很隐蔽但很重要的坑。

---

## 3.6 `docker build` 与构建上下文

写好 Dockerfile，用 `docker build` 把它变成镜像：

```bash
docker build -t todo-backend:1.0 .
# 逐个解释：
#   build              构建镜像
#   -t todo-backend:1.0  给镜像打标签（tag）：名字 todo-backend，版本 1.0
#   .                  ★【构建上下文】= 当前目录。这是最容易被忽视的参数！
```

### 什么是"构建上下文（build context）"？

`docker build` 最后那个 `.` **不是"在哪运行"，而是"把哪个目录打包发给 Docker 引擎"**。

还记得第 0 章说的吗——Docker 引擎跑在一个独立的（虚拟）环境里。你执行 build 时，Docker 会把**上下文目录里的所有文件打包**发给引擎，引擎才能在构建时 `COPY` 到这些文件。

⚠️ **两个重要后果**：

1. **COPY 只能拷上下文里的文件**。`COPY ../other/file .` 会失败，因为 `../other` 不在上下文（`.`）里。
2. **上下文越大，build 越慢**。如果你的目录里有个几百 MB 的 `node_modules` 或 `.git`，它们会被一并打包发给引擎，哪怕你根本没 COPY 它们。解决办法就是下一节的 `.dockerignore`。

---

## 3.7 `.dockerignore`：和 `.gitignore` 一样重要

在 Dockerfile 同级目录建一个 `.dockerignore` 文件，列出**不该进入构建上下文**的东西：

```gitignore
# .dockerignore
node_modules       # ← 宿主机的 node_modules 不要，镜像里会重新 npm ci 装（且平台可能不同！）
.git               # ← 版本历史，几百 MB，构建用不到
.env               # ← ★ 密钥文件，绝不能打进镜像（安全！）
*.log              # ← 日志文件
dist               # ← 本地构建产物（镜像里会重新构建）
Dockerfile         # ← Dockerfile 本身也没必要拷进镜像
.DS_Store          # ← macOS 的垃圾文件
```

**为什么重要**：

- **变快**：上下文变小，build 瞬间快很多。
- **变小**：避免把无关文件 `COPY . .` 进镜像。
- **变安全**：防止把 `.env`、密钥、`.git` 历史打进镜像被泄露。⚠️ **这是安全红线。**

> 💡 你已经很熟 `.gitignore` 了，`.dockerignore` 语法几乎一样，思路也一样：**声明哪些东西不参与（这次是不参与构建）**。

---

## 3.8 ⚠️ 常见坑

**坑 1：把宿主机的 `node_modules` COPY 进了镜像**
你 Mac 上装的 `node_modules` 可能含有为 macOS 编译的二进制模块，拷进 Linux 镜像里会**跑不起来**。正确做法：用 `.dockerignore` 排除它，在镜像里用 `RUN npm ci` 重新装 Linux 版的。

**坑 2：每次改一行代码，build 都要重装所有依赖，慢死**
这是因为你把 `COPY . .` 写在了 `RUN npm ci` 前面，导致代码一变，依赖层缓存就失效。正确顺序是"先拷 package.json 装依赖，再拷代码"——原因和完整优化第 4 章专门讲。

**坑 3：用了 shell 形式的 CMD，容器停不掉/停得慢**
`CMD node server.js`（shell 形式）会让你的 node 进程不是 PID 1，收不到 `docker stop` 的信号。改用 `CMD ["node", "server.js"]`。

**坑 4：忘了 `.` 或路径写错**
`docker build -t xxx` 漏掉结尾的 `.` 会报错（缺少上下文路径）。记住 build 命令**结尾几乎总有个 `.`**。

---

## 3.9 🔨 实战项目推进①：给 Node 后端写第一个 Dockerfile

我们正式开工实战项目。先建一个最小可跑的 Node 后端。

**第 1 步：创建项目文件**

新建一个目录 `todo-backend`，在里面建三个文件：

`package.json`：
```json
{
  "name": "todo-backend",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": { "start": "node server.js" },
  "dependencies": { "express": "^4.19.2" }
}
```

`server.js`：
```javascript
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Docker! 🐳', time: new Date().toISOString() });
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

`.dockerignore`：
```gitignore
node_modules
.git
*.log
.DS_Store
```

**第 2 步：写 Dockerfile**（就放在 `todo-backend/Dockerfile`）：

```dockerfile
# 基于官方 Node 20 的精简镜像
FROM node:20-alpine

# 设定工作目录
WORKDIR /app

# 先只拷依赖清单（利用缓存：代码改动不会让这层失效）
COPY package*.json ./

# 安装依赖
RUN npm install

# 再拷入其余源码
COPY . .

# 声明服务端口（文档性）
EXPOSE 3000

# 容器启动时运行的主进程
CMD ["node", "server.js"]
```

> 注：这里用 `npm install` 是因为我们没生成 lock 文件。生产项目建议提交 `package-lock.json` 并用 `npm ci`。

**第 3 步：构建镜像**

在 `todo-backend` 目录下执行：

```bash
docker build -t todo-backend:1.0 .
#   构建镜像，命名 todo-backend:1.0，上下文是当前目录
```

✅ **预期输出**：一连串 `=> [1/5] FROM ...`、`=> [4/5] RUN npm install`、`=> [5/5] COPY . .` 的步骤，最后是：
```
=> => naming to docker.io/library/todo-backend:1.0
```

确认镜像已生成：
```bash
docker images | grep todo-backend
#   预期看到：todo-backend   1.0   <镜像ID>   <刚才>   ~180MB 左右
```

**第 4 步：运行它**

```bash
docker run -d --name todo-api -p 3000:3000 todo-backend:1.0
#   后台运行，命名 todo-api，把宿主机 3000 映射到容器 3000
```

**用浏览器或命令访问：**

```bash
curl http://localhost:3000
```

✅ **预期输出**：
```json
{"message":"Hello from Docker! 🐳","time":"2026-09-10T..."}
```

看到这段 JSON，说明你**亲手构建的镜像跑起来了**！🎉 这是质的飞跃——你已经能把任意 Node 项目容器化了。

看看日志、清理：
```bash
docker logs todo-api        # ← 能看到 "Server running on port 3000"
docker rm -f todo-api       # ← 用完清理（镜像 todo-backend:1.0 保留，下一章还要用）
```

> 🎯 **自检**：试着改一下 `server.js` 里的 message，然后**重新 build**，你会发现 `FROM`、`COPY package*.json`、`RUN npm install` 几步都显示 `CACHED`（走了缓存），只有 `COPY . .` 之后重新执行了。这就是分层缓存的威力——下一章我们把它用到极致。

---

## ✅ 本章小结

- **Dockerfile = 自动化的装机说明书**，让镜像构建可复现、可追溯、可进 Git。
- 核心指令：`FROM`（基础镜像）、`WORKDIR`、`COPY`、`RUN`、`ENV`、`EXPOSE`（仅声明）、`CMD`（主进程）。
- **COPY vs ADD**：默认用 COPY，ADD 的自动解压/下载魔法少碰。
- **CMD vs ENTRYPOINT**：CMD 是可被覆盖的默认命令；ENTRYPOINT 是固定入口。⚠️ 都要用 JSON 数组形式。
- `docker build -t 名:tag .`，最后的 `.` 是**构建上下文**，配合 `.dockerignore` 让构建又快又安全。
- 你已经成功把一个 Node 应用打包成镜像并运行——实战项目第一步完成。

下一章，我们让这个镜像变得更"专业"：构建更快、体积更小。👉 [04-构建优化.md](./04-构建优化.md)
