import requests
import json

URL_IPV4 = 'https://www.cloudflare.com/ips-v4'

def fetch_ipv4():
    r = requests.get(URL_IPV4, timeout=15)
    r.raise_for_status()
    lines = [l.strip() for l in r.text.splitlines() if l.strip()]
    return lines

if __name__ == '__main__':
    ips = fetch_ipv4()
    with open('cf_ipv4.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(ips))
    print(f'✅ Saved {len(ips)} IPv4 CIDR blocks to cf_ipv4.txt')
