import httpx
from src.ui import print_log

async def search_domain_via_hunter(domain_name, api_key):
    """Melakukan tracking alamat email korporasi dan informasi struktur domain via Hunter.io."""
    if not api_key or api_key == "TIDAK_ADA":
        return {"Status": "Hunter.io API Key belum dikonfigurasi."}
        
    url = f"https://api.hunter.io/v2/domain-search?domain={domain_name}&api_key={api_key}"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            if res.status_code == 200:
                raw_data = res.json().get("data", {})
                return {
                    "Domain": raw_data.get("domain"),
                    "Organisasi/Perusahaan": raw_data.get("organization", "-"),
                    "Pola Email Populer": raw_data.get("pattern", "-"),
                    "Total Email Terdeteksi": len(raw_data.get("emails", [])),
                    "Daftar Email Korporat": [e.get("value") for e in raw_data.get("emails", [])][:5]
                }
            elif res.status_code == 401:
                return {"Status": "API Key Hunter.io tidak valid/expired."}
    except Exception as e:
        print_log(f"Koneksi Hunter.io terganggu: {e}", "error")
    return {"Status": "Gagal menarik data dari Hunter.io"}
