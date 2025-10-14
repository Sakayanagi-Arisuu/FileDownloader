import requests
import time

class DownloadManager:
    def __init__(self):
        self.is_paused = False
        self.is_stopped = False
        self.progress = 0

    def start(self, url):
        self.is_paused = False
        self.is_stopped = False
        self.progress = 0

        local_filename = url.split("/")[-1]
        with requests.get(url, stream=True) as r:
            total = int(r.headers.get('content-length', 0))
            downloaded = 0

            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if self.is_stopped:
                        break

                    while self.is_paused:
                        time.sleep(0.3)

                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.progress = int((downloaded / total) * 100)

        if self.is_stopped:
            self.progress = 0

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def stop(self):
        self.is_stopped = True
