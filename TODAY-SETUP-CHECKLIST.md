# 📋 TODO LIST - Làm trước khi có router access

## ✅ **COMPLETED**
- [x] Check network environment (Public IP: 27.69.244.249, Local IP: 192.168.1.122)
- [x] DNS configuration (brain.xemgiadat.com, webhook.xemgiadat.com, api.xemgiadat.com)
- [x] DNS propagation test (all working)

## 🔄 **CAN DO NOW (Without Router Access)**

### **1. Windows Firewall Setup** ⚙️
```powershell
# Run PowerShell as Administrator
.\step2-firewall.ps1
```
**What it does:**
- Creates firewall rules for ports 80, 443, 8080, 3000, 8000
- Adds Windows Defender exclusions
- Prepares Windows for incoming connections

### **2. Nginx Proxy Installation** 🌐
```powershell  
.\step3-nginx.ps1
```
**What it does:**
- Downloads nginx for Windows
- Creates configuration for subdomain routing
- Tests configuration validity

### **3. Application Dependencies** 📦
```powershell
# Check Python environment
python --version
pip list

# Check Node.js for Brain UI
node --version
npm --version

# Install missing packages if needed
pip install fastapi uvicorn
```

### **4. Create Webhook Secret** 🔐
```powershell
# Generate secure webhook secret
$secret = [System.Web.Security.Membership]::GeneratePassword(32, 5)
Write-Host "Webhook Secret: $secret"

# Save to environment
$env:WEBHOOK_SECRET = $secret
```

### **5. Test Services Locally** 🧪
```powershell
# Terminal 1: Test webhook
uvicorn webhook_listener:app --host 127.0.0.1 --port 8080 --reload

# Terminal 2: Test main API  
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 3: Test brain UI
cd brain-ui
npm run dev -- --host 127.0.0.1 --port 3000
```

## 📅 **FOR TOMORROW (With Router Access)**

### **Router Port Forwarding Setup**
- Access router admin panel
- Configure port forwarding rules
- Test external access from phone 4G

### **Final Integration Test**
- Test all external URLs
- Setup GitHub webhook
- Verify brain system sync

---

## 🎯 **Let's Start with Windows Setup!**

**Ready to run firewall setup?** (Need Administrator PowerShell)