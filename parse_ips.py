import requests

def get_cloud_ips():
    # 获取 Google Cloud IPv4 前缀
    g_url = "https://www.gstatic.com/ipranges/cloud.json"
    g_data = requests.get(g_url).json()
    g_ips = [item['ipv4Prefix'] for item in g_data['prefixes'] if 'ipv4Prefix' in item]

    # 合并并去重
    all_ips = sorted(list(set(g_ips)))

    with open("gcp_ranges.txt", "w") as f:
        f.write("\n".join(all_ips))

if __name__ == "__main__":
    get_cloud_ips()
