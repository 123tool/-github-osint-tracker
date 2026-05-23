#!/usr/bin/env python3
"""
Project Name: GitSint Pro V2
Author      : SPY-E | Indonesia OSINT
Description : High-performance, asynchronous open-source intelligence (OSINT) tool
              for tracking GitHub profiles, organizations, and linked emails.
"""

import asyncio
import sys
from colorama import Fore, Style
from tabulate import tabulate

from src.ui import Theme, show_banner, print_log
from src.utils import export_report
from src.core import GitHubAsyncCore
from src.modules.email_resolver import find_username_by_email, extract_hidden_email_from_commits
from src.modules.hunter import search_domain_via_hunter

# Konfigurasi Kredensial (Disarankan diisi menggunakan GitHub Personal Access Token)
# Kosongkan atau biarkan None jika ingin mencoba tanpa token (Akan terkena rate-limit jika berlebihan)
GITHUB_TOKEN = None
HUNTER_API_KEY = "TIDAK_ADA" # Ganti dengan API Key Hunter.io kamu jika ingin melacak struktur domain korporat

async def run_tracker_menu():
    engine = GitHubAsyncCore(token=GITHUB_TOKEN)
    
    while True:
        show_banner()
        print(f"{Theme.SECONDARY}[ PILIHAN MENU OPERASI INVESTIGASI ]")
        print(f"{Theme.PRIMARY}1. {Theme.TEXT}Lacak Informasi Akun Pengguna (Username Target)")
        print(f"{Theme.PRIMARY}2. {Theme.TEXT}Lacak Informasi Entitas Organisasi GitHub")
        print(f"{Theme.PRIMARY}3. {Theme.TEXT}Resolusi Email (Cari Akun Melalui Alamat Email)")
        print(f"{Theme.PRIMARY}4. {Theme.TEXT}Ubah Skema Tampilan (Toggle Dark / Light Mode)")
        print(f"{Theme.PRIMARY}5. {Theme.TEXT}Keluar dari GitSint Pro")
        print(f"{Theme.MUTED}------------------------------------------------------------")
        
        pilihan = input(f"{Theme.ACCENT}Masukkan Kode Operasi (1-5): {Style.RESET_ALL}").strip()
        
        if pilihan == "1":
            target = input(f"\n{Theme.ACCENT}Masukkan Username GitHub Target: {Style.RESET_ALL}").strip()
            if not target:
                print_log("Username tidak boleh kosong!", "error")
                await asyncio.sleep(2)
                continue
                
            print_log("Memulai penarikan data profil dan repositori...", "info")
            report = await engine.trace_target(target, is_org=False)
            
            if report and report != "RATE_LIMIT":
                # Cari email tersembunyi lewat forensik commit
                print_log("Memulai pemindaian log commit untuk mencari email tersembunyi...", "muted")
                hidden_emails = await extract_hidden_email_from_commits(target, token=GITHUB_TOKEN)
                report["Email Tersembunyi (Forensik Commit)"] = hidden_emails if hidden_emails else "Tidak Terdeteksi"
                
                # Tampilkan tabel ringkasan hasil intelijen
                print(f"\n{Theme.SUCCESS}[ INTEL REPORT FOR @{target} ]")
                table_data = [[f"{Theme.PRIMARY}{k}", f"{Theme.TEXT}{v}"] for k, v in report.items() if not isinstance(v, list)]
                print(tabulate(table_data, headers=[f"{Theme.SECONDARY}Key Metric", f"{Theme.SECONDARY}Value Data"], tablefmt="fancy_grid"))
                
                # Tampilkan data berbentuk list (Repositori dan Relasi)
                if report.get("Daftar Repositori"):
                    print(f"\n{Theme.SECONDARY}[ Sampel Repositori Terbaru ]")
                    for r in report["Daftar Repositori"]: print(f" {Theme.PRIMARY}• {Theme.TEXT}{r}")
                    
                if report.get("Email Tersembunyi (Forensik Commit)") and isinstance(report["Email Tersembunyi (Forensik Commit)"], list):
                    print(f"\n{Theme.ACCENT}[ Hasil Analisis Email Hasil Commit ]")
                    for em in report["Email Tersembunyi (Forensik Commit)"]: print(f" {Theme.PRIMARY}• {Theme.TEXT}{em}")
                
                # Ekspor Laporan
                await export_report(target, report)
                
            elif report == "RATE_LIMIT":
                print_log("Gagal mengeksekusi akibat pembatasan rate limit API GitHub.", "error")
                
            input(f"\n{Theme.MUTED}Tekan ENTER untuk kembali ke menu utama...")

        elif pilihan == "2":
            target_org = input(f"\n{Theme.ACCENT}Masukkan Nama Organisasi GitHub Target: {Style.RESET_ALL}").strip()
            if not target_org:
                print_log("Nama organisasi tidak boleh kosong!", "error")
                await asyncio.sleep(2)
                continue
                
            report = await engine.trace_target(target_org, is_org=True)
            if report and report != "RATE_LIMIT":
                # Cari domain via Hunter.io jika perusahaan tertera
                comp_domain = report.get("Afiliasi Perusahaan", "-").replace("@", "").strip()
                if "." in comp_domain:
                    print_log(f"Mendeteksi domain korporat '{comp_domain}'. Melakukan kueri Hunter.io...", "info")
                    hunter_res = await search_domain_via_hunter(comp_domain, HUNTER_API_KEY)
                    for k, v in hunter_res.items():
                        report[f"Hunter.io -> {k}"] = v
                
                print(f"\n{Theme.SUCCESS}[ INTEL REPORT FOR ORGANIZATION: {target_org} ]")
                table_data = [[f"{Theme.PRIMARY}{k}", f"{Theme.TEXT}{v}"] for k, v in report.items() if not isinstance(v, list)]
                print(tabulate(table_data, headers=[f"{Theme.SECONDARY}Metric", f"{Theme.SECONDARY}Value"], tablefmt="fancy_grid"))
                
                await export_report(f"org_{target_org}", report)
            input(f"\n{Theme.MUTED}Tekan ENTER untuk kembali...")

        elif pilihan == "3":
            email_query = input(f"\n{Theme.ACCENT}Masukkan Alamat Email Target: {Style.RESET_ALL}").strip()
            if "@" not in email_query:
                print_log("Format email tidak valid!", "error")
                await asyncio.sleep(2)
                continue
                
            print_log(f"Mencari kepemilikan akun untuk email: {email_query}", "info")
            matched_users = await find_username_by_email(email_query, token=GITHUB_TOKEN)
            
            if matched_users:
                print_log(f"Berhasil memetakan akun! Ditemukan {len(matched_users)} akun terhubung:", "success")
                for u in matched_users:
                    print(f" {Theme.SUCCESS}➔ {Theme.TEXT}Username: {Theme.SECONDARY}{u} {Theme.TEXT}(https://github.com/{u})")
            else:
                print_log("Tidak ada akun publik GitHub yang terikat dengan email tersebut.", "warning")
            input(f"\n{Theme.MUTED}Tekan ENTER untuk kembali...")

        elif pilihan == "4":
            print_log("Mengubah skema warna...", "muted")
            # Logika toggle mode, jika saat ini warna primernya hijau (dark) ubah ke biru (light)
            if Theme.PRIMARY == Fore.GREEN:
                Theme.set_light_mode()
                print_log("Berhasil berpindah ke MODE TERANG (Light Mode).", "success")
            else:
                # Mengembalikan instansiasi kelas ke struktur default (Dark)
                Theme.PRIMARY = Fore.GREEN
                Theme.SECONDARY = Fore.CYAN
                Theme.ACCENT = Fore.YELLOW
                Theme.TEXT = Fore.WHITE
                Theme.MUTED = Fore.BLACK + Style.BRIGHT
                Theme.ERROR = Fore.RED
                Theme.SUCCESS = Fore.GREEN + Style.BRIGHT
                print_log("Berhasil berpindah ke MODE GELAP (Dark Mode / Matrix Theme).", "success")
            await asyncio.sleep(2)

        elif pilihan == "5":
            print_log("Keluar dari GitSint Pro V2 Engine. Sampai jumpa di investigasi berikutnya!", "info")
            break
        else:
            print_log("Pilihan tidak valid, silakan ketik angka 1 sampai 5.", "warning")
            await asyncio.sleep(1.5)

def main():
    try:
        asyncio.run(run_tracker_menu())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Sesi dihentikan secara paksa oleh interupsi sistem (Ctrl+C).")
        sys.exit(0)

if __name__ == "__main__":
    main()
