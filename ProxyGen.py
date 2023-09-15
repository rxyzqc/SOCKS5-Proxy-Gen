from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import hashlib
import time
import sys
import os

if os.name == "nt":
    os.system("title SOCKS5 Proxy Gen")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def get_country_code(ip_address):
    api_url = f"https://ipinfo.io/{ip_address}/json"

    response = requests.get(api_url)
    data = response.json()

    country_code = data.get("country")
    return country_code


def get_isp(ip_address):
    api_url = f"https://ipinfo.io/{ip_address}/json"

    response = requests.get(api_url)
    data = response.json()

    isp = data.get("org", "ISP information not available")
    return isp


def main():
    global MAX_WORKERS
    global MAX_LATENCY

    while True:
        clear()
        print("""
        1 - Check socks5 proxies listed sites from file
        2 - Check socks5 proxies url list from file
        3 - Check socks5 proxies listed site
        """)

        choice = int(input("Choice: "))
        if choice == 1:
            MAX_LATENCY = int(input("Max Latency (10-150): "))
            MAX_WORKERS = int(input("Workers (5-15): "))
            file = input("File: ")
            print("")
            check_sites_list(file)
            break
        elif choice == 2:
            MAX_LATENCY = int(input("Max Latency (10-150): "))
            MAX_WORKERS = int(input("Workers (5-15): "))
            file = input("File: ")
            print("")
            check_proxy_list(file)
            break
        elif choice == 3:
            MAX_LATENCY = int(input("Max Latency (10-150): "))
            MAX_WORKERS = int(input("Workers (5-15): "))
            site = input("Site: ")
            print("")
            check_proxy_list_from_site(site)
            break
        else:
            print("Invalid choice")
            time.sleep(1)
            clear()


def check_sites_list(file):
    with open(file, "r") as f:
        site_urls = f.readlines()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for site_url in site_urls:
            site_url = site_url.strip()
            proxy_list = get_proxy_list(site_url)
            if proxy_list:
                for proxy in proxy_list:
                    executor.submit(check_proxy, proxy)


def check_proxy_list(file):
    with open(file, "r") as f:
        proxy_urls = f.readlines()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for proxy_url in proxy_urls:
            proxy_url = proxy_url.strip()
            executor.submit(check_proxy, proxy_url)


def check_proxy_list_from_site(site_url):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        proxy_list = get_proxy_list(site_url)
        if proxy_list:
            for proxy in proxy_list:
                executor.submit(check_proxy, proxy)


def get_proxy_list(site_url):
    try:
        response = requests.get(site_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            proxy_list = [line.strip() for line in soup.get_text().split("\n") if line.strip()]
            return proxy_list
        else:
            print(f"\033[93m[?]\033[0m {site_url}")
            return []
    except requests.exceptions.RequestException:
        print(f"\033[93m[?]\033[0m {site_url}")
        return []


def check_proxy(proxy_url):
    try:
        ip = proxy_url.split(':')[0]
        output = os.popen(f'ping -n 4 {ip}').read()  # Ping the IP address 4 times
        if "Received = 4" in output:  # Check if all 4 packets were received
            latency_line = [line for line in output.split('\n') if 'Minimum' in line]
            if latency_line:
                latency = int(latency_line[0].split('=')[1].split('ms')[0])
                cc = get_country_code(proxy_url.split(':')[0])
                isp = get_isp(proxy_url.split(':')[0])
                if latency > MAX_LATENCY:
                    print(f"\033[33m[-]\033[0m {proxy_url} {latency}ms {cc}")
                else:
                    print(f"\033[32m[+]\033[0m {proxy_url} {latency}ms {cc}")
                    with open("valid_socks5.txt", "a") as valid_file:
                        if cc and isp:
                            if cc and isp is not None:
                                valid_file.write(f"{proxy_url} {cc} {isp}\n")
                            else:
                                valid_file.write(f"{proxy_url}\n")
                        else:
                            valid_file.write(f"{proxy_url}\n")
            else:
                print(f"\033[31m[-]\033[0m {proxy_url}")
        else:
            print(f"\033[31m[-]\033[0m {proxy_url}")
    except Exception as e:
        print(f"\033[31m[-]\033[0m {proxy_url} {e}")


while True:
    main()
    input("\nPress any key to continue . . .")
