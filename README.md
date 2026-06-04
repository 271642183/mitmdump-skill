# mitmdump Skill

本仓库是 mitmdump 抓包技能，用于拦截和分析 HTTP/HTTPS 流量。

## 原工具：mitmproxy

**mitmproxy** 由 [@mitmproxy](https://github.com/mitmproxy) 组织开发和维护，核心作者包括 Aldo Cortesi（@cortesi）等，采用 MIT License。

- **官网**: https://mitmproxy.org/
- **GitHub**: https://github.com/mitmproxy/mitmproxy
- **文档**: https://docs.mitmproxy.org/

mitmproxy 是一套交互式 HTTPS 代理工具集，包含三个组件：

| 组件 | 界面 | 适用场景 |
|------|------|----------|
| **mitmproxy** | 交互式终端 TUI | 手动调试、实时查看流量 |
| **mitmweb** | Web 界面 | 浏览器操作、远程访问 |
| **mitmdump** | 无 UI，命令行 | **AI 自动化、后台运行、脚本控制** |

本 skill 聚焦 `mitmdump` + Python 脚本的组合。

## 安装依赖

```bash
brew install mitmproxy
```

验证：

```bash
mitmdump --version
```

## 快速开始

### 1. 启动 mitmdump

```bash
# 静默模式后台运行
mitmdump -q -p 9090 -s mitmdump/scripts/capture.py 2>&1 &
```

### 2. 配置系统代理（macOS）

```bash
# 开启
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 9090
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 9090

# 关闭
sudo networksetup -setwebproxystate "Wi-Fi" off
sudo networksetup -setsecurewebproxystate "Wi-Fi" off
```

### 3. 配置 CA 证书（首次）

首次使用需要信任 mitmproxy 的 CA 证书：

1. 双击 `~/.mitmproxy/mitmproxy-ca-cert.pem`
2. 在 Keychain Access 中找到 mitmproxy 证书
3. 展开"信任"，选"始终信任"

### 4. 修改 capture.py

将 `TARGET_HOSTS` 改为你想拦截的域名即可：

```python
TARGET_HOSTS = ["example.com", "api.example.com"]
```

## 仓库结构

```
mitmdump-skill/
├── README.md              # 本文件
├── SKILL.md               # Hermes Agent 技能文档（完整技术细节）
└── mitmdump/
    └── scripts/
        └── capture.py     # 抓包脚本模板
```

## 核心要点

1. **必须用 `-q` 静默模式**：否则 TUI 会吞掉所有 print/log 输出，AI 无法看到日志
2. **系统代理会影响 AI 通信**：配置代理时注意用 `--noproxy` 排除 AI 服务域名
3. **脚本中用文件写日志**：print 在静默模式直接到终端，但最好同时写文件确保记录

## 相关链接

- [mitmproxy GitHub](https://github.com/mitmproxy/mitmproxy)
- [mitmproxy 文档](https://docs.mitmproxy.org/)