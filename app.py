import os
import sys
import uuid
import pathlib
import webview
import threading
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# Automatically targets your official Windows Downloads folder (e.g. C:\Users\jayden\Downloads)
DOWNLOAD_DIR = str(pathlib.Path.home() / "Downloads")

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

@app.route("/api/download", methods=["POST"])
def download_video():
    data = request.json or {}
    url = data.get("url")
    format_type = data.get("format", "mp4")
    
    if not url:
        return jsonify({"error": "Please enter a YouTube link"}), 400

    if format_type == "mp3":
        # Save directly using video title as filename
        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
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
        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == "mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"

        return jsonify({"status": "success", "filename": os.path.basename(filename)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_flask():
    app.run(host="127.0.0.1", port=5000)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    html_path = get_resource_path("index.html")
    
    window = webview.create_window(
        'YT Stream Master', 
        html_path, 
        width=1000, 
        height=750, 
        resizable=True
    )
    
    webview.start()