import concurrent.futures
import ipaddress
import subprocess
import geoip2.database
import os

IP_FILE = 'cf_ipv4.txt'                 # Cloudflare IPv4 列表
OUTPUT_FILE = 'results/top20.txt'       # 输出 top20 文件
DB_PATH = 'GeoLite2-Country.mmdb'       # 离线数据库
TOPN = 20
PING_TIMEOUT = 1.5                       # 秒
MAX_WORKERS = 100

def load_ips(file_path):
    ips = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                net = ipaddress.ip_network(line, strict=False)
                if isinstance(net.network_address, ipaddress.IPv4Address):
                    ips.extend([str(ip) for ip in net.hosts()])
            except ValueError:
                pass
    return ips

def ping(ip):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(int(PING_TIMEOUT * 1000)), ip],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if '平均' in line:
                    delay = line.split('平均 = ')[-1].replace('ms', '').strip()
                    return ip, float(delay)
        return ip, float('inf')
    except Exception:
        return ip, float('inf')

def get_country_info(ip, reader):
    try:
        response = reader.country(ip)
        country_name = response.country.names.get('zh-CN', '未知')
        code = response.country.iso_code or 'UN'
        flag = ''.join(chr(127397 + ord(c)) for c in code.upper()) if len(code) == 2 else '🏳️'
        return f"{country_name}{flag}"
    except Exception:
        return "未知🏳️"

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ 未找到 GeoLite2 数据库文件: {DB_PATH}")
        return
    if not os.path.exists(IP_FILE):
        print(f"❌ 未找到 IP 列表文件: {IP_FILE}")
        return

    print("🚀 正在加载 Cloudflare IPv4 列表...")
    ips = load_ips(IP_FILE)
    print(f"✅ 共加载 IPv4 地址 {len(ips)} 个")

    print("⚡ 开始测速中...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for ip, delay in executor.map(ping, ips):
            if delay != float('inf'):
                results.append((ip, delay))

    top_ips = sorted(results, key=lambda x: x[1])[:TOPN]

    print("🌍 正在识别国家信息...")
    reader = geoip2.database.Reader(DB_PATH)

    lines = []
    for ip, delay in top_ips:
        country_info = get_country_info(ip, reader)
        lines.append(f"{ip}#{country_info}#{delay:.1f}ms")

    reader.close()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"🏁 测速完成！结果已保存至 {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
