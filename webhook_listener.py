# GitHub Webhook Listener - Home Server

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import hashlib
import hmac
import json
import os
from datetime import datetime
import subprocess
import sys

app = FastAPI(title="Airbnb GitHub Webhook Listener")

# Configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-secret-here')
BRAIN_DIR = '.brain'

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    if not signature:
        return False
    
    try:
        sha_name, signature = signature.split('=')
    except ValueError:
        return False
    
    if sha_name != 'sha256':
        return False
    
    mac = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256)
    expected_signature = mac.hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def update_brain_context(event_data: dict):
    """Update brain system with GitHub event data"""
    try:
        # Prepare context update
        update_info = {
            "timestamp": datetime.now().isoformat(),
            "event": event_data.get("action", "push"),
            "repository": event_data.get("repository", {}).get("name", "unknown"),
            "branch": event_data.get("ref", "").replace("refs/heads/", ""),
            "commits": []
        }
        
        # Extract commit information
        if "commits" in event_data:
            for commit in event_data["commits"]:
                update_info["commits"].append({
                    "id": commit.get("id", "")[:8],
                    "message": commit.get("message", ""),
                    "author": commit.get("author", {}).get("name", ""),
                    "modified": commit.get("modified", []),
                    "added": commit.get("added", []),
                    "removed": commit.get("removed", [])
                })
        
        # Save to brain system
        brain_file = os.path.join(BRAIN_DIR, "GITHUB_EVENTS.json")
        
        # Load existing events
        events = []
        if os.path.exists(brain_file):
            try:
                with open(brain_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            except:
                events = []
        
        # Add new event
        events.insert(0, update_info)  # Latest first
        
        # Keep only last 50 events
        events = events[:50]
        
        # Save updated events
        os.makedirs(BRAIN_DIR, exist_ok=True)
        with open(brain_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        # Update session context
        update_session_context(update_info)
        
        return True
        
    except Exception as e:
        print(f"Error updating brain context: {e}")
        return False

def update_session_context(update_info: dict):
    """Update SESSION_CONTEXT.md with latest changes"""
    try:
        session_file = os.path.join(BRAIN_DIR, "SESSION_CONTEXT.md")
        
        # Create session update entry
        session_update = f"""
## 🔄 GitHub Update - {update_info['timestamp'][:19]}
- **Repository**: {update_info['repository']}
- **Branch**: {update_info['branch']}
- **Event**: {update_info['event']}

### 📝 Changes:
"""
        
        for commit in update_info.get('commits', []):
            session_update += f"""
**Commit {commit['id']}**: {commit['message']}
- Author: {commit['author']}
- Modified: {len(commit['modified'])} files
- Added: {len(commit['added'])} files  
- Removed: {len(commit['removed'])} files
"""
        
        # Append to session context
        if os.path.exists(session_file):
            with open(session_file, 'a', encoding='utf-8') as f:
                f.write(session_update)
        else:
            with open(session_file, 'w', encoding='utf-8') as f:
                f.write(f"# Session Context - Auto Updated\n{session_update}")
                
    except Exception as e:
        print(f"Error updating session context: {e}")

@app.get("/")
async def root():
    return {"message": "Airbnb GitHub Webhook Listener - Home Server", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "brain_dir": os.path.exists(BRAIN_DIR),
        "webhook_secret": "configured" if WEBHOOK_SECRET != 'your-secret-here' else "default"
    }

@app.post("/webhook/github")
async def github_webhook(request: Request):
    try:
        # Get payload and signature
        payload = await request.body()
        signature = request.headers.get('X-Hub-Signature-256', '')
        event_type = request.headers.get('X-GitHub-Event', '')
        
        # Verify signature
        if not verify_signature(payload, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse payload
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Process the webhook
        print(f"📨 GitHub Event: {event_type}")
        print(f"📂 Repository: {event_data.get('repository', {}).get('name', 'unknown')}")
        
        # Update brain system
        success = update_brain_context(event_data)
        
        response_data = {
            "status": "success",
            "event_type": event_type,
            "repository": event_data.get('repository', {}).get('name'),
            "processed": datetime.now().isoformat(),
            "brain_updated": success
        }
        
        # Log for debugging
        print(f"✅ Webhook processed: {json.dumps(response_data, indent=2)}")
        
        return JSONResponse(content=response_data, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/brain/status")
async def brain_status():
    """Check brain system status"""
    try:
        status = {
            "brain_dir_exists": os.path.exists(BRAIN_DIR),
            "files": []
        }
        
        if os.path.exists(BRAIN_DIR):
            for file in os.listdir(BRAIN_DIR):
                file_path = os.path.join(BRAIN_DIR, file)
                if os.path.isfile(file_path):
                    status["files"].append({
                        "name": file,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/brain/events")
async def get_brain_events():
    """Get recent GitHub events from brain system"""
    try:
        brain_file = os.path.join(BRAIN_DIR, "GITHUB_EVENTS.json")
        
        if not os.path.exists(brain_file):
            return {"events": [], "count": 0}
        
        with open(brain_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
        
        return {
            "events": events[:10],  # Return last 10 events
            "count": len(events),
            "last_updated": events[0]["timestamp"] if events else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Set webhook secret from environment or prompt
    if WEBHOOK_SECRET == 'your-secret-here':
        print("⚠️  WARNING: Using default webhook secret!")
        print("Set WEBHOOK_SECRET environment variable for security")
    
    print(f"🚀 Starting webhook listener on http://0.0.0.0:8080")
    print(f"📁 Brain directory: {os.path.abspath(BRAIN_DIR)}")
    print(f"🔗 GitHub webhook URL: http://webhook.xemgiadat.com/webhook/github")
    
    uvicorn.run("webhook_listener:app", host="0.0.0.0", port=8080, reload=True)