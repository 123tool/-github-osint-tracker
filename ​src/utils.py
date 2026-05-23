import os
import aiofiles
import httpx
from src.ui import print_log

async def download_avatar(avatar_url, username):
    """Mengunduh gambar avatar secara asinkron dan menyimpannya ke direktori lokal."""
    if not avatar_url:
        return None
    
    folder = "downloaded_avatars"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{username}_avatar.jpg")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(avatar_url, timeout=15)
            if response.status_code == 200:
                async with aiofiles.open(file_path, mode='wb') as f:
                    await f.write(response.content)
                print_log(f"Avatar berhasil diunduh secara lokal ke: {file_path}", "success")
                return file_path
    except Exception as e:
        print_log(f"Gagal mengunduh avatar secara asinkron: {e}", "error")
    return None

async def export_report(target_name, data):
    """Mengekspor dictionary data hasil pelacakan ke file teks rapi."""
    folder = "reports"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{target_name}_osint_report.txt")
    
    try:
        async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
            await f.write(f"=== GITSINT PRO OSINT AUTOMATION REPORT ===\n")
            await f.write(f"Target Identifier: {target_name}\n")
            await f.write("-" * 50 + "\n")
            for key, value in data.items():
                if isinstance(value, list):
                    await f.write(f"{key}:\n")
                    for item in value:
                        await f.write(f"  - {item}\n")
                else:
                    await f.write(f"{key}: {value}\n")
        print_log(f"Laporan investigasi berhasil diekspor ke: {file_path}", "success")
    except Exception as e:
        print_log(f"Gagal mengekspor laporan: {e}", "error")
