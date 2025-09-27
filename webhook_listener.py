"""
GitHub Webhook Listener for Brain Data Sync
Tự động đồng bộ file .brain/ từ GitHub repository khi có push events
"""

import os
import json
import hmac
import hashlib
import subprocess
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Brain Data Webhook Sync", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn origins cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'your-secret-key-here')
REPO_URL = os.getenv('REPO_URL', 'https://github.com/your-org/airbnb-webapp.git')
TEMP_DIR = Path('./temp_sync')
BRAIN_SOURCE = Path('./temp_sync/.brain')
BRAIN_DEST = Path('./brain-ui/public/brain')
SYNC_LOG_FILE = Path('./sync_history.json')

class SyncLog(BaseModel):
    timestamp: str
    commit_sha: str
    commit_message: str
    author: str
    files_changed: list
    status: str
    error: Optional[str] = None

def verify_signature(payload_body: bytes, signature: str) -> bool:
    """Xác thực chữ ký GitHub webhook"""
    if not signature:
        return False
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    expected_signature = f"sha256={expected_signature}"
    
    return hmac.compare_digest(expected_signature, signature)

def log_sync_event(log_entry: SyncLog):
    """Ghi log sự kiện đồng bộ"""
    logs = []
    if SYNC_LOG_FILE.exists():
        try:
            with open(SYNC_LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    
    logs.append(log_entry.dict())
    
    # Chỉ giữ lại 50 log gần nhất
    if len(logs) > 50:
        logs = logs[-50:]
    
    with open(SYNC_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def clone_or_pull_repo() -> bool:
    """Clone hoặc pull repository"""
    try:
        if TEMP_DIR.exists():
            # Pull nếu đã tồn tại
            logger.info("Pulling latest changes...")
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=TEMP_DIR,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                logger.error(f"Git pull failed: {result.stderr}")
                # Thử xóa và clone lại
                shutil.rmtree(TEMP_DIR)
                return clone_repo()
        else:
            return clone_repo()
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Error in clone_or_pull_repo: {e}")
        return False

def clone_repo() -> bool:
    """Clone repository từ đầu"""
    try:
        logger.info(f"Cloning repository {REPO_URL}...")
        result = subprocess.run(
            ['git', 'clone', REPO_URL, str(TEMP_DIR)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("Repository cloned successfully")
            return True
        else:
            logger.error(f"Git clone failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        return False

def sync_brain_files() -> tuple[bool, str]:
    """Đồng bộ file .brain/ từ temp sang public/brain/"""
    try:
        if not BRAIN_SOURCE.exists():
            return False, f"Source .brain directory not found: {BRAIN_SOURCE}"
        
        # Tạo thư mục đích nếu chưa có
        BRAIN_DEST.mkdir(parents=True, exist_ok=True)
        
        # Copy toàn bộ nội dung .brain/
        files_synced = []
        for item in BRAIN_SOURCE.rglob('*'):
            if item.is_file():
                # Tính relative path
                relative_path = item.relative_to(BRAIN_SOURCE)
                dest_file = BRAIN_DEST / relative_path
                
                # Tạo thư mục cha nếu cần
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(item, dest_file)
                files_synced.append(str(relative_path))
                
        logger.info(f"Synced {len(files_synced)} files to {BRAIN_DEST}")
        return True, f"Synced {len(files_synced)} files: {', '.join(files_synced[:5])}"
        
    except Exception as e:
        error_msg = f"Error syncing brain files: {e}"
        logger.error(error_msg)
        return False, error_msg

async def process_webhook_sync(payload: dict) -> dict:
    """Xử lý đồng bộ trong background"""
    try:
        # Lấy thông tin commit
        commits = payload.get('commits', [])
        if not commits:
            return {"status": "skipped", "reason": "No commits found"}
        
        latest_commit = commits[-1]
        commit_sha = latest_commit.get('id', 'unknown')
        commit_message = latest_commit.get('message', 'No message')
        author = latest_commit.get('author', {}).get('name', 'Unknown')
        
        # Kiểm tra xem có thay đổi file .brain/ không
        brain_files_changed = []
        for commit in commits:
            for file_list in ['added', 'modified', 'removed']:
                files = commit.get(file_list, [])
                brain_files = [f for f in files if f.startswith('.brain/')]
                brain_files_changed.extend(brain_files)
        
        if not brain_files_changed:
            logger.info("No .brain/ files changed, skipping sync")
            return {
                "status": "skipped",
                "reason": "No .brain/ files changed",
                "commit": commit_sha[:8]
            }
        
        logger.info(f"Brain files changed: {brain_files_changed}")
        
        # Bước 1: Clone/Pull repository
        if not clone_or_pull_repo():
            raise Exception("Failed to clone/pull repository")
        
        # Bước 2: Sync brain files
        success, message = sync_brain_files()
        if not success:
            raise Exception(message)
        
        # Ghi log thành công
        log_entry = SyncLog(
            timestamp=datetime.now().isoformat(),
            commit_sha=commit_sha,
            commit_message=commit_message,
            author=author,
            files_changed=brain_files_changed,
            status="success"
        )
        log_sync_event(log_entry)
        
        logger.info(f"Sync completed successfully for commit {commit_sha[:8]}")
        
        return {
            "status": "success",
            "commit": commit_sha[:8],
            "message": message,
            "files_changed": brain_files_changed
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Sync failed: {error_msg}")
        
        # Ghi log lỗi
        if 'latest_commit' in locals():
            log_entry = SyncLog(
                timestamp=datetime.now().isoformat(),
                commit_sha=commit_sha,
                commit_message=commit_message,
                author=author,
                files_changed=brain_files_changed if 'brain_files_changed' in locals() else [],
                status="error",
                error=error_msg
            )
            log_sync_event(log_entry)
        
        return {
            "status": "error",
            "error": error_msg
        }

@app.post("/api/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """GitHub webhook endpoint"""
    
    # Đọc payload
    payload_body = await request.body()
    
    # Xác thực chữ ký
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(payload_body, signature):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse payload
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Kiểm tra event type
    event_type = request.headers.get('X-GitHub-Event')
    if event_type != 'push':
        return {"message": f"Ignored event: {event_type}"}
    
    # Kiểm tra branch (chỉ xử lý main/master)
    ref = payload.get('ref', '')
    if not (ref.endswith('/main') or ref.endswith('/master')):
        return {"message": f"Ignored branch: {ref}"}
    
    logger.info(f"Received push event for {ref}")
    
    # Xử lý sync trong background
    background_tasks.add_task(process_webhook_sync, payload)
    
    return {
        "message": "Webhook received, processing sync in background",
        "event": event_type,
        "ref": ref
    }

@app.get("/api/sync/status")
async def get_sync_status():
    """Lấy trạng thái đồng bộ gần nhất"""
    if not SYNC_LOG_FILE.exists():
        return {"message": "No sync history found"}
    
    try:
        with open(SYNC_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        if not logs:
            return {"message": "No sync history found"}
        
        latest_log = logs[-1]
        return {
            "latest_sync": latest_log,
            "brain_dest_exists": BRAIN_DEST.exists(),
            "total_syncs": len(logs)
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/sync/history")
async def get_sync_history():
    """Lấy lịch sử đồng bộ"""
    if not SYNC_LOG_FILE.exists():
        return {"history": []}
    
    try:
        with open(SYNC_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        return {"history": logs[-20:]}  # 20 log gần nhất
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/sync/manual")
async def manual_sync(background_tasks: BackgroundTasks):
    """Trigger đồng bộ thủ công"""
    logger.info("Manual sync triggered")
    
    # Tạo payload giả lập
    fake_payload = {
        "commits": [{
            "id": "manual-sync-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
            "message": "Manual sync triggered",
            "author": {"name": "Manual Trigger"},
            "added": [".brain/manual_sync"],
            "modified": [],
            "removed": []
        }]
    }
    
    background_tasks.add_task(process_webhook_sync, fake_payload)
    
    return {"message": "Manual sync started"}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Brain Data Webhook Sync",
        "status": "running",
        "brain_dest": str(BRAIN_DEST),
        "brain_dest_exists": BRAIN_DEST.exists()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)