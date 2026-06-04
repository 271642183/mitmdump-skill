---
name: mitmdump
description: mitmdump 抓包工具。当用户说"抓包"、"抓取流量"、"intercept HTTP"、"需要抓某应用的包"、"配置 mitmdump"、"mitmproxy 脚本"时使用。
argument-hint: 提供要拦截的域名或应用名称
---

# mitmdump 抓包工具

mitmdump 是 mitmproxy 项目的命令行版本，核心与 mitmproxy/mitmweb 相同，只是没有交互界面。

## 核心三工具对比

| 工具 | 界面 | 适用场景 |
|------|------|----------|
| **mitmproxy** | 交互式终端 TUI | 手动调试、实时查看流量 |
| **mitmweb** | Web 界面 | 浏览器操作、远程访问 |
| **mitmdump** | 无 UI，命令行 | **AI 自动化、后台运行、脚本控制** |

## 快速启动

```bash
# 基本启动（监听 8080 端口）
mitmdump

# 指定端口
mitmdump -p 9090

# 静默模式（TUI 不输出，避免 stdout 被吞）
mitmdump -q -p 9090

# 后台运行并指定脚本
mitmdump -q -p 9090 -s capture.py 2>&1 &
```

## 关键：静默模式 `-q`

mitmdump 默认启动交互式 TUI，会捕获所有输出。**AI 自动化必须用 `-q` 静默**，否则脚本里的 `print()` 和 `ctx.log.info()` 全部被 TUI 吞掉，AI 看不到任何日志。

## 脚本编写

### 基本结构

```python
from mitmproxy import http, ctx

TARGET_HOSTS = ["example.com", "api.example.com"]

def response(flow: http.HTTPFlow):
    """响应拦截"""
    host = flow.request.pretty_host
    if not any(h in host for h in TARGET_HOSTS):
        return

    try:
        body = flow.response.text
        if body:
            # 保存到文件
            with open("/tmp/capture.json", "w") as f:
                f.write(body)
    except Exception as e:
        ctx.log.info(f"Error: {e}")

def request(flow: http.HTTPFlow):
    """请求拦截"""
    host = flow.request.pretty_host
    if not any(h in host for h in TARGET_HOSTS):
        return
    ctx.log.info(f"Request: {flow.request.method} {flow.request.path}")
```

### 事件钩子完整列表

| 钩子 | 触发时机 |
|------|----------|
| `http_connect(flow)` | 收到 HTTP CONNECT 请求 |
| `requestheaders(flow)` | 请求头读完（body 为空） |
| `request(flow)` | **完整请求已读** |
| `responseheaders(flow)` | 响应头读完（body 为空） |
| `response(flow)` | **完整响应已读** |
| `error(flow)` | HTTP 错误（连接中断等） |

> 每个 flow 会收到 `response` 或 `error`，不会两者都有。

### Flow 对象常用属性

```python
# 请求
flow.request.method        # "GET", "POST"
flow.request.url           # 完整 URL
flow.request.pretty_url    # 带 host 的 URL
flow.request.path          # 路径
flow.request.headers       # 请求头 dict
flow.request.cookies       # Cookie dict
flow.request.text          # 请求体（字符串）
flow.request.content       # 请求体（bytes）
flow.request.pretty_host   # 主机名（去除端口）

# 响应
flow.response.status_code  # 200, 404 等
flow.response.headers      # 响应头
flow.response.text         # 响应体（字符串）
flow.response.content      # 响应体（bytes）

# 其他
flow.error                 # 错误信息（如果有）
```

## macOS 系统代理配置

### 命令行

```bash
# 启用 HTTP/HTTPS 代理
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 9090
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 9090

# 关闭代理
sudo networksetup -setwebproxystate "Wi-Fi" off
sudo networksetup -setsecurewebproxystate "Wi-Fi" off

# 查看状态
networksetup -getwebproxy "Wi-Fi"
networksetup -getsecurewebproxy "Wi-Fi"
```

### 环境变量（临时，不影响系统）

```bash
# HTTP 代理
http_proxy=http://localhost:9090 curl https://example.com

# HTTPS 代理
https_proxy=http://localhost:9090 curl https://example.com
```

### 重要提醒

开启系统代理后，所有流量（包括 AI 通信）都会走代理。如果需要让本机 AI 通信绕过代理，在环境变量中排除：

```bash
# curl 绕过代理访问本机和直连 IP
curl -x http://localhost:9090 --noproxy localhost,127.0.0.1 https://example.com
```

## 常用命令速查

```bash
# 启动抓包
mitmdump -q -p 9090 -s script.py 2>&1

# 保存所有流量到文件
mitmdump -p 9090 -w output.mitm

# 读取文件并过滤（只保留 POST 请求）
mitmdump -nr input.mitm -w output.mitm "~m post"

# 读取文件并重放
mitmdump -nC input.mitm
```

## 常见问题

### 1. 脚本中的 print() 不生效

TUI 模式下 print() 被吞掉。用文件写日志：

```python
def log(msg):
    with open("/tmp/mitm.log", "a") as f:
        f.write(f"{msg}\n")
    print(msg)  # 同时输出到终端
```

### 2. curl 请求卡住

原因：脚本里某个钩子阻塞了事件循环。检查脚本是否有死循环或同步 I/O，改用异步或移到外部处理。

### 3. HTTPS 抓不到

mitmdump 生成 CA 证书到 `~/.mitmproxy/`。需要手动安装并信任：

1. 双击 `~/.mitmproxy/mitmproxy-ca-cert.pem`
2. Keychain Access 中找到 mitmproxy 证书
3. 展开"信任"，选"始终信任"

### 4. 代理导致 AI 通信中断

系统代理开启后本机所有流量走代理，AI 也会断。解决方法：

- 用环境变量临时代理，不用系统代理
- 或用 `--noproxy` 排除特定域名

## 依赖

- mitmproxy（通过 brew 安装：`brew install mitmproxy`）
- macOS 10.15+ / Linux

安装后 `mitmdump --version` 验证。

## 参考文档

- 官网: https://mitmproxy.org/
- 文档: https://docs.mitmproxy.org/
- GitHub: https://github.com/mitmproxy/mitmproxy