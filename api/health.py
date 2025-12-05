"""
Vercel Serverless Function - Health Check
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-vercel",
        "environment": "serverless"
    })

# Vercel serverless handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
