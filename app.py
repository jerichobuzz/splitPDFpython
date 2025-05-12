from flask import Flask, request, jsonify
from PyPDF2 import PdfReader, PdfWriter
import base64
import io

app = Flask(__name__)

@app.before_request
def log_request_info():
    print("\n=== Incoming Request ===")
    print("Method:", request.method)
    print("Path:", request.path)
    print("Headers:", dict(request.headers))
    print("Form:", request.form)
    print("Files:", request.files)
    print("========================\n")

@app.route("/split", methods=["POST"])
def split_pdf():
    if 'file' not in request.files:
        print("❌ No file received")
        return "No file received", 400

    file = request.files['file']
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

@app.route("/", methods=["GET"])
def health():
    return "PDF Split API is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
