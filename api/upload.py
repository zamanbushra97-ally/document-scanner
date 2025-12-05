"""
Vercel Serverless Function - Upload Handler
Handles file uploads in serverless environment
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import base64

app = Flask(__name__)
CORS(app)

# Vercel uses /tmp for temporary storage
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload():
    """Handle file upload"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file and file.filename:
                # Save file to /tmp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{file.filename}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                
                file.save(filepath)
                
                # Convert to base64 for storage (since /tmp is ephemeral)
                with open(filepath, 'rb') as f:
                    file_data = base64.b64encode(f.read()).decode('utf-8')
                
                uploaded_files.append({
                    "filename": filename,
                    "size": os.path.getsize(filepath),
                    "data": file_data  # Store in response for client-side processing
                })
        
        return jsonify({
            "success": True,
            "files": uploaded_files,
            "count": len(uploaded_files)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel serverless handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
