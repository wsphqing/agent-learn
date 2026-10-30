# 第 6 章 · 容器间通信：Docker 网络

> 本章目标：搞懂容器怎么找到彼此、`-p` 端口映射的真相，让实战项目的后端能连上数据库和 Redis。

---

## 6.1 为什么需要网络

到目前，我们的容器都是"孤岛"：你在宿主机上用浏览器访问它，靠的是 `-p` 端口映射。但真实应用里，**容器之间要互相说话**：

- 后端容器要连数据库容器的 5432 端口。
- 后端容器要连 Redis 容器的 6379 端口。

问题来了：后端容器**怎么知道**数据库容器在哪？用 `localhost` 吗？不行——**每个容器都有自己的 `localhost`，指的是它自己**，不是数据库容器。

我们需要一个机制让容器能**按名字互相找到**。这就是 Docker 网络。

---

## 6.2 网络模式速览

Docker 给容器提供了几种网络模式，先混个脸熟（最常用的是 bridge）：

| 模式 | 一句话解释 | 用途 |
|------|-----------|------|
| **bridge**（默认） | 容器连到一个虚拟桥接网络，各自有内网 IP，可互相通信 | 默认，绝大多数场景 |
| **host** | 容器**直接共用宿主机的网络**，不再隔离 | 追求极致性能；但 macOS 上行为受限，少用 |
| **none** | 完全没有网络 | 完全隔离的离线任务 |
| **自定义 bridge** | 你自己建的 bridge 网络，**支持用容器名当域名** ★ | 多容器互通的推荐方式 |

⚠️ **关键区别**：Docker 默认那个 `bridge` 网络上的容器**只能通过 IP 互相通信，不能用容器名**。而**自定义的 bridge 网络，容器之间可以直接用"容器名"当域名互相访问**。所以实际项目中我们**总是自己建一个网络**。

---

## 6.3 自定义 bridge 网络 + 容器名当域名

这是本章最重要的机制。

> **同一个自定义网络里的容器，可以用【容器名】直接访问对方，Docker 内置的 DNS 会自动把容器名解析成对应容器的 IP。**

类比：默认网络像一个大广场，你只能靠"门牌号（IP）"找人，而且门牌号还会变；**自定义网络像一个微信群**，你只要喊昵称（容器名）就能 @ 到人，不用管他此刻在哪。

```bash
# 1. 创建一个自定义网络
docker network create todo-net
#   todo-net 是网络名

# 2. 把数据库容器接进这个网络
docker run -d --name todo-db --network todo-net \
  -e POSTGRES_PASSWORD=secret -v todo-pgdata:/var/lib/postgresql/data \
  postgres:16
#   --network todo-net 把这个容器加入自定义网络

# 3. 把后端容器也接进同一个网络
docker run -d --name todo-api --network todo-net -p 3000:3000 todo-backend:1.0
```

现在，**后端容器里可以用 `todo-db` 这个名字直接连数据库**：

```
在 todo-api 容器内部，连接字符串写：
postgres://postgres:secret@todo-db:5432/tododb
                            └──┬──┘
                          容器名就能当主机名用！
```

而如果用默认 bridge 网络，你就得先 `docker inspect` 查出数据库容器的 IP（还是动态变化的），写死在配置里——非常脆弱。

---

## 6.4 网络相关命令

```bash
docker network create todo-net        # ← 创建自定义网络
docker network ls                     # ← 列出所有网络（能看到默认的 bridge/host/none 和你的自定义网络）
docker network inspect todo-net       # ← 查看网络详情：哪些容器接入、各自的 IP 是多少
docker network connect todo-net xxx   # ← 把一个【已存在】的容器接入网络
docker network disconnect todo-net xxx# ← 断开会话
docker network rm todo-net            # ← 删除网络（无容器使用时可删）
```

`docker network inspect` 的输出很值得看，里面有 `Containers` 段，列出接入的容器名字和 IP：

```bash
docker network inspect todo-net
#   预期能看到 todo-db、todo-api 两个容器，以及它们的 IPv4Address
```

---

## 6.5 ⚠️ 端口映射再理解：`-p 8080:80` 谁是谁

这是新手最容易搞反的地方，务必钉牢：

```
       宿主机（你的 Mac）                    容器内部
   ┌────────────────────┐            ┌────────────────────┐
   │  localhost:8080    │  ────────▶ │      :80           │
   │  (你浏览器敲的)      │   DOCKER   │ (nginx 实际监听)    │
   └────────────────────┘   转发      └────────────────────┘
        -p 8080:80
        └─┬─┘ └┬┘
       宿主机  容器
       端口    端口
```

**格式永远是 `-p 宿主机端口:容器端口`**。

- **左边（8080）**：你在**宿主机**（Mac）上访问时用的端口，你从外面敲门敲的是这个。
- **右边（80）**：**容器内部**服务真正监听的端口，由镜像决定（nginx 是 80，node 应用看你代码里 `listen` 多少）。

**口诀**：**左边是"外面看到的口"，右边是"里面实际开的门"。** 里外可以相同（如 `3000:3000`）也可以不同。

> ⚠️ **注意**：端口映射是"从宿主机访问容器"用的。**容器之间互相访问不需要端口映射**——它们在同一个网络里，直接用容器名 + 容器内部端口通信即可。给数据库容器 `-p 5432:5432` 只是为了让你能用宿主机上的工具连它调试，容器之间连它根本不需要这行。

---

## 6.6 ⚠️ 常见坑

**坑 1：在容器里连 `localhost` 连不上数据库**
在容器内部，`localhost` 永远指**这个容器自己**。想连另一个容器，必须用**容器名**（在自定义网络里）或 IP。这是新手最常见的困惑。

**坑 2：容器想访问宿主机上的服务，怎么办？**
容器里 `localhost` 也访问不到宿主机。macOS/Windows 的 Docker Desktop 提供了一个特殊域名 **`host.docker.internal`**，在容器里用它就能指回宿主机：

```bash
# 假设宿主机上跑了个服务在 8000 端口，容器里这样访问：
curl http://host.docker.internal:8000
#   host.docker.internal 是 Docker Desktop 提供的"指回宿主机"的固定域名。
#   ⚠️ Linux 上默认没有这个，需要额外配置（--add-host=host.docker.internal:host-gateway）
```

**坑 3：容器不在同一个网络里，互相 ping 不通**
如果两个容器没接在同一个自定义网络，就用容器名找不到对方。**确保要通信的容器都 `--network` 到同一个网络。**

**坑 4：`localhost` vs `127.0.0.1` 在服务监听时的坑**
如果容器里的服务监听的是 `127.0.0.1`（只监听回环），那么**从容器外部（包括宿主机经端口映射）连不进来**。服务要监听 `0.0.0.0`（所有网卡）才能被外部访问。Node 里常见的是 `app.listen(PORT)` 默认监听 `0.0.0.0`，一般没事；但有些框架/配置默认监听 `127.0.0.1`，会导致端口映射后仍连不上。⚠️ **排查"端口映射了但连不上"时，先检查服务监听的是不是 `0.0.0.0`。**

---

## 6.7 🔨 跟着敲一遍：两个容器互相通信

目标：让一个容器**通过容器名**访问到另一个容器。

```bash
# 1. 建一个自定义网络
docker network create test-net

# 2. 在网络上起一个 redis 容器
docker run -d --name my-redis --network test-net redis:7-alpine

# 3. 在【同一个网络】上起一个临时容器，用它的命令行去连 redis
docker run --rm -it --network test-net redis:7-alpine \
  redis-cli -h my-redis ping
# 参数解释：
#   --rm              退出后自动删除这个临时容器（我们只是拿它当客户端用）
#   --network test-net 加入同一个自定义网络
#   redis-cli -h my-redis  redis 客户端，-h 指定主机为【容器名 my-redis】
#   ping               向 redis 发 ping 命令
```

✅ **预期输出**：打印 **`PONG`**。

这一个 `PONG` 证明了：**在自定义网络里，容器可以直接用容器名 `my-redis` 找到对方**。这就是第 7 章 Compose 编排的基础。

**对照实验（感受默认网络的差异）**：
```bash
# 不加 --network，用默认 bridge 网络再试一次：
docker run --rm -it redis:7-alpine redis-cli -h my-redis ping
#   预期：报错，类似 "Could not connect to Redis at my-redis:6379: Name or service not known"
#   —— 因为默认网络里不能用容器名解析，找不到 my-redis。
```

清理：
```bash
docker rm -f my-redis
docker network rm test-net
```

> 🎯 **自检**：为什么同一个 `redis-cli -h my-redis` 命令，在自定义网络里能通、在默认网络里报"名字解析不了"？（答：自定义网络有内置 DNS，能把容器名解析成 IP；默认 bridge 网络没有这个按名字解析的能力。）

---

## ✅ 本章小结

- 容器之间要通信，必须解决"如何按名字找到对方"的问题。
- **默认 bridge 网络不支持容器名解析**；**自定义 bridge 网络支持用容器名当域名** ★。所以实际项目总是自建网络。
- `docker network create/ls/inspect/connect` 是核心命令。
- **`-p 宿主机端口:容器端口`**，左边是外面敲门的口，右边是里面开的门。容器之间互相访问**不需要**端口映射。
- ⚠️ 坑：容器里 `localhost` 指容器自己；访问宿主机用 `host.docker.internal`（macOS）；服务要监听 `0.0.0.0` 才能被外部访问。

下一章是"爽点"：用一个文件、一条命令，同时拉起前端 + 后端 + 数据库。👉 [07-DockerCompose.md](./07-DockerCompose.md)
