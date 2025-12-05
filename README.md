# Document Scanner - AI-Powered OCR Solution

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/document-scanner)

A comprehensive document digitization solution that uses multi-engine OCR technology to extract text from handwritten and printed documents.

## 🚀 Features

- **Multi-Engine OCR**: Tesseract, EasyOCR, and PaddleOCR
- **Intelligent Processing**: Auto document type detection
- **Metadata Extraction**: Dates, names, emails, phone numbers
- **Modern Web UI**: Drag-and-drop interface with real-time processing
- **Multiple Export Formats**: JSON, CSV, TXT

## 📦 Quick Deploy

### Deploy to Vercel (Recommended)

1. Click the "Deploy with Vercel" button above
2. Connect your GitHub account
3. Deploy!

**Note**: For full OCR capabilities, see [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run server
python backend/api_server.py

# Open browser
http://localhost:5000
```

## 📖 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Vercel Deployment](VERCEL_DEPLOYMENT.md)
- [Full Documentation](README.md)
- [Walkthrough](walkthrough.md)

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **OCR**: Tesseract, EasyOCR, PaddleOCR
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Vercel Serverless Functions

## 📝 License

Created for VIR Softech's digitization solution suite.

## 🤝 Contributing

Contributions welcome! Please read the contributing guidelines first.

## 📧 Support

For issues or questions, please open a GitHub issue.

---

**Powered by Multi-Engine OCR Technology** 🚀
