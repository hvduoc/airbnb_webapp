# 🚀 NETLIFY + GITHUB SETUP - Brain UI Auto-Deploy

## ✅ **Prerequisites READY**
- [x] Brain UI built successfully (`brain-ui/dist/`)
- [x] Project pushed to GitHub (`hvduoc/airbnb_webapp`)
- [x] Brain data integrated in `brain-ui/public/brain/`

---

## 🌐 **STEP 1: Netlify Dashboard Setup**

### **1.1 Create Netlify Account**
- Go to: **https://app.netlify.com**
- Sign up with GitHub account (recommended)
- Click "Authorize Netlify"

### **1.2 Create New Site**
- Click **"New site from Git"** 
- Choose **"GitHub"** as Git provider
- **Authorize** Netlify to access your repositories

### **1.3 Repository Selection**
- Search and select: **`hvduoc/airbnb_webapp`**
- Branch to deploy: **`feature/opex-sprint1`** (or your current branch)

---

## ⚙️ **STEP 2: Build Configuration**

### **2.1 Site Settings**
```
Site name: brain-xemgiadat (or your choice)
Branch: feature/opex-sprint1
Base directory: brain-ui
Build command: npm run build
Publish directory: brain-ui/dist
```

### **2.2 Environment Variables (Optional)**
```
NODE_VERSION: 18
NPM_VERSION: latest
```

---

## 🔧 **STEP 3: Deploy Configuration File**

Create `netlify.toml` in your project root:

```powershell
# Create netlify.toml for better control
```