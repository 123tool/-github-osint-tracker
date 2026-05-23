# GitSint Pro V2 - Advanced Asynchronous GitHub OSINT Tool

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Asynchronous-HTTP%2F2-orange?style=flat-square" alt="Async">
  <img src="https://img.shields.io/badge/Niche-OSINT%20%7C%20Forensics-red?style=flat-square" alt="Niche">
  <img src="https://img.shields.io/badge/Branding-Indonesia%20OSINT-green?style=flat-square" alt="Branding">
</p>

**GitSint Pro V2** adalah instrumen intelijen bersumber terbuka (*Open Source Intelligence*) berbasis CLI (*Command Line Interface*) yang dirancang khusus untuk melakukan pelacakan, profiling mendalam, serta investigasi forensik digital pada ekosistem platform manajemen kode (GitHub & GitLab). 

Ditenagai oleh arsitektur **Asynchronous IO (`asyncio` + `httpx`)**, tool ini mampu mengekstrak puluhan parameter data intelijen secara paralel dalam hitungan detik tanpa memblokir performa *thread* utama sistem.

---

## 🎯 Fitur Unggulan

*   ⚡ **Fully Asynchronous Architecture**: Proses *scraping* data profil, organisasi, repositori, dan gists berjalan secara simultan memanfaatkan protokol HTTP/2 client.
*   🔍 **Commit History Email Forensics**: Mampu membongkar alamat email asli pengguna yang disembunyikan (*hidden email*) dari profil publik melalui analisis metadata pada log *PushEvent commit* terbaru.
*   📧 **Reverse Email Resolver**: Memetakan kepemilikan akun GitHub hanya berdasarkan masukan alamat email target.
*   🏢 **Corporate Domain Tracking**: Terintegrasi dengan **Hunter.io API** untuk memetakan struktur email, nama perusahaan, serta pola email korporat jika target terafiliasi dengan domain bisnis.
*   🦊 **Cross-Platform Presence Check**: Otomatis mendeteksi keberadaan akun duplikat dengan username yang sama di ekosistem **GitLab**.
*   🎨 **Dynamic Dual-Theme UI**: Mendukung pergantian skema tampilan antarmuka secara *real-time* antara **Mode Gelap (Matrix/Dark)** dan **Mode Terang (Light)** yang ramah terminal.
*   💾 **Automated Asset & Report Dump**: Otomatis mengunduh berkas gambar avatar target secara lokal serta mengekspor seluruh hasil investigasi ke dalam format laporan `.txt` yang rapi.

---

## Panduan Instalasi
​Prasyarat
​Sistem Anda harus sudah terpasang Python versi 3.9 atau yang lebih baru.
​Clone Repositori

    git clone [https://github.com/username-kamu/gitsint-pro.git](https://github.com/username-kamu/gitsint-pro.git)
    cd gitsint-pro
    ```
2.  **Instalasi Dependensi**
    Pasang pustaka pihak ketiga yang dibutuhkan menggunakan manajer paket `pip`:
```bash
    pip install -r requirements.txt
    ```
3.  **Konfigurasi Kredensial API (Opsional tapi Sangat Disarankan)**
    Untuk menghindari batasan batas permintaan (*rate-limit*) dari API publik GitHub (60 permintaan/jam naik menjadi 5.000 permintaan/jam), buka file `main.py` dan masukkan *Personal Access Token* (PAT) GitHub serta API Key Hunter.io Anda pada baris berikut:
```python
    GITHUB_TOKEN = "isi_token_github_anda_disini"
    HUNTER_API_KEY = "isi_api_key_hunter_io_disini"
    ```
4.  **Eksekusi Program**
    Jalankan perintah berikut untuk masuk ke menu interaktif GitSint Pro:
```bash
    python main.py
    ```
---
## 📊 Parameter Data yang Diekstrak

| Kategori Intelijen | Atribut Data |
| :--- | :--- |
| **Identitas Inti** | Login Username, Nama Resmi, Angka ID Internal, Deskripsi Biografi |
| **Geografis & Kontak** | Lokasi Fisik, Alamat Email Publik, Tautan Blog/Situs, Username X (Twitter) |
| **Forensik Lanjutan** | Email Tersembunyi (Via Log Commit), Riwayat Afiliasi Perusahaan |
| **Statistik & Jaringan** | Jumlah Repositori Publik, Jumlah Gists, Total Pengikut, Total Mengikuti |
| **Integrasi Eksternal** | Status Akun GitLab, Pola Email Korporat & Daftar Email Domain (Via Hunter.io) |

---
## 📜 Kebijakan Lisensi & Disclaimer
Alat ini dibuat murni untuk keperluan edukasi, riset keamanan siber, pengujian penetrasi, dan analisis data terbuka (*Open Source Intelligence*). Segala bentuk penyalahgunaan yang melanggar ketentuan layanan (*Terms of Service*) dari platform pihak ketiga (GitHub, GitLab, Meta, Hunter.io) sepenuhnya merupakan tanggung jawab pengguna akhir. Pengembang tidak bertanggung jawab atas pemblokiran kredensial atau tuntutan hukum apa pun yang timbul akibat penggunaan alat ini.
---
Developed with 💻 by **SPY-E | Indonesia OSINT**
