"""
Flask API Server for Document Scanner
Provides RESTful endpoints for document upload, processing, and retrieval
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import logging
from datetime import datetime
import os

from backend.document_processor import DocumentProcessor
from backend.config import API_CONFIG, UPLOAD_DIR, OUTPUT_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = API_CONFIG['max_upload_size']
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['OUTPUT_FOLDER'] = OUTPUT_DIR

# Initialize document processor
processor = DocumentProcessor()

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in API_CONFIG['allowed_extensions']


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload one or more files
    
    Returns:
        JSON with uploaded file information
    """
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400
    
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = UPLOAD_DIR / filename
            
            file.save(str(filepath))
            uploaded_files.append({
                "filename": filename,
                "filepath": str(filepath),
                "size": os.path.getsize(filepath)
            })
            logger.info(f"Uploaded: {filename}")
        else:
            logger.warning(f"Rejected file: {file.filename}")
    
    return jsonify({
        "success": True,
        "files": uploaded_files,
        "count": len(uploaded_files)
    })


@app.route('/api/process', methods=['POST'])
def process_documents():
    """
    Process uploaded documents with OCR
    
    Request JSON:
        {
            "files": ["filename1.jpg", "filename2.png"],
            "output_formats": ["json", "txt", "csv"]
        }
    
    Returns:
        JSON with processing results
    """
    data = request.get_json()
    
    if not data or 'files' not in data:
        return jsonify({"error": "No files specified"}), 400
    
    filenames = data['files']
    output_formats = data.get('output_formats', ['json', 'txt'])
    
    # Get full paths
    filepaths = [str(UPLOAD_DIR / f) for f in filenames]
    
    # Validate files exist
    missing_files = [f for f in filepaths if not Path(f).exists()]
    if missing_files:
        return jsonify({"error": f"Files not found: {missing_files}"}), 404
    
    try:
        # Process documents
        logger.info(f"Processing {len(filepaths)} documents...")
        results = processor.process_batch(filepaths, output_formats)
        
        return jsonify({
            "success": True,
            "results": results,
            "count": len(results),
            "statistics": processor.get_statistics()
        })
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/process/single', methods=['POST'])
def process_single_document():
    """
    Process a single document
    
    Request JSON:
        {
            "filename": "document.jpg",
            "output_formats": ["json", "txt"]
        }
    
    Returns:
        JSON with processing result
    """
    data = request.get_json()
    
    if not data or 'filename' not in data:
        return jsonify({"error": "No filename specified"}), 400
    
    filename = data['filename']
    output_formats = data.get('output_formats', ['json', 'txt'])
    
    filepath = UPLOAD_DIR / filename
    
    if not filepath.exists():
        return jsonify({"error": f"File not found: {filename}"}), 404
    
    try:
        # Process document
        logger.info(f"Processing: {filename}")
        result = processor.process_document(str(filepath), output_formats)
        
        return jsonify({
            "success": True,
            "result": result
        })
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search_documents():
    """
    Search processed documents
    
    Query params:
        q: Search query
    
    Returns:
        JSON with matching documents
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    results = processor.search_documents(query)
    
    return jsonify({
        "success": True,
        "query": query,
        "results": results,
        "count": len(results)
    })


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get processing statistics"""
    stats = processor.get_statistics()
    
    return jsonify({
        "success": True,
        "statistics": stats
    })


@app.route('/api/export/metadata', methods=['GET'])
def export_metadata():
    """Export all metadata to CSV"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"metadata_export_{timestamp}.csv"
        
        processor.export_all_metadata(str(output_path))
        
        return send_file(
            str(output_path),
            as_attachment=True,
            download_name=f"metadata_export_{timestamp}.csv"
        )
    
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download a processed file"""
    filepath = OUTPUT_DIR / filename
    
    if not filepath.exists():
        return jsonify({"error": f"File not found: {filename}"}), 404
    
    return send_file(
        str(filepath),
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/list/uploads', methods=['GET'])
def list_uploads():
    """List all uploaded files"""
    files = []
    for filepath in UPLOAD_DIR.glob('*'):
        if filepath.is_file():
            files.append({
                "filename": filepath.name,
                "size": filepath.stat().st_size,
                "uploaded_at": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            })
    
    return jsonify({
        "success": True,
        "files": files,
        "count": len(files)
    })


@app.route('/api/list/outputs', methods=['GET'])
def list_outputs():
    """List all output files"""
    files = []
    for filepath in OUTPUT_DIR.glob('*'):
        if filepath.is_file():
            files.append({
                "filename": filepath.name,
                "size": filepath.stat().st_size,
                "created_at": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            })
    
    return jsonify({
        "success": True,
        "files": files,
        "count": len(files)
    })


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        "error": "File too large",
        "max_size": API_CONFIG['max_upload_size']
    }), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    logger.info("Starting Document Scanner API Server...")
    logger.info(f"Upload directory: {UPLOAD_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )
