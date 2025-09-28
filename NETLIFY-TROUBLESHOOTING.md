# 🔧 NETLIFY DEPLOYMENT TROUBLESHOOTING

## 📋 **COMMON ISSUES & SOLUTIONS**

### **❌ Issue 1: Build Failed**
**Symptoms:** Deploy shows "Deploy failed" or "Build failed"

**Solutions:**
```bash
# Check if build works locally first
cd brain-ui
npm install
npm run build

# If local build fails, fix dependencies
npm audit fix
npm install --legacy-peer-deps
```

**Common build errors:**
- **Node version**: Change to Node 18 in site settings
- **Missing dependencies**: Check package.json
- **Memory issues**: Large bundle size

---

### **❌ Issue 2: 404 on All Pages**
**Symptoms:** Site loads but shows "Page not found" 

**Solutions:**
1. **Check netlify.toml redirect rules:**
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. **Verify build output:**
- brain-ui/dist/index.html exists
- brain-ui/dist/assets/ folder exists

---

### **❌ Issue 3: Site Loads but Content Missing**
**Symptoms:** Blank page or missing brain data

**Solutions:**
1. **Check browser console (F12)** for errors
2. **Verify brain data:**
```
brain-ui/public/brain/ folder should contain:
├── ACTIVE_TASKS.json
├── SESSION_CONTEXT.md  
├── SCOPE.md
└── other .brain files
```

3. **Rebuild with updated data:**
```powershell
# Copy latest brain data
Copy-Item -Recurse ".brain\*" "brain-ui\public\brain\" -Force

# Rebuild
cd brain-ui
npm run build
```

---

### **❌ Issue 4: Incorrect Build Settings**
**Symptoms:** Deploy succeeds but wrong files served

**Check these settings in Netlify:**
```
Base directory: brain-ui
Build command: npm run build  
Publish directory: brain-ui/dist
```

**NOT:**
- Base directory: (empty)
- Publish directory: dist (without brain-ui/)

---

### **❌ Issue 5: Domain/DNS Issues**  
**Symptoms:** Custom domain not working

**Solutions:**
1. **Use Netlify URL first:** https://your-site-name.netlify.app
2. **Check DNS propagation:** https://dnschecker.org
3. **Verify CNAME record** in Cloudflare

---

## 🧪 **DEBUG STEPS**

### **Step 1: Test Local Build**
```powershell
cd brain-ui
npm run build
npm run preview
# Should work at http://localhost:4173
```

### **Step 2: Check Deployed Files**
In Netlify dashboard:
1. Site overview → "Browse deploys"
2. Click latest deploy
3. "Browse deploy files"
4. Verify index.html and assets/ exist

### **Step 3: Test Different URLs**
```
Main site: https://your-site.netlify.app/
Direct index: https://your-site.netlify.app/index.html
Assets: https://your-site.netlify.app/assets/
Brain data: https://your-site.netlify.app/brain/ACTIVE_TASKS.json
```

---

## 📞 **TELL ME THE SPECIFICS**

**To help you better, please share:**

1. **What exact error** do you see?
   - [ ] "Site not found" 
   - [ ] "Deploy failed"
   - [ ] "Page not found" 
   - [ ] Blank page
   - [ ] Other: ___________

2. **What's the Netlify URL?** 
   - https://____________.netlify.app

3. **Build status in dashboard:**
   - [ ] Published (green)
   - [ ] Failed (red) 
   - [ ] Building (yellow)

4. **Any error messages** in browser console (F12)?

---

## 🚀 **QUICK FIXES TO TRY**

### **Fix 1: Force Rebuild**
In Netlify dashboard:
1. Deploys tab
2. "Trigger deploy" → "Deploy site"

### **Fix 2: Clear Build Cache**  
In site settings:
1. Build & deploy
2. Environment → Clear build cache
3. Trigger new deploy

### **Fix 3: Check File Case Sensitivity**
Make sure file names match exactly:
- index.html (not Index.html)
- assets/ folder exists
- brain/ folder in public/

---

**🔍 Share the specific error and I'll give you the exact solution!**