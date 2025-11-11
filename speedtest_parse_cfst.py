#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import geoip2.database

# 配置路径
CFST_RAW_FILE = "results/cfst_raw.txt"
TOP20_FILE = "results/top20.txt"
GEO_DB_FILE = "GeoLite2-Country.mmdb"

# Emoji 国旗转换函数
def country_code_to_emoji(code):
    if not code or code == "--":
        return "🏳️"
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)

# 读取 cfst 原始结果
if not os.path.exists(CFST_RAW_FILE):
    print(f"[Error] 文件不存在: {CFST_RAW_FILE}")
    exit(1)

with open(CFST_RAW_FILE, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# 解析 IP 和延迟（只保留 IPv4 且测速成功的行）
ip_speed_list = []
pattern = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}).*?(\d+(?:\.\d+)?)\s*ms")

for line in lines:
    match = pattern.search(line)
    if match:
        ip = match.group(1)
        speed = float(match.group(2))
        ip_speed_list.append((ip, speed))

if not ip_speed_list:
    print("[Warning] 没有解析到有效的 IPv4 测速数据")
    open(TOP20_FILE, "w", encoding="utf-8").close()
    exit(0)

# 按速度排序（升序，越快越好）
ip_speed_list.sort(key=lambda x: x[1])
top20 = ip_speed_list[:20]

# 打开 GeoLite2 数据库
if not os.path.exists(GEO_DB_FILE):
    print(f"[Error] GeoLite2 数据库不存在: {GEO_DB_FILE}")
    exit(1)

reader = geoip2.database.Reader(GEO_DB_FILE)

# 生成 top20.txt
with open(TOP20_FILE, "w", encoding="utf-8") as f:
    for ip, speed in top20:
        try:
            response = reader.country(ip)
            country_cn = response.country.names.get("zh-CN", response.country.name or "--")
            flag = country_code_to_emoji(response.country.iso_code)
        except Exception:
            country_cn = "--"
            flag = "🏳️"
        f.write(f"{ip}#{country_cn}{flag}\n")

print(f"[Success] top20.txt 已生成，共 {len(top20)} 个 IP")

reader.close()
