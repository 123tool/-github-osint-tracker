import asyncio
import httpx
from src.ui import Theme, print_log
from src.utils import download_avatar

class GitHubAsyncCore:
    def __init__(self, token=None):
        """
        Inisialisasi core engine. 
        Menggunakan Personal Access Token (PAT) GitHub sangat direkomendasikan 
        agar terhindar dari pembatasan rate-limit (60 req/jam ke 5000 req/jam).
        """
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitSint-Pro/V2 (Indonesia OSINT; SPY-E Engine)"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    async def fetch_endpoint(self, client, url):
        """Helper asinkron untuk mengambil data mentah JSON dari endpoint API."""
        try:
            response = await client.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            elif response.status_code == 403:
                print_log("Rate limit GitHub tercapai atau akses ditolak!", "error")
                return "RATE_LIMIT"
        except Exception as e:
            print_log(f"Koneksi timeout/gagal ke {url}: {e}", "error")
        return None

    async def check_gitlab_presence(self, username):
        """Mengecek apakah username yang sama aktif di ekosistem GitLab."""
        url = f"https://gitlab.com/api/v4/users?username={username}"
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=10)
                if res.status_code == 200 and res.json():
                    return f"Aktif (https://gitlab.com/{username})"
        except Exception:
            pass
        return "Tidak Ditemukan"

    async def trace_target(self, identifier, is_org=False):
        """Melakukan investigasi penuh secara asinkron pada objek target."""
        base_url = "https://api.github.com"
        path = f"orgs/{identifier}" if is_org else f"users/{identifier}"
        
        async with httpx.AsyncClient(http2=True) as client:
            print_log(f"Memulai pemindaian asinkron pada entitas: {identifier}", "info")
            
            # Tarik data profil utama terlebih dahulu
            profile_data = await self.fetch_endpoint(client, f"{base_url}/{path}")
            
            if not profile_data:
                print_log("Target tidak ditemukan di database GitHub.", "error")
                return None
            if profile_data == "RATE_LIMIT":
                return "RATE_LIMIT"

            # Jika target valid, lakukan scraping endpoint sekunder secara paralel (Simultaneous Scraping)
            tasks = {
                "repos": self.fetch_endpoint(client, profile_data.get("repos_url", "")),
                "orgs": self.fetch_endpoint(client, profile_data.get("organizations_url", "")) if not is_org else asyncio.sleep(0, result=[]),
                "gists": self.fetch_endpoint(client, f"{base_url}/{path}/gists"),
                "followers_list": self.fetch_endpoint(client, profile_data.get("followers_url", "")) if not is_org else asyncio.sleep(0, result=[]),
                "following_list": self.fetch_endpoint(client, f"{base_url}/users/{identifier}/following") if not is_org else asyncio.sleep(0, result=[]),
                "gitlab": self.check_gitlab_presence(identifier)
            }
            
            # Jalankan semua task secara asinkron berbarengan
            results = await asyncio.gather(*tasks.values())
            resolved_tasks = dict(zip(tasks.keys(), results))

            # Proses Kompilasi Hasil Intelijen
            extracted_report = {
                "Login/ID": profile_data.get("login"),
                "Nama Resmi": profile_data.get("name", "-"),
                "Email Publik": profile_data.get("email", "-"),
                "Internal ID": profile_data.get("id"),
                "Biografi": profile_data.get("bio", "-"),
                "Lokasi Geografis": profile_data.get("location", "-"),
                "Avatar URL": profile_data.get("avatar_url"),
                "Total Followers": profile_data.get("followers", 0) if not is_org else "N/A",
                "Total Following": profile_data.get("following", 0) if not is_org else "N/A",
                "Total Repositori": profile_data.get("public_repos", 0),
                "Total Gists": profile_data.get("public_gists", 0),
                "Tanggal Dibuat": profile_data.get("created_at"),
                "Akun X/Twitter": profile_data.get("twitter_username", "-"),
                "Situs Blog/Web": profile_data.get("blog", "-"),
                "Afiliasi Perusahaan": profile_data.get("company", "-"),
                "Status GitLab": resolved_tasks.get("gitlab"),
            }

            # Ekstrak nama-nama repositori teratas
            repos = resolved_tasks.get("repos")
            extracted_report["Daftar Repositori"] = [r.get("name") for r in repos][:10] if isinstance(repos, list) else []
            
            # Ekstrak nama organisasi yang diikuti (jika target adalah user)
            orgs = resolved_tasks.get("orgs")
            extracted_report["Organisasi Terikat"] = [o.get("login") for o in orgs] if isinstance(orgs, list) else []

            # Ekstrak sampel teman terdekat/interaksi (diambil dari followers)
            f_list = resolved_tasks.get("followers_list")
            extracted_report["Sampel Teman/Followers"] = [f.get("login") for f in f_list][:10] if isinstance(f_list, list) else []

            # Otomatisasi pengunduhan avatar target secara lokal
            if extracted_report["Avatar URL"]:
                print_log("Mengunduh aset gambar avatar secara asinkron...", "muted")
                local_path = await download_avatar(extracted_report["Avatar URL"], extracted_report["Login/ID"])
                extracted_report["Penyimpanan Avatar Lokal"] = local_path if local_path else "Gagal mengunduh"

            return extracted_report
