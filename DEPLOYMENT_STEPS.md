# Git Setup and Deployment Commands

## Quick Setup Script

Run these commands in order to set up Git and deploy to Vercel:

### 1. Initialize Git Repository

```powershell
cd d:\SCANNER

# Initialize git
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit: Document Scanner with Vercel support"
```

### 2. Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `document-scanner`
3. Description: `AI-powered document OCR scanner with Vercel deployment`
4. Choose Public or Private
5. **Do NOT** check "Initialize with README"
6. Click "Create repository"

### 3. Push to GitHub

```powershell
# Add your GitHub repository as remote
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/document-scanner.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 4. Deploy to Vercel

#### Option A: Via Vercel Dashboard (Easiest)

1. Go to: https://vercel.com/dashboard
2. Click "Add New Project"
3. Click "Import Git Repository"
4. Select your `document-scanner` repository
5. Click "Import"
6. Click "Deploy"

#### Option B: Via Vercel CLI

```powershell
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

### 5. Verify Deployment

Your app will be live at: `https://document-scanner-[random].vercel.app`

Test it by:
1. Opening the URL
2. Uploading a test document
3. Processing with OCR

## Updating Your Deployment

Whenever you make changes:

```powershell
# Stage changes
git add .

# Commit with message
git commit -m "Your change description"

# Push to GitHub
git push

# Vercel will automatically redeploy!
```

## Troubleshooting

### If git command not found:
Install Git from: https://git-scm.com/download/win

### If npm command not found:
Install Node.js from: https://nodejs.org/

### If push is rejected:
```powershell
git pull origin main --rebase
git push
```

## Environment Variables (if needed)

Add in Vercel Dashboard → Settings → Environment Variables:
- `OCR_API_KEY` (if using external OCR service)
- Any other API keys

## Custom Domain

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your domain
3. Update DNS records as instructed

---

**Ready to deploy!** 🚀
