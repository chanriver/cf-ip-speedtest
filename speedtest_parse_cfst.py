import geoip2.database
import os

DB_PATH = 'GeoLite2-Country.mmdb'
RAW_FILE = 'results/cfst_raw.txt'
OUTPUT_FILE = 'results/top20.txt'
TOPN = 20

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
        print(f"❌ 未找到 GeoLite2 数据库: {DB_PATH}")
        return

    if not os.path.exists(RAW_FILE):
        print(f"❌ 未找到 CloudflareSpeedTest 输出文件: {RAW_FILE}")
        return

    reader = geoip2.database.Reader(DB_PATH)

    lines = []
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # 假设输出格式: IP 延迟(ms) ...
            parts = line.split()
            ip = parts[0]
            try:
                delay = float(parts[1])
            except:
                continue
            lines.append((ip, delay))

    # 按延迟排序，取前20
    top20 = sorted(lines, key=lambda x: x[1])[:TOPN]

    out_lines = []
    for ip, delay in top20:
        country_info = get_country_info(ip, reader)
        out_lines.append(f"{ip}#{country_info}#{delay:.1f}ms")

    reader.close()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))

    print(f"🏁 top20.txt 已生成: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
