# Deploying to Vercel via GitHub

This guide will help you deploy the Document Scanner application to Vercel using GitHub.

## Prerequisites

1. **GitHub Account**: Sign up at https://github.com
2. **Vercel Account**: Sign up at https://vercel.com (can use GitHub login)
3. **Git installed**: Download from https://git-scm.com

## Step 1: Prepare Your Repository

### Initialize Git Repository

```bash
cd d:\SCANNER

# Initialize git
git init

# Create .gitignore
echo "uploads/
output/
__pycache__/
*.pyc
.env
node_modules/" > .gitignore

# Add all files
git add .

# Commit
git commit -m "Initial commit: Document Scanner application"
```

### Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `document-scanner`
3. Description: `AI-powered document OCR scanner`
4. Keep it **Public** or **Private** (your choice)
5. **Do NOT** initialize with README (we already have one)
6. Click "Create repository"

### Push to GitHub

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/document-scanner.git

# Push code
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel**: https://vercel.com/dashboard
2. **Click "Add New Project"**
3. **Import Git Repository**:
   - Select your GitHub account
   - Find `document-scanner` repository
   - Click "Import"

4. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as is)
   - **Build Command**: Leave empty
   - **Output Directory**: `frontend`
   - **Install Command**: `pip install -r requirements-vercel.txt`

5. **Environment Variables** (Optional):
   - Add any API keys if needed
   - For now, leave empty

6. **Click "Deploy"**

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name? document-scanner
# - Directory? ./
# - Override settings? No

# Deploy to production
vercel --prod
```

## Step 3: Configure Tesseract (Important!)

⚠️ **Note**: Vercel's serverless functions have limitations. Tesseract OCR may not work out-of-the-box on Vercel due to binary dependencies.

### Recommended Solutions:

#### Option 1: Use OCR.space API (Free Tier Available)

1. Sign up at https://ocr.space/ocrapi
2. Get free API key (25,000 requests/month)
3. Update `api/process.py` to use their API instead of local Tesseract

#### Option 2: Use Google Cloud Vision API

1. Create Google Cloud account
2. Enable Vision API
3. Get API credentials
4. Update code to use Cloud Vision

#### Option 3: Hybrid Approach (Recommended)

- Deploy frontend to Vercel
- Keep backend on a separate service:
  - **Railway.app** (free tier available)
  - **Render.com** (free tier available)
  - **Heroku** (paid)

## Step 4: Verify Deployment

Once deployed, Vercel will provide a URL like:
```
https://document-scanner-xyz.vercel.app
```

1. **Open the URL**
2. **Test file upload**
3. **Check if OCR processing works**

## Troubleshooting

### Issue: "Tesseract not found"

**Solution**: Use OCR API service (see Option 1 above)

### Issue: "Function timeout"

**Solution**: 
- Reduce image size before processing
- Use lighter OCR models
- Increase timeout in `vercel.json` (max 60s on free tier)

### Issue: "Out of memory"

**Solution**:
- Process smaller images
- Reduce batch size
- Upgrade Vercel plan for more memory

## Alternative: Full Local Backend + Vercel Frontend

If you want to keep the full OCR capabilities:

1. **Deploy frontend only to Vercel**
2. **Run backend locally or on another service**
3. **Update API_BASE in `frontend/app.js`**:

```javascript
const API_BASE = 'https://your-backend-url.com/api';
```

## Updating Your Deployment

Whenever you make changes:

```bash
# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub
git push

# Vercel will automatically redeploy!
```

## Custom Domain (Optional)

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## Environment Variables

If you add API keys or secrets:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add variables:
   - `OCR_API_KEY`
   - `DATABASE_URL`
   - etc.

## Cost Considerations

**Vercel Free Tier Includes**:
- 100 GB bandwidth
- Serverless function executions
- Automatic HTTPS
- Continuous deployment

**Limitations**:
- 10-second function timeout (Hobby)
- 1024 MB function memory
- No persistent storage

For production use with heavy OCR processing, consider:
- Vercel Pro ($20/month) - 60s timeout, 3008 MB memory
- Or use separate backend service

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Test functionality
3. ⚠️ Set up OCR API if Tesseract doesn't work
4. 🎨 Customize domain
5. 📊 Monitor usage in Vercel dashboard

---

**Need Help?**
- Vercel Docs: https://vercel.com/docs
- Vercel Discord: https://vercel.com/discord
- GitHub Issues: Create an issue in your repository
