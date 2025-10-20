import requests
import os
from .utils import safe_filename

def download_file_from_url(url: str, dst_folder: str) -> str:
    """
    Download a file from URL into dst_folder.
    Returns the saved filename (not full path).
    Raises exceptions on error.
    """
    os.makedirs(dst_folder, exist_ok=True)

    # Lấy tên file từ URL
    url_path = url.split('?')[0].rstrip('/')
    candidate = url_path.split('/')[-1] or 'downloaded_file'
    filename = safe_filename(candidate)

    # Thử lấy tên file từ header nếu có
    try:
        head = requests.head(url, allow_redirects=True, timeout=10)
        ct = head.headers.get('content-disposition')
        if ct and 'filename=' in ct:
            fname = ct.split('filename=')[-1].strip(' "')
            filename = safe_filename(fname)

        # Thêm phần mở rộng dựa vào content-type nếu thiếu
        if '.' not in filename:
            content_type = head.headers.get('content-type', '')
            if 'pdf' in content_type:
                filename += '.pdf'
            elif 'html' in content_type:
                filename += '.html'
            elif 'plain' in content_type:
                filename += '.txt'
    except Exception as e:
        print(f"[WARN] HEAD request failed: {e}")

    dst_path = os.path.join(dst_folder, filename)

    # Nếu file trùng, thêm hậu tố
    base, ext = os.path.splitext(filename)
    i = 1
    while os.path.exists(dst_path):
        filename = f"{base}_{i}{ext}"
        dst_path = os.path.join(dst_folder, filename)
        i += 1

    # Tải file
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dst_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"[OK] File downloaded: {dst_path}")
        return filename
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        raise e
