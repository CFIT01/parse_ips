import requests
import sys
import os

def get_wechat_ips():
    # 0. 从环境变量中读取密钥（由 GitHub Actions 注入）
    corp_id = os.environ.get("CORP_ID")
    corp_secret = os.environ.get("CORP_SECRET")
    
    if not corp_id or not corp_secret:
        print("CRITICAL ERROR: CORP_ID or CORP_SECRET environment variables are missing.")
        sys.exit(1)

    try:
        # 1. 获取 Access Token
        token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
        tok_response = requests.get(token_url, timeout=30)
        tok_response.raise_for_status() 
        tok_data = tok_response.json()
        
        if tok_data.get("errcode") != 0:
            print(f"CRITICAL ERROR: Failed to get access token. WeChat API Error: {tok_data}")
            sys.exit(1)
            
        access_token = tok_data.get("access_token")

        # 2. 获取数据
        w_url = f"https://qyapi.weixin.qq.com/cgi-bin/getcallbackip?access_token={access_token}"
        response = requests.get(w_url, timeout=30)
        response.raise_for_status() 
        
        w_data = response.json()
        if w_data.get("errcode") != 0:
            print(f"CRITICAL ERROR: Failed to get IP list. WeChat API Error: {w_data}")
            sys.exit(1)
            
        raw_ips = w_data.get("ip_list", [])

        # 3. 核心保护机制：阈值检查
        # 企业微信回调 IP 正常情况下有上百个。如果少于 3 个，大概率是数据源或权限出错了。
        if len(raw_ips) < 3:
            print(f"CRITICAL ERROR: Only {len(raw_ips)} WeChat IPs found. Data source might be broken.")
            sys.exit(1)

        # 4. 格式化转换（通配符转为 CIDR）
        cidr_ips = []
        for ip in raw_ips:
            if "*" in ip:
                cidr_ips.append(ip.replace("*", "0/24"))
            else:
                cidr_ips.append(ip)

        # 5. 写入文件
        all_ips = sorted(list(set(cidr_ips)))
        with open("wechat_ranges.txt", "w") as f:
            f.write("\n".join(all_ips))
            
        print(f"Successfully parsed {len(all_ips)} WeChat IPs.")

    except Exception as e:
        print(f"ERROR during parsing WeChat IPs: {e}")
        sys.exit(1) 

if __name__ == "__main__":
    get_wechat_ips()
