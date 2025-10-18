# SECURITY

## Secrets
- Không bao giờ commit secrets/API keys/credentials.
- Dùng `.env.example` làm mẫu; secrets thật:
  - Local: `.env` (đã ignore)
  - CI/Prod: **GitHub Actions → Secrets/Environments**

## Lộ secrets phải làm gì?
1) Thu hồi (revoke) / rotate khoá ngay.
2) Xoá khỏi history (filter-repo) nếu cần.
3) Tạo incident note trong repo (Issue private hoặc doc nội bộ).

## Dữ liệu nhạy cảm
- Không log PII. Ẩn/redact trong middleware nếu có.

## Phơi bày “Brain”
- Không mount `.brain` / `.prompts` ở production hoặc môi trường public.
