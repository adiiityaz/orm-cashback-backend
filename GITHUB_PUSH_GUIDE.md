# 🚀 GitHub Push Guide - Step by Step

## Prerequisites
- GitHub account created
- Git installed on your system

---

## Step-by-Step Instructions

### Step 1: Initialize Git Repository
```bash
git init
```

### Step 2: Configure Git (if not already done)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Add All Files
```bash
git add .
```

### Step 4: Create Initial Commit
```bash
git commit -m "Initial commit: ORM Cashback Platform Backend - Complete implementation with all phases"
```

### Step 5: Create GitHub Repository

**Option A: Using GitHub Website**
1. Go to https://github.com
2. Click the "+" icon in top right → "New repository"
3. Repository name: `orm-cashback-backend` (or your preferred name)
4. Description: "ORM Cashback & Review Platform - Django REST Framework Backend"
5. Choose: **Public** or **Private**
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

**Option B: Using GitHub CLI** (if installed)
```bash
gh repo create orm-cashback-backend --public --source=. --remote=origin --push
```

### Step 6: Add Remote Repository
```bash
git remote add origin https://github.com/YOUR_USERNAME/orm-cashback-backend.git
```
Replace `YOUR_USERNAME` with your GitHub username.

### Step 7: Rename Branch to Main (if needed)
```bash
git branch -M main
```

### Step 8: Push to GitHub
```bash
git push -u origin main
```

---

## Alternative: If Repository Already Exists

If you already created the repository on GitHub:

```bash
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

---

## What Gets Pushed

✅ **Included:**
- All source code
- Models, views, serializers
- Migrations
- Settings files
- Requirements.txt
- README.md
- API_DOCUMENTATION.md
- .gitignore
- .env.example

❌ **Excluded (via .gitignore):**
- venv/ (virtual environment)
- db.sqlite3 (database file)
- __pycache__/ (Python cache)
- .env (environment variables - sensitive!)
- *.pyc (compiled Python files)
- /media (uploaded files)
- /staticfiles (static files)

---

## After Pushing

### Verify on GitHub
1. Visit your repository: `https://github.com/YOUR_USERNAME/orm-cashback-backend`
2. Check that all files are there
3. Verify .env is NOT there (security!)

### Next Steps
1. Add repository description
2. Add topics/tags: `django`, `rest-api`, `jwt`, `postgresql`, `cashback-platform`
3. Create a LICENSE file (if needed)
4. Set up GitHub Actions for CI/CD (optional)
5. Add collaborators (if team project)

---

## Troubleshooting

### If push is rejected:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### If authentication fails:
- Use Personal Access Token instead of password
- Or use SSH keys

### To check remote:
```bash
git remote -v
```

### To remove remote (if wrong):
```bash
git remote remove origin
```

---

## Security Checklist Before Pushing

- [x] .env file is in .gitignore ✅
- [x] SECRET_KEY is not hardcoded (use .env) ✅
- [x] Database credentials not in code ✅
- [x] API keys not in code ✅
- [x] .env.example created (template only) ✅

---

## Quick Command Summary

```bash
# Initialize and push
git init
git add .
git commit -m "Initial commit: ORM Cashback Platform Backend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

