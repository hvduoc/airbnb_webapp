# Airbnb Webapp

Repository gồm ứng dụng web và “Brain System” cho AI (`.brain`) cùng bộ prompt (`.prompts`).

## Bắt đầu nhanh
1. Cài Python 3.11+ (hoặc theo `requirements.txt` nếu có).
2. `cp .env.example .env` rồi chỉnh biến phù hợp (xem bên dưới).
3. Cài deps: `pip install -r requirements.txt` (hoặc `requirements-dev.txt` nếu có).
4. Chạy dev: `APP_ENV=development uvicorn app:app --reload` (ví dụ).

> Tài liệu chi tiết: `QUICK_START.md`, `DEPLOY_GUIDE.md`, `RAILWAY_ENV_SETUP.md`, `MONITORING_DEPLOYMENT_GUIDE.md`, các release notes.

## Brain & Prompts (chỉ dùng ở development)
- **Không public** `.brain` và `.prompts` trên production.
- Để bật duyệt nội dung trong dev, đặt `BRAIN_MOUNT=true` hoặc `APP_ENV=development` (xem snippet `main.brain-mount.example.py`).

## Bảo mật
- Không commit secrets. Dùng `.env.example` làm mẫu, secrets thật đặt trong **GitHub Actions → Secrets/Environments**. Thêm chi tiết: `SECURITY.md`.

## Quy trình làm việc AI (tóm tắt)
- Dùng workflow 3-phase: Session start → Work execution → Session end (tham khảo /.prompts/README.md).
- Mỗi file .brain nên có header metadata: owner, last_updated, purpose.
- Mỗi thay đổi của AI phải đi kèm PR nhỏ, kèm test nếu ảnh hưởng logic.
- CI sẽ kiểm tra: no-secrets scan, tests, và đảm bảo .brain không bị serve trong production.

## Tài liệu liên quan
- /.brain/README.md — hướng dẫn chi tiết hệ thống “Brain”
- /.prompts/README.md — hướng dẫn prompt workflow
- /.github/ — templates PR/Issue và workflows (sẽ thêm nếu chưa có)