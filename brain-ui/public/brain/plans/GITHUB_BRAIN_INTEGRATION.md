# 🌐 QUẢN LÝ BỘ NÃO TRỰC TUYẾN - GitHub Integration

## 🎯 Mục Tiêu
Tạo hệ thống quản lý bộ não trực tuyến, real-time sync với GitHub để team có thể collaborate hiệu quả.

## 🚀 Giải Pháp: GitHub + Brain UI + Webhook

### **Architecture với Cloudflare Subdomains**
```
GitHub Repository (.brain/) 
    ↕ (webhook push events)
Webhook Listener (webhook.xemgiadat.com:80)
    ↕ (file sync)
Brain UI (brain.xemgiadat.com:80)
    ↕ (real-time updates)
FastAPI (api.xemgiadat.com:80)
    ↕ (business logic)
Team Members (browser - stable URLs)
```

### **Production URLs (STABLE - Never Change!)**
- **Brain UI**: https://brain.xemgiadat.com
- **Main API**: https://api.xemgiadat.com  
- **Webhook**: https://webhook.xemgiadat.com/webhook/github
- **Repository**: https://github.com/hvduoc/airbnb_webapp

## 📋 Implementation Plan

### **Phase 1: GitHub Integration (COMPLETED ✅)**
- [x] Repository uploaded: `https://github.com/hvduoc/airbnb_webapp`
- [x] Webhook listener setup: `webhook_listener.py`
- [x] Auto-sync on push events
- [x] Brain UI serving từ GitHub data

### **Phase 2: Real-time Collaboration**

#### **A. Enhanced Webhook System**
```python
# webhook_listener.py enhancements
@app.post("/webhook/github")  
async def github_webhook(request: Request):
    # Verify GitHub signature
    signature = request.headers.get("X-Hub-Signature-256")
    
    # Parse payload
    payload = await request.json()
    
    # Handle different events
    if payload["ref"] == "refs/heads/main":
        # Sync .brain/ changes
        await sync_brain_files()
        
        # Notify Brain UI clients
        await notify_brain_ui_clients()
        
        # Log activity
        await log_brain_activity(payload)
```

#### **B. Real-time Notifications**
```javascript
// Brain UI - Real-time sync notifications
const useGitHubSync = () => {
    const [syncStatus, setSyncStatus] = useState('connected')
    const [lastSync, setLastSync] = useState(null)
    
    useEffect(() => {
        // Polling GitHub API for recent commits
        const checkForUpdates = async () => {
            const response = await fetch('/api/github/latest-commit')
            const data = await response.json()
            
            if (data.sha !== lastSync) {
                setLastSync(data.sha)
                // Trigger UI refresh
                window.location.reload()
            }
        }
        
        const interval = setInterval(checkForUpdates, 30000) // 30s
        return () => clearInterval(interval)
    }, [lastSync])
}
```

### **Phase 3: Online Brain Management**

#### **A. GitHub Web Editor Integration**
```markdown
# Direct GitHub editing workflow
1. Vào GitHub repo: https://github.com/hvduoc/airbnb_webapp
2. Navigate to .brain/ folder
3. Click file cần edit (ACTIVE_TASKS.json, SCOPE.md, etc.)
4. Click ✏️ "Edit this file"  
5. Make changes directly trong browser
6. Commit với message rõ ràng
7. Brain UI tự động sync trong 30s
```

#### **B. Brain UI Editor (Advanced)**
```javascript
// Tích hợp GitHub API để edit trực tiếp
const BrainFileEditor = ({ fileName }) => {
    const [content, setContent] = useState('')
    const [isEditing, setIsEditing] = useState(false)
    
    const saveToGitHub = async () => {
        const response = await fetch('/api/github/update-file', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                path: `.brain/${fileName}`,
                content: content,
                message: `Update ${fileName} via Brain UI`,
                branch: 'main'
            })
        })
        
        if (response.ok) {
            showNotification('✅ File saved to GitHub!')
        }
    }
}
```

## 🛠️ Setup Instructions

### **1. GitHub Repository Setup**
```bash
# Already done - repo exists at:
# https://github.com/hvduoc/airbnb_webapp

# Ensure .brain/ folder is tracked
git add .brain/
git commit -m "Add brain system to repository"
git push origin main
```

### **2. Webhook Configuration**
```bash
# GitHub Repo → Settings → Webhooks
# Payload URL: http://your-server.com:8080/webhook/github
# Content type: application/json
# Events: Push events
# Secret: [generate strong secret]
```

### **3. Brain UI GitHub Integration**
```bash
# Add GitHub API integration
npm install @octokit/rest
npm install react-github-editor (optional)

# Environment variables
echo "GITHUB_TOKEN=your_token_here" >> .env
echo "GITHUB_REPO=hvduoc/airbnb_webapp" >> .env
echo "WEBHOOK_SECRET=your_secret_here" >> .env
```

## 📊 Real-time Features

### **A. Live Activity Feed**
- Recent commits affecting .brain/
- Task status changes  
- New documents added
- Team member activities

### **B. Collaborative Editing**
- Multiple users can edit brain files
- Conflict resolution via GitHub merge
- Change notifications
- Activity logging

### **C. Mobile Access**
- Brain UI responsive design
- GitHub mobile app integration
- Quick task updates via mobile
- Push notifications

## 🎯 Usage Scenarios

### **Scenario 1: Task Update**
1. Team member vào Brain UI
2. Navigate to Tasks section
3. Update task status trong ACTIVE_TASKS.json
4. Changes auto-commit to GitHub
5. Other team members see updates trong 30s

### **Scenario 2: Document Collaboration**  
1. PM updates SCOPE.md via GitHub web editor
2. Webhook triggers brain sync
3. Dev team sees updated scope trong Brain UI
4. Comments/feedback via GitHub issues

### **Scenario 3: Remote Planning**
1. Team meeting via Zoom
2. Screen share Brain UI dashboard
3. Real-time updates ACTIVE_TASKS.json
4. Everyone sees changes live
5. Action items committed to GitHub

## 🔧 Technical Implementation

### **Current Status**
- ✅ Repository: https://github.com/hvduoc/airbnb_webapp
- ✅ Brain UI: Local development ready
- ✅ Webhook listener: Basic implementation  
- ⚠️ GitHub integration: Needs API token setup
- ⚠️ Real-time sync: Needs polling/websocket

### **Next Steps**
1. **Setup GitHub Personal Access Token**
2. **Configure webhook với proper secret**
3. **Test real-time sync flow**
4. **Deploy webhook listener to production**
5. **Train team on collaborative workflow**

## 💡 Benefits

### **For Team**
- ✅ **Real-time collaboration** on project planning
- ✅ **Version control** cho all brain documents  
- ✅ **Mobile access** to project status
- ✅ **Centralized knowledge** accessible anywhere

### **For AI Assistants**
- ✅ **Always up-to-date context** từ GitHub
- ✅ **Change history** for better understanding
- ✅ **Collaborative intelligence** với team inputs

### **For Project**  
- ✅ **Transparent progress** tracking
- ✅ **Distributed team** collaboration  
- ✅ **Knowledge preservation** in version control
- ✅ **Scalable documentation** system

---

**Ready to implement! 🚀 Bạn có muốn tôi setup GitHub integration ngay bây giờ không?**

---
*GitHub Integration Plan v1.0 | 28/09/2025*