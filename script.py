#!/usr/bin/env python3
import requests
import curl_cffi import request
import re
import datetime
import time
import urllib3
import sys
import json
import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG = {
    "NIM": "",
    "PASS": "",
    "KELAS": "",
    "URL_BASE": "https://sisak1.polsri.ac.id/mahasiswa",
    "TIMEOUT": 30,
    "RETRIES": 3
}

class SisakBot:
    def __init__(self):
        self.session = requests.Session(impersonate="chrome110")
        self.session.headers.update(self._get_headers())
        self.urls = self._get_urls()

    @staticmethod
    def _get_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f"{CONFIG['URL_BASE']}/site/login",
            'Origin': 'https://sisak1.polsri.ac.id'
        }

    @staticmethod
    def _get_urls():
        base = CONFIG['URL_BASE']
        return {
            "login": f"{base}/site/login",
            "presensi": f"{base}/akademik/presensi",
            "jadwal": f"{base}/akademik/presensi/json_jadwal_mahasiswa",
            "act_absen": f"{base}/akademik/presensi/ajax_simpan_presensi",
            "act_capaian": f"{base}/akademik/presensi/ajax_simpan_capaian"
        }

    def _req(self, method, url, **kwargs):
        for i in range(CONFIG['RETRIES']):
            try:
                kwargs['verify'] = False
                kwargs['timeout'] = CONFIG['TIMEOUT']
                if method.upper() == 'GET':
                    return self.session.get(url, **kwargs)
                return self.session.post(url, **kwargs)
            except requests.RequestException:
                print(f"[!] Connection error ({i+1}/{CONFIG['RETRIES']}). Retrying...")
                time.sleep(2)
        return None

    def login(self):
        print("[*] Authenticating...")
        try:
            self.session.cookies.clear()
            resp = self._req('GET', self.urls['login'])
            if not resp:
                return False

            csrf = re.search(r'name="csrf_has_name" value="([^"]+)"', resp.text)
            if not csrf:
                print("[!] Failed to extract CSRF token.")
                return False

            payload = {
                'username': CONFIG['NIM'],
                'password': CONFIG['PASS'],
                'csrf_has_name': csrf.group(1)
            }
            resp = self._req('POST', self.urls['login'], data=payload)

            if resp and ("/beranda" in resp.url or "Logout" in resp.text):
                print(f"[+] Login success: {CONFIG['NIM']}")
                return True

            print("[!] Login failed. Check credentials.")
            return False

        except Exception as e:
            print(f"[!] Login exception: {e}")
            return False

    def get_token(self):
        resp = self._req('GET', self.urls['presensi'])
        if resp:
            match = re.search(r"'csrf_has_name':\s*'([a-f0-9]+)'", resp.text)
            return match.group(1) if match else None
        return None

    def run_job(self, target_date, is_retry=False):
        print(f"\n[*] Processing: {target_date}")
        token = self.get_token()
        
        if not token:
            if not is_retry:
                print("[!] Session invalid. Attempting re-login...")
                if self.login(): return self.run_job(target_date, is_retry=True)
            print(f"[X] Skipped {target_date}: Cannot get token.")
            return

        payload = {'csrf_has_name': token, 'kelas': CONFIG['KELAS'], 'tanggal': target_date}
        resp = self._req('POST', self.urls['jadwal'], data=payload)
        
        try:
            data = resp.json()
        except (json.JSONDecodeError, AttributeError):
            if not is_retry:
                print(f"[!] Session expired during job. Re-authenticating...")
                if self.login(): return self.run_job(target_date, is_retry=True)
            print("[X] Failed to parse schedule data.")
            return

        if not data:
            print(f"[-] No schedule found for {target_date}.")
            return

        count = 0
        for day in data:
            if 'jadwal' not in day: continue
            for item in day['jadwal']:
                self._process_item(item, token)
                count += 1
        
        if count == 0:
            print("[-] Schedule is empty (Holiday/Free).")
        else:
            print(f"[+] Done. Processed {count} subjects.")

    def _process_item(self, item, token):
        name = item.get('nama_mtk', 'Unknown')
        pid = item['id_pre']

        print(f"    > {name}")

        if not item.get('kkpresensi'):
            print("      [+] Marking Presence: HADIR")
            self._req('POST', self.urls['act_absen'], data={
                'csrf_has_name': token, 'id_pre': pid, 'status': 'H'
            })
        else:
            print(f"      [.] Already marked: {item['kkpresensi']}")

        if not item.get('capaian'):
            print("      [+] Marking Achievement: SESUAI")
            self._req('POST', self.urls['act_capaian'], data={
                'csrf_has_name': token, 'id_pre': pid, 'capaian': 'Y'
            })
        else:
            print(f"      [.] Achievement filled.")

        time.sleep(1)

def parse_dates(date_input):
    today = datetime.date.today()
    if not date_input:
        return [today.strftime('%Y-%m-%d')]

    try:
        if ":" in date_input:
            start_s, end_s = date_input.split(":")
            start = datetime.datetime.strptime(start_s.strip(), '%Y-%m-%d').date()
            end = datetime.datetime.strptime(end_s.strip(), '%Y-%m-%d').date()
            delta = (end - start).days
            if delta < 0:
                return []
            return [(start + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta + 1)]
        else:
            datetime.datetime.strptime(date_input.strip(), '%Y-%m-%d')
            return [date_input.strip()]
    except ValueError:
        return []

def main():
    _print_banner()

    try:
        _get_credentials()
        if not all([CONFIG['NIM'], CONFIG['PASS'], CONFIG['KELAS']]):
            print("[!] Credentials missing.")
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)

    bot = SisakBot()
    if not bot.login():
        sys.exit(1)

    _print_date_help()

    try:
        user_in = input(" Target Date > ").strip()
    except KeyboardInterrupt:
        sys.exit(0)

    dates = parse_dates(user_in)
    if not dates:
        print("[!] Invalid date format. Use YYYY-MM-DD.")
        sys.exit(1)

    print(f"[*] Queue: {len(dates)} days.")

    try:
        for d in dates:
            bot.run_job(d)
            if d != dates[-1]:
                time.sleep(1.5)
    except KeyboardInterrupt:
        print("\n[!] Job cancelled by user.")
        sys.exit(0)


def _print_banner():
    print(r"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       ██████╗  ██████╗ ██╗     ███████╗██████╗ ██╗        ║
║       ██╔══██╗██╔═══██╗██║     ██╔════╝██╔══██╗██║        ║
║       ██████╔╝██║   ██║██║     ███████╗██████╔╝██║        ║
║       ██╔═══╝ ██║   ██║██║     ╚════██║██╔══██╗██║        ║
║       ██║     ╚██████╔╝███████╗███████║██║  ██║██║        ║
║       ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝        ║
║                                                           ║
║        ╔═╗╦ ╦╔╦╗╔═╗╔╦╗╔═╗╔╦╗╦╔═╗╔╗╔  ╔╦╗╔═╗╔═╗╦           ║
║        ╠═╣║ ║ ║ ║ ║║║║╠═╣ ║ ║║ ║║║║   ║ ║ ║║ ║║           ║
║        ╩ ╩╚═╝ ╩ ╚═╝╩ ╩╩ ╩ ╩ ╩╚═╝╝╚╝   ╩ ╚═╝╚═╝╩═╝         ║
║                       by Foxe                             ║
╚═══════════════════════════════════════════════════════════╝
    """)


def _get_credentials():
    if not CONFIG['NIM']:
        CONFIG['NIM'] = input(" NIM   : ").strip()
    if not CONFIG['PASS']:
        CONFIG['PASS'] = getpass.getpass(" PASS  : ").strip()
    if not CONFIG['KELAS']:
        CONFIG['KELAS'] = input(" KELAS : ").strip().upper()


def _print_date_help():
    print("-" * 50)
    print(" [?] INPUT FORMAT EXAMPLES:")
    print("     1. Today       : (Press Enter)")
    print("     2. Single Date : 2025-12-20")
    print("     3. Date Range  : 2025-12-20:2025-12-25")
    print("-" * 50)

if __name__ == "__main__":
    main()
