# 第 7 章 · 一键编排：Docker Compose

> 本章目标：用一个 YAML 文件描述整套服务，一条命令启动整个开发环境。这是日常开发中你用得最多的功能。

---

## 7.1 痛点：命令太长，记不住

回顾我们目前启动整套项目要敲的命令：

```bash
docker network create todo-net
docker run -d --name todo-db --network todo-net -e POSTGRES_PASSWORD=secret -v todo-pgdata:/var/lib/postgresql/data postgres:16
docker run -d --name todo-redis --network todo-net redis:7-alpine
docker build -t todo-backend:1.0 ./backend
docker run -d --name todo-api --network todo-net -p 3000:3000 -v $(pwd)/backend:/app todo-backend:1.0
docker build -t todo-frontend:1.0 ./frontend
docker run -d --name todo-web --network todo-net -p 8080:80 todo-frontend:1.0
```

**问题**：

- 五六条又长又臭的命令，参数全靠在脑子里记。
- 换个项目、换台机器，又得重敲一遍。
- 团队协作时，得给每个同事写一份"操作手册"，还容易漏。
- 想停掉全套？再敲一串 `docker rm -f ...`。

**Docker Compose 就是来解决这个的。**

---

## 7.2 Docker Compose 是什么

> **Compose = 用一个 YAML 文件，声明式地描述"这套系统有哪些服务、各自怎么配"，然后一条命令全搞定。**

生活类比：前面用 `docker run` 是"**手动一台台启动机器**"，每台都要单独操作；Compose 是"**写一份开机清单**"——清单上写好要开哪几台机器、每台什么配置，然后一句"按清单开机"，全部自动就位。

**核心价值**：

- **声明式**：你只描述"我要什么"，不用管"怎么一步步做"。
- **一条命令起全套**：`docker compose up`。
- **一条命令停全套**：`docker compose down`。
- **进版本控制**：`docker-compose.yml` 进 Git，全团队环境一致。

---

## 7.3 逐字段精讲 `docker-compose.yml`

来看我们实战项目的 Compose 文件，每一行都注释了：

```yaml
# 注意：新版 Compose 不需要写 version: 字段了（旧教程里的 version: '3' 已过时）
services:                                    # ← 顶层：定义所有服务
  db:                                        # ← 服务名。这个名字会自动成为【容器名的前缀+网络别名】
    image: postgres:16                       # ← 用现成镜像（不自己构建）
    environment:                             # ← 环境变量（等价于 docker run 的 -e）
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: tododb
    volumes:
      - todo-pgdata:/var/lib/postgresql/data # ← 数据卷挂载（卷名:容器路径）
    ports:
      - "5432:5432"                          # ← 端口映射（注意用引号包住，避免 YAML 解析成时间）
    healthcheck:                             # ← 健康检查（见 7.6）
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:                                     # ← 第二个服务：Redis
    image: redis:7-alpine
    volumes:
      - todo-redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:                                   # ← 我们的 Node 后端
    build: ./backend                         # ← 【构建】而非用现成镜像。指定 Dockerfile 所在目录
    # build 也可以展开写成：
    #   build:
    #     context: ./backend                   #   构建上下文
    #     dockerfile: Dockerfile               #   指定 Dockerfile 文件名（默认就是它）
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/tododb  # ← ★ 主机名直接写服务名 db！
      REDIS_URL: redis://redis:6379                            # ← ★ 同上，用服务名 redis
      PORT: 3000
    ports:
      - "3000:3000"
    depends_on:                              # ← 依赖关系（见 7.6，注意它的局限）
      db:
        condition: service_healthy           #   db 健康后再启动 backend
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app                       # ← 绑定挂载源码，实现开发热更新（第5章的技巧）
      - /app/node_modules                    # ← 匿名卷保护 node_modules
    command: npm run dev                     # ← 覆盖镜像默认的启动命令（开发用 nodemon）

  frontend:                                  # ← 前端
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

volumes:                                     # ← 顶层：声明用到的【数据卷】
  todo-pgdata:                               #   Compose 会自动创建它们
  todo-redisdata:
# 注意：networks 可以不用显式声明！Compose 默认会创建一个网络，
# 并把本文件里所有服务都接进去，所以服务之间能【直接用服务名互访】。
```

**几个关键点**：

1. **服务名就是主机名** ★：`db`、`redis`、`backend` 这些服务名，在同一个 Compose 网络里可以直接当域名用。所以后端连数据库写 `db:5432` 就行，非常干净。
2. **`build` vs `image`**：`build: ./backend` 表示"用这个目录的 Dockerfile 构建"；`image: postgres:16` 表示"直接用现成镜像"。
3. **端口要加引号**：`"5432:5432"` 建议加引号，避免 YAML 把 `5432:5432` 解析成"时间"之类的奇怪类型。
4. **相对路径基于 compose 文件所在目录**：`./backend`、`$(pwd)` 都相对 `docker-compose.yml` 的位置。

---

## 7.4 核心命令

Compose 的命令都是 `docker compose`（新版，中间空格）开头，**必须在你放 `docker-compose.yml` 的目录下执行**（否则要用 `-f 路径` 指定）。

```bash
docker compose up              # ← 启动所有服务（前台，日志直接打在终端，Ctrl+C 停）
docker compose up -d           # ← -d 后台启动。日常用这个
docker compose up -d --build   # ← ★ 强制先重新构建镜像再启动（改了 Dockerfile 后必用）

docker compose down            # ← 停止并删除所有容器 + 网络（★ 但【不删数据卷】，数据安全）
docker compose down -v         # ← ⚠️ 连数据卷一起删（数据会丢！谨慎用）
docker compose down --rmi all  # ← 连镜像也一起删

docker compose ps              # ← 查看本 compose 项目的容器状态
docker compose logs            # ← 查看所有服务日志
docker compose logs -f backend # ← ★ 只看 backend 服务，-f 持续跟随
docker compose exec backend sh # ← ★ 进入 backend 容器的 shell（调试神器）
docker compose run --rm backend npm test  # ← 用 backend 服务跑一次性命令（如测试）

docker compose restart backend # ← 重启某个服务
docker compose stop            # ← 只停止，不删除
docker compose start           # ← 启动已停止的
```

**日常最高频的两个**：

- 开发时：`docker compose up -d`，改代码（配合热更新），完事 `docker compose down`。
- 改了 Dockerfile 后：`docker compose up -d --build`（⚠️ 不加 `--build` 它不会重新构建，你会以为改了没生效）。

---

## 7.5 环境变量与 `.env` 文件

把敏感信息（密码、密钥）硬编码在 compose 文件里，提交到 Git 就泄露了。Compose 支持 **`.env` 文件**：

**`.env`（不提交进 Git，加到 `.gitignore`）**：
```bash
POSTGRES_PASSWORD=my_super_secret
DB_NAME=tododb
```

**`docker-compose.yml` 里用 `${}` 引用**：
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}   # ← 从 .env 读，不写死在文件里
      POSTGRES_DB: ${DB_NAME}
```

Compose 启动时会自动读取同目录的 `.env` 文件并替换 `${}`。这样配置文件可以安全地提交 Git，真正的密钥留在本地 `.env` 里。

⚠️ 别忘了把 `.env` 加进 `.gitignore`！这是安全红线。

---

## 7.6 ⚠️ 重点：`depends_on` 的真相

新手常有个误解：以为 `depends_on: [db]` 就保证"数据库好了，后端才启动"。**不是的！**

> ⚠️ **`depends_on` 默认只保证"启动顺序"（先起 db，再起 backend），不保证"服务真的就绪"。**

问题在哪：数据库容器"启动"了（进程起来了），但从"进程启动"到"能接受连接"之间还有几秒（要初始化数据目录、加载配置等）。如果后端在这几秒内就去连数据库，会连接失败、崩溃。

**正确解法：配合 `healthcheck` + `condition: service_healthy`**（就是我们 7.3 里写的）：

```yaml
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]  # ← 怎么判断 db "健康"了
      interval: 5s                                    #   每 5 秒检查一次
      timeout: 5s                                     #   单次检查超时时间
      retries: 5                                      #   连续失败 5 次才判定 unhealthy

  backend:
    depends_on:
      db:
        condition: service_healthy   # ← ★ 等 db【健康】了，才启动 backend
```

这样才是真正的"等数据库能用了再启动后端"。

> 💡 **补充**：即便有了 healthcheck，**应用自身也应该有重试逻辑**（连不上数据库时重试几次而不是直接崩）。这是更健壮的做法，工业级项目都会这么做。

---

## 7.7 ⚠️ 对比表：手动 `docker run` vs Compose

| 维度 | 手动 `docker run` | Docker Compose |
|------|------------------|----------------|
| 启动整套系统 | 五六条长命令 | **一条 `docker compose up -d`** |
| 配置存放 | 散在你的终端历史/脑子里 | **一个 `.docker-compose.yml` 文件** |
| 团队协作 | 发一份"操作手册"，易漏易错 | **共享同一个文件，环境一致** |
| 服务发现 | 要手动建网络、记容器名 | **服务名自动当主机名，零配置** |
| 停止清理 | 一长串 `docker rm -f` | **`docker compose down`** |
| 适合场景 | 单容器、临时调试 | **多服务项目的开发与部署** ★ |
| 学习曲线 | 记一堆参数 | 记一个文件格式 |

**结论**：**只要你的项目超过一个容器，就用 Compose。** 单跑一个临时容器才用 `docker run`。

---

## 7.8 🔨 实战项目推进④：一条命令拉起全套

我们把实战项目用 Compose 组织起来。**这是本项目的里程碑。**

**第 1 步：确认目录结构**

```
todo-app/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile          （第 3 章写的）
│   ├── package.json
│   └── server.js
└── frontend/
    ├── Dockerfile          （第 4 章写的）
    ├── package.json
    ├── index.html
    └── main.js
```

**第 2 步：改造后端，让它连数据库和 Redis**

把 `backend/server.js` 升级为：

```javascript
const express = require('express');
const { Pool } = require('pg');
const redis = require('redis');

const app = express();
const PORT = process.env.PORT || 3000;

// 连接 Postgres：注意主机名就是 compose 里的服务名 "db"
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
// 连接 Redis：主机名就是服务名 "redis"
const redisClient = redis.createClient({ url: process.env.REDIS_URL });
redisClient.connect();

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Docker! 🐳' });
});

// 验证数据库连通
app.get('/db', async (req, res) => {
  const r = await pool.query('SELECT NOW() as now');
  res.json({ db: 'connected', now: r.rows[0].now });
});

// 验证 Redis 连通
app.get('/cache', async (req, res) => {
  await redisClient.set('key', 'hello-from-redis');
  res.json({ redis: await redisClient.get('key') });
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

更新 `backend/package.json` 的依赖加上 `pg` 和 `redis`：

```json
{
  "name": "todo-backend",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": { "start": "node server.js" },
  "dependencies": {
    "express": "^4.19.2",
    "pg": "^8.12.0",
    "redis": "^4.7.0"
  }
}
```

> 为简化，这里用 `start` 而非 `dev`，即改动后端代码后需要 `docker compose restart backend`（不加 nodemon 依赖，减少变量）。

**第 3 步：写 `docker-compose.yml`**（放在 `todo-app/` 根目录）：

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: tododb
    volumes:
      - todo-pgdata:/var/lib/postgresql/data     # 数据卷，数据不丢
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/tododb   # ★ 主机名=服务名 db
      REDIS_URL: redis://redis:6379                             # ★ 主机名=服务名 redis
      PORT: 3000
    ports:
      - "3000:3000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

volumes:
  todo-pgdata:            # 复用第 5 章那个卷（若名字相同则复用，否则新建）
```

**第 4 步：一键启动**

在 `todo-app/` 目录下：

```bash
docker compose up -d --build
#   up      启动所有服务
#   -d      后台
#   --build 先构建有 build 的服务（backend、frontend）
```

✅ **预期输出**：会显示每个服务被创建（`Created` / `Started`），最后几行类似：
```
✔ Network todo-app_default  Created
✔ Container todo-app-db-1       Healthy
✔ Container todo-app-redis-1    Healthy
✔ Container todo-app-backend-1  Started
✔ Container todo-app-frontend-1 Started
```
注意容器名自动带了项目名前缀（目录名 `todo-app` + 服务名）：`todo-app-db-1`。

**第 5 步：逐项验证**

```bash
docker compose ps
#   预期：4 个服务都 Up，db 和 redis 的 STATUS 显示 (healthy)
```

```bash
curl http://localhost:3000/db
```
✅ **预期输出**：`{"db":"connected","now":"2026-...T..."}` —— **后端成功连上了 Postgres 容器！**（靠的是服务名 `db` 被解析成数据库容器）

```bash
curl http://localhost:3000/cache
```
✅ **预期输出**：`{"redis":"hello-from-redis"}` —— **后端成功连上了 Redis 容器！**

浏览器访问 <http://localhost:8080>：
✅ **预期输出**：看到第 4 章那个前端页面。

**第 6 步：感受 Compose 的威力**

```bash
docker compose down
#   一条命令，4 个容器 + 网络全部干净停掉删除（数据卷 todo-pgdata 保留）
docker compose up -d
#   再一条命令，全套瞬间回来（镜像和卷都还在，秒起）
curl http://localhost:3000/db    # 依然正常工作
```

> 🎯 **自检**：你能说清楚为什么后端里写 `DATABASE_URL` 用的主机名是 `db`（服务名）而不是某个 IP 吗？为什么 Compose 不需要我们手动 `docker network create`？（答：Compose 自动建网络并把所有服务接入，服务名自动成为网络内的可解析主机名。）

---

## ✅ 本章小结

- **Compose 用一个 YAML 声明整套服务**，一条 `docker compose up -d` 全起，一条 `down` 全停。
- 核心字段：`services` / `image` 或 `build` / `ports` / `environment` / `volumes` / `depends_on` / `healthcheck`。
- **服务名自动成为主机名** ★，容器间互访零配置；Compose 自动建网络，不用手动 `network create`。
- 常用命令：`up -d --build` / `down` / `logs -f` / `exec` / `ps`。（⚠️ 改 Dockerfile 后要 `--build`）
- ⚠️ **`depends_on` 只管启动顺序，不管服务就绪**；要真正"等就绪"必须配 `healthcheck` + `condition: service_healthy`。
- 敏感信息用 `.env` 文件，别硬编码，且 `.env` 不进 Git。
- **你的实战项目现在能一条命令拉起前端+后端+Postgres+Redis 了。**

下一章：把镜像分享出去，为部署做准备。👉 [08-镜像分发.md](./08-镜像分发.md)
