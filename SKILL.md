---
name: mitmdump
description: Use when the user says "抓包", "抓取流量", "intercept HTTP", "需要抓某应用的包", "配置 mitmdump", or "mitmproxy 脚本". Captures HTTP/HTTPS traffic via mitmdump with Python scripts for AI-driven automation and analysis.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [network, http, capture, mitmproxy, traffic-analysis, proxy]
    related_skills: [api-data-scraping]
---

# mitmdump 抓包工具

## Overview

mitmdump 是 mitmproxy 项目的命令行版本，核心功能与 mitmproxy/mitmweb 相同，只是没有交互界面。本 skill 聚焦 `mitmdump` + Python 脚本的组合，特别适合 AI Agent 自动化场景——后台运行、脚本控制、日志记录全部可编程实现。

## When to Use

- 用户说"抓包"、"抓取流量"、"intercept HTTP"、"需要抓某应用的包"、"配置 mitmdump"、"mitmproxy 脚本"时使用
- 需要拦截特定域名的 HTTP 请求/响应并保存到文件时
- 需要在 AI 自动化流程中记录网络请求日志时
- 需要分析某个应用或网站的 API 调用时

**不要用于：**
- 实时调试（用 mitmproxy TUI 更合适）
- 需要图形界面操作（用 mitmweb）

## 核心三工具对比

| 工具 | 界面 | 适用场景 |
|------|------|----------|
| **mitmproxy** | 交互式终端 TUI | 手动调试、实时查看流量 |
| **mitmweb** | Web 界面 | 浏览器操作、远程访问 |
| **mitmdump** | 无 UI，命令行 | **AI 自动化、后台运行、脚本控制** |

## 快速启动

### 安装依赖

```bash
brew install mitmproxy
mitmdump --version
```

### 启动 mitmdump

```bash
# 基本启动（监听 8080 端口）
mitmdump

# 指定端口
mitmdump -p 9090

# 静默模式（TUI 不输出，避免 stdout 被吞）
mitmdump -q -p 9090

# 后台运行并指定脚本
mitmdump -q -p 9090 -s mitmdump/scripts/capture.py 2>&1 &
```

## macOS 系统代理配置

### 命令行配置

```bash
# 开启 HTTP/HTTPS 代理
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
# 临时代理单个命令
http_proxy=http://localhost:9090 curl https://example.com
https_proxy=http://localhost:9090 curl https://example.com

# curl 绕过代理访问本机
curl -x http://localhost:9090 --noproxy localhost,127.0.0.1 https://example.com
```

### CA 证书配置（首次）

mitmdump 生成 CA 证书到 `~/.mitmproxy/`。需要手动安装并信任：

1. 双击 `~/.mitmproxy/mitmproxy-ca-cert.pem`
2. Keychain Access 中找到 mitmproxy 证书
3. 展开"信任"，选"始终信任"

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
flow.request.pretty_url   # 带 host 的 URL
flow.request.path         # 路径
flow.request.headers       # 请求头 dict
flow.request.cookies       # Cookie dict
flow.request.text          # 请求体（字符串）
flow.request.content       # 请求体（bytes）
flow.request.pretty_host   # 主机名（去除端口）

# 响应
flow.response.status_code  # 200, 404 等
flow.response.headers     # 响应头
flow.response.text         # 响应体（字符串）
flow.response.content     # 响应体（bytes）

# 其他
flow.error                # 错误信息（如果有）
```

## 常用命令速查

```bash
# 启动抓包（静默模式）
mitmdump -q -p 9090 -s mitmdump/scripts/capture.py 2>&1

# 保存所有流量到文件
mitmdump -p 9090 -w output.mitm

# 读取文件并过滤（只保留 POST 请求）
mitmdump -nr input.mitm -w output.mitm "~m post"

# 读取文件并重放
mitmdump -nC input.mitm
```

## 仓库结构

```
mitmdump-skill/
├── README.md              # 项目说明
├── SKILL.md               # Hermes Agent 技能文档（本文件）
└── mitmdump/
    └── scripts/
        └── capture.py     # 抓包脚本模板
```

## Common Pitfalls

1. **脚本中的 print() 不生效** — TUI 模式下 print() 被吞掉。用文件写日志：
   ```python
   def log(msg):
       with open("/tmp/mitm.log", "a") as f:
           f.write(f"{msg}\n")
       print(msg)  # 同时输出到终端
   ```

2. **curl 请求卡住** — 脚本里某个钩子阻塞了事件循环。检查脚本是否有死循环或同步 I/O。

3. **HTTPS 抓不到** — CA 证书未安装或未信任。按上述 CA 配置步骤操作。

4. **代理导致 AI 通信中断** — 系统代理开启后本机所有流量走代理。解决方法：
   - 用环境变量临时代理，不用系统代理
   - 或用 `--noproxy` 排除 AI 服务域名

5. **必须用 `-q` 静默模式** — 否则 TUI 捕获所有输出，print/log 全部被吞，AI 看不到日志。

## Verification Checklist

- [ ] `brew install mitmproxy` 成功，`mitmdump --version` 有输出
- [ ] 启动命令使用 `-q` 静默模式，后台运行
- [ ] CA 证书已安装并信任（首次）
- [ ] `TARGET_HOSTS` 已修改为实际目标域名
- [ ] capture.py 中同时使用文件写日志，print 作为终端备份
- [ ] 系统代理配置后 AI 通信未中断（如有需要用 `--noproxy`）