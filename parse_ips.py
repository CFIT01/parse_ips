import requests
import sys

def get_cloud_ips():
    try:
        # 1. 获取数据
        g_url = "https://www.gstatic.com/ipranges/cloud.json"
        response = requests.get(g_url, timeout=30)
        
        # 如果 HTTP 状态码不是 200，直接报错
        response.raise_for_status() 
        
        g_data = response.json()
        # 提取 IPv4 列表
        g_ips = [item['ipv4Prefix'] for item in g_data['prefixes'] if 'ipv4Prefix' in item]

        # 2. 核心保护机制：阈值检查
        # 谷歌云全球 IP 段通常有几千个。如果少于 100 个，大概率是数据源出错了。
        if len(g_ips) < 100:
            print(f"CRITICAL ERROR: Only {len(g_ips)} IPs found. Data source might be broken.")
            sys.exit(1) # 以非零状态退出，中断 GitHub Actions

        # 3. 写入文件
        all_ips = sorted(list(set(g_ips)))
        with open("gcp_ranges.txt", "w") as f:
            f.write("\n".join(all_ips))
            
        print(f"Successfully parsed {len(all_ips)} IPs.")

    except Exception as e:
        print(f"ERROR during parsing: {e}")
        # 抛出错误以确保 GitHub Actions 标记为 Failure，且不会执行后续的 git push
        sys.exit(1) 

if __name__ == "__main__":
    get_cloud_ips()
