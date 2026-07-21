import os
import pathlib
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, static_folder='.')
CORS(app)

DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route("/api/download", methods=["POST"])
def download_video():
    data = request.json or {}
    url = data.get("url")
    format_type = data.get("format", "mp4")
    
    if not url:
        return jsonify({"error": "Please enter a YouTube link"}), 400

    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    if format_type == "mp3":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == "mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"

        base_name = os.path.basename(filename)
        return jsonify({"status": "success", "filename": base_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/get-file/<filename>", methods=["GET"])
def get_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)