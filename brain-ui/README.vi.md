# Brain UI - Giao Diện Web Hiển Thị Nội Dung .brain/

Một giao diện web React hiện đại để hiển thị và điều hướng nội dung thư mục `.brain/` của dự án - hệ thống "bộ não dự án" giúp team và AI theo dõi context, scope, tasks, logs và ADR.

## 🌟 Tính Năng

- **Bảng Điều Khiển**: Tổng quan dự án với thống kê và điều hướng nhanh
- **Trình Xem Tài Liệu**: Hiển thị file Markdown với highlight cú pháp
- **Quản Lý Tasks**: Xem ACTIVE_TASKS.json với tìm kiếm và lọc
- **Thiết Kế Responsive**: Thân thiện với mobile và hỗ trợ chế độ tối
- **Trang Tĩnh**: Có thể triển khai lên GitHub Pages, Vercel, Netlify
- **Hỗ Trợ Tiếng Việt**: Giao diện hoàn toàn bằng tiếng Việt

## 🚀 Bắt Đầu Nhanh

### Yêu Cầu Hệ Thống
- Node.js 18+ và npm/yarn
- Dự án của bạn có cấu trúc thư mục `.brain/`

### Cài Đặt

```powershell
# Di chuyển vào thư mục brain-ui
cd brain-ui

# Cài đặt dependencies
npm install

# Chạy server development
npm run dev
```

Server development sẽ chạy trên http://localhost:5173

### Build Để Triển Khai

```powershell
# Build file tĩnh
npm run build

# Xem trước bản build production
npm run preview
```

Các file đã build sẽ nằm trong thư mục `dist/`.

## 📁 Cấu Trúc Dự Án

```
brain-ui/
├── src/
│   ├── components/          # Các React component
│   │   ├── BangDieuKhien.jsx    # Bảng điều khiển chính
│   │   ├── ThanhDieuHuong.jsx   # Thanh điều hướng  
│   │   ├── TrinhXemMarkdown.jsx # Hiển thị file markdown
│   │   └── TrinhXemTasks.jsx    # Quản lý tasks
│   ├── App.jsx             # Component chính
│   ├── main.jsx           # Entry point React
│   └── index.css          # Style toàn cục
├── public/                 # Tài nguyên tĩnh
│   └── brain/             # Dữ liệu .brain/ mẫu
├── dist/                   # Bản build production
├── package.json
├── vite.config.js
└── README.vi.md
```

## 🔧 Cấu Hình

### Tích Hợp Dữ Liệu Brain

Hiện tại sử dụng dữ liệu mẫu. Để tích hợp với file `.brain/` thật:

1. Copy các file `.brain/` vào `public/brain/`:
```powershell
# Copy file brain vào thư mục public
Copy-Item -Recurse .brain/* brain-ui/public/brain/
```

2. Cập nhật components để fetch từ `/brain/`:
```javascript
// Ví dụ: TrinhXemMarkdown.jsx
const response = await fetch('/brain/documentation/SCOPE.md');
const content = await response.text();
```

### Tùy Chỉnh Giao Diện

#### Màu Sắc & Theme
Chỉnh sửa CSS variables trong `src/index.css`:
```css
:root {
  --mau-chinh: #3b82f6;      /* Đổi màu chính */
  --nen-the: #ffffff;        /* Nền các thẻ */
  --chu-chinh: #1f2937;      /* Màu chữ chính */
}
```

#### Menu Điều Hướng
Cập nhật `src/components/ThanhDieuHuong.jsx` để tùy chỉnh menu:
```javascript
const mucMenu = [
  // Thêm mục menu tùy chỉnh
  { duongDan: '/tuy-chinh', nhan: 'Trang Tùy Chỉnh', icon: '🔧' }
];
```

## 🌐 Triển Khai

### GitHub Pages

1. Build dự án:
```powershell
npm run build
```

2. Đẩy nội dung `dist/` lên nhánh `gh-pages`:
```powershell
# Sử dụng package gh-pages
npm run deploy:gh-pages
```

3. Bật GitHub Pages trong settings repository

### Vercel

```powershell
# Cài đặt Vercel CLI
npm install -g vercel

# Triển khai
npm run deploy:vercel
```

### Netlify

```powershell
# Cài đặt Netlify CLI  
npm install -g netlify-cli

# Triển khai
npm run build
npm run deploy:netlify
```

## 🛠️ Phát Triển

### Thêm Component Mới

1. Tạo file component trong `src/components/`:
```javascript
// src/components/ComponentMoi.jsx
import React from 'react';
import './ComponentMoi.css';

function ComponentMoi() {
  return <div>Component Mới</div>;
}

export default ComponentMoi;
```

2. Thêm file CSS cùng tên
3. Import vào `App.jsx` và thêm route nếu cần

### Tích Hợp Dữ Liệu

Các component hiện dùng dữ liệu mẫu. Để tích hợp thật:

1. **Cách File Tĩnh** (Khuyến khích):
   - Copy file `.brain/` vào `public/brain/`
   - Fetch qua HTTP requests thông thường

2. **Cách API**:
   - Tạo API backend endpoints
   - Cập nhật components để gọi API

### Hướng Dẫn Styling

- Sử dụng CSS variables để theme nhất quán
- Thiết kế responsive mobile-first
- Sử dụng semantic HTML elements
- Duy trì accessibility (ARIA labels, keyboard navigation)

## 📱 Hỗ Trợ Mobile

Giao diện hoàn toàn responsive với breakpoints:
- Desktop: 1024px+
- Tablet: 768px - 1023px  
- Mobile: 480px - 767px
- Mobile Nhỏ: < 480px

## 🔍 Hỗ Trợ Trình Duyệt

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🐛 Xử Lý Sự Cố

### Lỗi Build

```powershell
# Xóa cache và cài lại
Remove-Item -Recurse node_modules
Remove-Item package-lock.json
npm install
```

### Lỗi Routing Trên Static Hosts

Thêm file `_redirects` vào thư mục `public/`:
```
/*    /index.html   200
```

### Lỗi CORS Với Brain Files

Đảm bảo brain files được serve từ cùng origin hoặc cấu hình CORS headers đúng cách.

## 📈 Hiệu Năng

- Vite cung cấp HMR nhanh trong development
- Production build bao gồm:
  - Code splitting
  - Asset optimization  
  - Tree shaking
  - Minification

## 🤝 Đóng Góp

1. Fork repository
2. Tạo feature branch
3. Thực hiện thay đổi với testing đầy đủ
4. Gửi pull request

## 📄 Giấy Phép

Dự án này tuân theo giấy phép của dự án chính.

## 🔗 Liên Kết

- [Tài Liệu React](https://react.dev)
- [Tài Liệu Vite](https://vitejs.dev)
- [Hệ Thống Brain Template](../PROJECT_TEMPLATE/)

---

Được xây dựng với ❤️ cho hệ sinh thái Brain