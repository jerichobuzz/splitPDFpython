import sys
import os
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader, PdfWriter
import base64
import io

# === Force unbuffered output for Render logs ===
sys.stdout = sys.stderr = open('/dev/stdout', 'w')
os.environ['PYTHONUNBUFFERED'] = '1'

# === Flask app setup ===
app = Flask(__name__)

@app.before_request
def log_request_info():
    print("\n=== Incoming Request ===")
    print("Method:", request.method)
    print("Path:", request.path)
    print("Headers:", dict(request.headers))
    print("Form keys:", list(request.form.keys()))
    print("Files keys:", list(request.files.keys()))
    print("========================\n")

@app.route("/split", methods=["POST"])
def split_pdf():
    try:
        if 'data' not in request.files or request.files['data'].filename == '':
            print("❌ No file received. Received fields:", request.files)
            return "No file received", 400

        file = request.files['data']
        print(f"✅ Received file: {file.filename}")

        reader = PdfReader(file)
        total_pages = len(reader.pages)
        chunks = []

        for i in range(0, total_pages, 25):
            writer = PdfWriter()
            for j in range(i, min(i + 25, total_pages)):
                writer.add_page(reader.pages[j])

            stream = io.BytesIO()
            writer.write(stream)
            stream.seek(0)

            chunks.append({
                "fileName": f"chunk_{i // 25 + 1}.pdf",
                "data": base64.b64encode(stream.read()).decode('utf-8')
            })

        print(f"✅ Returning {len(chunks)} chunks")
        return jsonify({ "chunks": chunks })

    except Exception as e:
        print("❌ Exception occurred:", str(e))
        return "Server Error: " + str(e), 500

@app.route("/", methods=["GET"])
def health():
    return "PDF Split API is running"
