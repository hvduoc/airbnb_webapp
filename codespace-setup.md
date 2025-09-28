# GitHub Codespace Setup Commands

# Terminal 1: Install Python dependencies
pip install -r requirements.txt

# Terminal 2: Install Node.js dependencies  
cd brain-ui
npm install
cd ..

# Terminal 3: Start webhook listener
uvicorn webhook_listener:app --host 0.0.0.0 --port 8080

# Terminal 4: Start Brain UI (new terminal)
cd brain-ui
npm run dev -- --host 0.0.0.0 --port 3000

# Terminal 5: Start main API (new terminal)
uvicorn main:app --host 0.0.0.0 --port 8000

# Codespaces sẽ tự động tạo public URLs:
# Port 8080 (webhook): https://xyz-8080.app.github.dev  
# Port 3000 (brain): https://xyz-3000.app.github.dev
# Port 8000 (api): https://xyz-8000.app.github.dev