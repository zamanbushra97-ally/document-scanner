# Vercel Deployment - Static Frontend Only

This deployment serves only the static frontend. The backend with OCR functionality should be run locally or deployed separately.

## Live URL
Your frontend is deployed at: https://document-scanner-[your-id].vercel.app

## To Use the Application

### Option 1: Local Backend (Recommended)
1. Run the backend locally:
   ```bash
   python backend/api_server.py
   ```
2. Open http://localhost:5000 in your browser
3. Full OCR functionality will work!

### Option 2: Deploy Backend to Railway (Cloud Solution)

If you want a fully cloud-hosted solution:

1. **Sign up for Railway**: https://railway.app
2. **Create New Project** → **Deploy from GitHub**
3. **Select** your `document-scanner` repository
4. **Add these settings**:
   - Root Directory: `/`
   - Start Command: `python backend/api_server.py`
5. **Add environment variable**:
   - `PORT`: 5000
6. **Deploy!**

Railway will give you a URL like: `https://document-scanner.railway.app`

Then update `frontend/app.js` line 4:
```javascript
const API_BASE = 'https://document-scanner.railway.app/api';
```

## Current Status

✅ **Frontend**: Deployed on Vercel (UI only)
⚠️ **Backend**: Not deployed (Python serverless functions don't work easily on Vercel)

## Recommended Architecture

- **Frontend**: Vercel (current) ✅
- **Backend**: Railway.app or local ✅
- **Database**: Not needed for basic OCR

This separation is actually better for:
- Easier debugging
- Better performance
- No serverless limitations
- Full OCR engine support
