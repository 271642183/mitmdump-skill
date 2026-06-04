#!/usr/bin/env python3
"""
mitmdump 抓包脚本模板
用法: mitmdump -q -p 9090 -s capture.py

修改 TARGET_HOSTS 和 SAVE_DIR 后使用。
"""
import datetime
from pathlib import Path

SAVE_DIR = Path.home() / "Desktop" / "hermes workspace" / "mitm_capture"
LOG_FILE = SAVE_DIR / "capture.log"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# 要拦截的域名，支持多个
TARGET_HOSTS = ["example.com", "api.example.com"]

def log(msg):
    """同时写文件和终端"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def request(flow):
    """请求发出前"""
    host = flow.request.pretty_host
    if not any(h in host for h in TARGET_HOSTS):
        return
    log(f"REQUEST {flow.request.method} {host}{flow.request.path}")

def response(flow):
    """响应收到后"""
    host = flow.request.pretty_host
    if not any(h in host for h in TARGET_HOSTS):
        return
    try:
        body = flow.response.text
        if body:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            out_file = SAVE_DIR / "responses" / f"{ts}.json"
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(body)
            size = len(body)
            log(f"SAVED {host}{flow.request.path} -> {out_file.name} ({size} bytes)")
    except Exception as e:
        log(f"ERROR: {e}")