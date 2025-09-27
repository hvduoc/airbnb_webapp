import React, { useState, useEffect } from 'react'
import { Home, BarChart3, ExternalLink } from 'lucide-react'
import './BangDieuKhien.css'

function BangDieuKhien() {
  const [thongKe, setThongKe] = useState(null)

  // Dữ liệu dashboard mẫu
  const duLieuMau = {
    duAn: {
      ten: "Airbnb Revenue WebApp",
      phienBan: "1.0.0",
      domain: "Hệ Thống Quản Lý Tài Sản (PMS)",
      trangThai: "Sẵn Sàng Production",
      capNhatCuoi: "27/09/2025",
      congNghe: ["FastAPI", "SQLAlchemy", "SQLite", "Jinja2", "Alembic"]
    },
    thongKeBrain: {
      tongFile: 12,
      fileTaiLieu: 8,
      taskDangHoatDong: 3,
      taskHoanThanh: 5,
      dongBoaCuoi: "27/09/2025 00:33"
    },
    lienKetNhanh: [
      {
        tieuDe: "Phạm Vi Dự Án",
        moTa: "Domain focus và yêu cầu business",
        duongDan: "/scope",
        icon: "📋"
      },
      {
        tieuDe: "Tasks Đang Hoạt Động",
        moTa: "Các ưu tiên phát triển hiện tại",
        duongDan: "/tasks",
        icon: "✅"
      },
      {
        tieuDe: "Ngữ Cảnh Session",
        moTa: "Hướng dẫn onboard AI nhanh",
        duongDan: "/session-context",
        icon: "🧠"
      },
      {
        tieuDe: "Bản Đồ Domain",
        moTa: "Kiến trúc business domain",
        duongDan: "/domain-map",
        icon: "🗺️"
      }
    ],
    hoatDongGanDay: [
      {
        hanhDong: "Tích Hợp Brain Template",
        thoiGian: "27/09/2025 00:33",
        moTa: "Tích hợp hệ thống brain chuẩn với backup"
      },
      {
        hanhDong: "Tạo SESSION_CONTEXT.md", 
        thoiGian: "27/09/2025 00:30",
        moTa: "Tài liệu loading context AI nhanh"
      },
      {
        hanhDong: "Thêm Scripts Tự Động",
        thoiGian: "27/09/2025 00:25",
        moTa: "Scripts PowerShell để setup brain"
      }
    ]
  }

  useEffect(() => {
    setThongKe(duLieuMau)
  }, [])

  if (!thongKe) {
    return <div className="dang-tai">Đang tải bảng điều khiển...</div>
  }

  return (
    <div className="bang-dieu-khien">
      <div className="header-dashboard">
        <div className="noi-dung-header">
          <div className="thong-tin-du-an">
            <h1>{thongKe.duAn.ten}</h1>
            <p className="domain-du-an">{thongKe.duAn.domain}</p>
            <div className="meta-du-an">
              <span className="phien-ban">v{thongKe.duAn.phienBan}</span>
              <span className="trang-thai">{thongKe.duAn.trangThai}</span>
              <span className="cap-nhat">Cập nhật {thongKe.duAn.capNhatCuoi}</span>
            </div>
          </div>
          <a 
            href="https://github.com/your-org/airbnb-webapp"
            target="_blank"
            rel="noopener noreferrer"
            className="link-github"
          >
            <ExternalLink size={20} />
            Xem Repository
          </a>
        </div>
      </div>

      {/* Lưới Thống Kê */}
      <div className="luoi-thong-ke">
        <div className="the-thong-ke">
          <div className="icon-thong-ke">📁</div>
          <div className="noi-dung-thong-ke">
            <h3>{thongKe.thongKeBrain.tongFile}</h3>
            <p>File Brain</p>
          </div>
        </div>
        
        <div className="the-thong-ke">
          <div className="icon-thong-ke">📖</div>
          <div className="noi-dung-thong-ke">
            <h3>{thongKe.thongKeBrain.fileTaiLieu}</h3>
            <p>Tài Liệu</p>
          </div>
        </div>
        
        <div className="the-thong-ke">
          <div className="icon-thong-ke">⚡</div>
          <div className="noi-dung-thong-ke">
            <h3>{thongKe.thongKeBrain.taskDangHoatDong}</h3>
            <p>Tasks Hoạt Động</p>
          </div>
        </div>
        
        <div className="the-thong-ke">
          <div className="icon-thong-ke">✅</div>
          <div className="noi-dung-thong-ke">
            <h3>{thongKe.thongKeBrain.taskHoanThanh}</h3>
            <p>Hoàn Thành</p>
          </div>
        </div>
      </div>

      {/* Lưới Nội Dung Chính */}
      <div className="luoi-noi-dung">
        {/* Liên Kết Nhanh */}
        <div className="phan-noi-dung">
          <h2>Điều Hướng Nhanh</h2>
          <div className="lien-ket-nhanh">
            {thongKe.lienKetNhanh.map((link, index) => (
              <a key={index} href={`#${link.duongDan}`} className="the-link-nhanh">
                <div className="icon-link">{link.icon}</div>
                <div className="noi-dung-link">
                  <h3>{link.tieuDe}</h3>
                  <p>{link.moTa}</p>
                </div>
              </a>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="phan-noi-dung">
          <h2>Công Nghệ Sử Dụng</h2>
          <div className="tech-stack">
            {thongKe.duAn.congNghe.map((tech, index) => (
              <span key={index} className="huy-hieu-tech">{tech}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Hoạt Động Gần Đây */}
      <div className="phan-noi-dung">
        <h2>Hoạt Động Brain Gần Đây</h2>
        <div className="danh-sach-hoat-dong">
          {thongKe.hoatDongGanDay.map((hoatDong, index) => (
            <div key={index} className="muc-hoat-dong">
              <div className="noi-dung-hoat-dong">
                <h3>{hoatDong.hanhDong}</h3>
                <p>{hoatDong.moTa}</p>
              </div>
              <div className="thoi-gian-hoat-dong">
                {hoatDong.thoiGian}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Thông Tin */}
      <div className="footer-dashboard">
        <div className="thong-tin-dong-bo">
          <BarChart3 size={16} />
          <span>Đồng bộ brain cuối: {thongKe.thongKeBrain.dongBoaCuoi}</span>
        </div>
        <div className="thong-tin-brain">
          <Home size={16} />
          <span>Hệ Thống Brain Hoạt Động</span>
        </div>
      </div>
    </div>
  )
}

export default BangDieuKhien