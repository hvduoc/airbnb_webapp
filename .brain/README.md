---
owner: hvduoc
last_updated: 2025-10-18
purpose: Bộ não AI cho dự án Airbnb WebApp và template tái sử dụng đa dự án
version: 2.0 - Multi-Project Template
---

# 🧠 HỆ THỐNG BỘ NÃO AI - AIRBNB WEBAPP

> **Mục tiêu**: Ngăn chặn AI "quên ngữ cảnh" và "lạc scope" — đảm bảo mọi phiên làm việc đều có context đầy đủ và focus đúng mục tiêu.

**Bộ não AI** là hệ thống quản lý ngữ cảnh nội bộ chuyên nghiệp, có thể tái sử dụng cho nhiều dự án (Airbnb, PMS, OTA, SaaS...).  
Hệ thống giúp AI duy trì trí nhớ dài hạn, quản lý tasks, metrics, logs và đảm bảo tuân thủ quy trình, bảo mật, cũng như hiệu quả vận hành.

---

## 🎯 KIẾN TRÚC DUAL-LAYER

👥 CLIENT LAYER (WebApp):
├── Giao diện sạch sẽ, chuyên nghiệp
├── Tính năng nghiệp vụ cốt lõi
├── Hỗ trợ hoàn toàn Tiếng Việt
└── Hoàn hảo cho presentation với khách hàng

🧠 DEVELOPER LAYER (Brain):
├── Giám sát hệ thống toàn diện
├── Chẩn đoán và điều khiển nâng cao
├── Quản lý task và theo dõi tiến độ
└── Công cụ nội bộ tối đa hiệu quả

yaml
Copy code

---

## 📁 CẤU TRÚC THƯ MỤC CHUẨN

/.brain/
├── README.md # File này - hướng dẫn sử dụng chính
├── SCOPE.md # Phạm vi dự án & những gì KHÔNG làm
├── GLOSSARY.md # Thuật ngữ chuyên môn
├── WORKFLOW_SIMPLE.md # Quy trình làm việc đơn giản
├── context/
│ ├── CONTEXT_INDEX.md # Danh mục tất cả context files
│ ├── VIETNAMESE_AI_INSTRUCTIONS.md # Hướng dẫn AI tiếng Việt
│ └── DOMAIN_MAP.md # Sơ đồ domain business
├── tasks/
│ ├── ACTIVE_TASKS.json # Công việc đang làm với scope cụ thể
│ └── PROJECT_TASKS.json # Lịch sử task và completed items
├── logs/daily/ # Nhật ký làm việc hàng ngày
├── metrics/ # KPIs & tiêu chí thành công
├── plans/ # Kế hoạch chiến lược
├── PLAYBOOKS/ # Hướng dẫn AI & quy tắc
│ ├── COPILOT_GUARDRAILS.md # Nguyên tắc bắt buộc cho AI
│ └── PROMPTING.md # Template prompt cho AI
└── PROJECT_TEMPLATE/ # Template cho dự án mới
├── SETUP_GUIDE.md
├── TEMPLATE_SCOPE.md
├── SAMPLE_ACTIVE_TASKS.json
└── QUICK_START.md

yaml
Copy code

---

## 🚀 WORKFLOW CHO AI COPILOT

### **Bước 1: Session Start**

```bash
# AI PHẢI ĐỌC THEO THỨ TỰ:
1. /.brain/context/VIETNAMESE_AI_INSTRUCTIONS.md  # BẮT BUỘC!
2. /.brain/SCOPE.md                               # Phạm vi & non-goals  
3. /.brain/tasks/ACTIVE_TASKS.json                # Tasks hiện tại
4. /.brain/PLAYBOOKS/COPILOT_GUARDRAILS.md        # Nguyên tắc bắt buộc
5. /.brain/context/DOMAIN_MAP.md                  # Business entities
Bước 2: Work Execution
AI PHẢI FOLLOW format trả lời:

Problem • Minimal change • Files • Test plan • Risks • Out-of-scope

Bước 3: Session End
bash
Copy code
- Cập nhật daily log với summary
- Update ACTIVE_TASKS.json nếu cần
- Sync metrics với deliverables
🌐 TRUY CẬP BRAIN DASHBOARD
pgsql
Copy code
URL: http://127.0.0.1:8000/brain
Yêu cầu: Server phải đang chạy
Đối tượng: Developer only (internal tool)
🎯 Tính Năng Dashboard
Tình trạng hệ thống real-time

Nhiệm vụ đang hoạt động

Nhật ký hàng ngày monitoring

Thao tác nhanh đến brain files

AI Session Starter với clipboard integration

🔒 GUARDRAILS & SECURITY
🇻🇳 Nguyên Tắc Tiếng Việt
✅ 100% giao tiếp bằng Tiếng Việt

✅ User-facing text và comment hoàn toàn Việt hóa

✅ Error messages thân thiện người dùng

🔒 Scope Control
✅ Chỉ làm việc trong files được chỉ định

✅ Tuân thủ goals/non-goals trong ACTIVE_TASKS.json

✅ Nếu request ngoài scope → ghi vào “Out-of-scope Suggestions”

🛡️ Security & Safety
❌ Không commit secrets/API keys

❌ Không expose PII data

❌ Không chạy lệnh nguy hiểm production

📊 METRICS & TRACKING
KPIs theo dõi hàng tuần
Mục tiêu	Chỉ số	Ngưỡng
Setup time	< 10 phút	✅
AI onboard context	< 5 phút	✅
Repeat questions	< 2/session	✅
Defect leakage	< 1/tuần	✅
PR first-pass rate	> 80%	✅

Daily Logging
What changed

Blockers encountered

Out-of-scope suggestions

Context gaps discovered

🔧 SCRIPTS & AUTOMATION
Script	Mục đích
scripts/session-start	Khởi tạo daily log
scripts/session-end	Tổng kết session
.github/workflows/context-check.yml	Kiểm tra tồn tại file context bắt buộc
scripts/cleanup_backups.sh	Dọn backup, đảm bảo repo sạch

🖥️ TECHNICAL INTEGRATION (AIRBNB WEBAPP)
Backend
python
Copy code
# routes_brain.py
- load_brain_metrics()
- load_active_tasks()
- load_recent_daily_logs()
- check_brain_health()
Frontend
html
Copy code
# templates/brain_dashboard.html
- Responsive Bootstrap design
- Vietnamese-optimized interface
- Interactive dashboard components
Static File Serving
python
Copy code
# main.py
import os
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

app = FastAPI()
ENV = os.getenv("APP_ENV", "production").lower()
if ENV == "development" or os.getenv("BRAIN_MOUNT", "false").lower() == "true":
    app.mount("/_brain", StaticFiles(directory=".brain"), name="brain")
🎯 WORKFLOW TÍCH HỢP TRONG DỰ ÁN
Session Start
less
Copy code
1. Chạy server: uvicorn main:app --reload
2. Truy cập brain: http://127.0.0.1:8000/brain  
3. Review context & tasks
4. Bắt đầu session tập trung
Trong Quá Trình Phát Triển
css
Copy code
1. Code có comment Tiếng Việt
2. Cập nhật tiến độ task
3. Document decisions & findings
4. Test với thông báo lỗi thân thiện
Session End
pgsql
Copy code
1. Update ACTIVE_TASKS.json
2. Ghi daily log
3. Cập nhật metrics
4. Lên kế hoạch cho session tiếp theo
📈 SUCCESS METRICS & BUSINESS VALUE
Hiệu quả kỹ thuật
less
Copy code
⚡ Context switching: giảm 70%
🎯 Task clarity: 100% rõ mục tiêu
📈 Progress tracking: real-time
🧠 Knowledge retention: tập trung hóa tài liệu
Chất lượng code
css
Copy code
🇻🇳 100% Tiếng Việt, không lẫn ngôn ngữ
📝 Document rõ ràng, self-explaining
🔄 Workflow chuẩn hóa, dễ review
Giá trị doanh nghiệp
css
Copy code
👥 Giao diện sạch, thân thiện khách hàng
📊 Dashboard chuyên nghiệp
🚀 Sẵn sàng mở rộng đa dự án
🔁 TEMPLATE ÁP DỤNG CHO DỰ ÁN MỚI
⚡ Quick Start (< 10 phút)
cp -r existing_project/.brain new_project/

Cập nhật TEMPLATE_SCOPE.md, ACTIVE_TASKS.json, DOMAIN_MAP.md

Test Brain Dashboard accessibility

📋 Checklist
 Scope.md được cập nhật

 Có ít nhất 1 task hoạt động

 DOMAIN_MAP.md phù hợp domain

 Dashboard hoạt động

 AI session đầu tiên thành công

🛠️ MAINTENANCE & UPDATES
Weekly Tasks
 Review ACTIVE_TASKS.json

 Clean daily logs cũ

 Update metrics thực tế

Monthly Tasks
 Review SCOPE.md

 Update DOMAIN_MAP.md

 Refresh AI instructions

 Cải tiến templates

🏆 KẾT LUẬN
Brain System là nền tảng giúp bạn và AI cộng tác hiệu quả, an toàn, có kiểm soát và 100% Việt hóa.
Nó vừa phục vụ dự án Airbnb WebApp hiện tại, vừa là khuôn mẫu chuẩn hóa cho mọi dự án tương lai.

Tạo bởi: AI Development Team
Cập nhật cuối: 2025-10-18
Version: 2.0 - Multi-Project Template

yaml
Copy code

---

## ✅ Gợi ý commit (để Copilot hoặc bạn chạy)

```bash
mv .brain/test_automation/README_NEW.md .brain/archive/README_OLD_2025_09_26.md
git add .brain/test_automation/README.md .brain/archive/
git commit -m "docs(brain): merge README_NEW into README.md (v2.0 multi-project template)"

