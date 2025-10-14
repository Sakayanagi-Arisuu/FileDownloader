from flask import Flask, render_template, request, jsonify
from downloader import DownloadManager
import threading

app = Flask(__name__)
manager = DownloadManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_download():
    url = request.json.get('url')
    threading.Thread(target=manager.start, args=(url,)).start()
    return jsonify({"status": "started"})

@app.route('/pause', methods=['POST'])
def pause_download():
    manager.pause()
    return jsonify({"status": "paused"})

@app.route('/resume', methods=['POST'])
def resume_download():
    manager.resume()
    return jsonify({"status": "resumed"})

@app.route('/stop', methods=['POST'])
def stop_download():
    manager.stop()
    return jsonify({"status": "stopped"})

@app.route('/progress', methods=['GET'])
def get_progress():
    return jsonify({"progress": manager.progress})

if __name__ == '__main__':
    app.run(debug=True)
