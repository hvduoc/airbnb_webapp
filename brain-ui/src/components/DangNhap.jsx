import React, { useState } from 'react'
import { Eye, EyeOff, Lock, User, LogIn } from 'lucide-react'
import './DangNhap.css'

function DangNhap({ onDangNhapThanhCong }) {
  const [tenDangNhap, setTenDangNhap] = useState('')
  const [matKhau, setMatKhau] = useState('')
  const [hienMatKhau, setHienMatKhau] = useState(false)
  const [loi, setLoi] = useState('')
  const [dangDangNhap, setDangDangNhap] = useState(false)

  // Thông tin đăng nhập hardcoded
  const THONG_TIN_DANG_NHAP = {
    admin: 'brain2025',
    manager: 'airbnb2025',
    user: 'pms2025'
  }

  const xuLyDangNhap = async (e) => {
    e.preventDefault()
    setLoi('')
    setDangDangNhap(true)

    // Simulate loading delay
    await new Promise(resolve => setTimeout(resolve, 800))

    // Kiểm tra thông tin đăng nhập
    if (THONG_TIN_DANG_NHAP[tenDangNhap] === matKhau) {
      // Tạo session token và thời gian hết hạn (24 giờ)
      const sessionToken = `brain-session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      const expiryTime = new Date().getTime() + (24 * 60 * 60 * 1000) // 24 hours

      // Lưu thông tin session
      localStorage.setItem('brain-ui-session', sessionToken)
      localStorage.setItem('brain-ui-session-expiry', expiryTime.toString())
      
      // Lưu thông tin user
      const userInfo = {
        tenDangNhap: tenDangNhap,
        tenHienThi: tenDangNhap === 'admin' ? 'Admin System' : 
                   tenDangNhap === 'manager' ? 'Property Manager' : 'User',
        vaiTro: tenDangNhap === 'admin' ? 'Quản trị viên' : 
                tenDangNhap === 'manager' ? 'Quản lý' : 'Người dùng',
        thoiGianDangNhap: new Date().toISOString()
      }
      localStorage.setItem('brain-ui-user-info', JSON.stringify(userInfo))
      
      // Callback để cập nhật App state
      onDangNhapThanhCong()
    } else {
      setLoi('Tên đăng nhập hoặc mật khẩu không đúng!')
    }
    
    setDangDangNhap(false)
  }

  return (
    <div className="trang-dang-nhap">
      <div className="container-dang-nhap">
        <div className="form-dang-nhap">
          <div className="header-dang-nhap">
            <div className="logo-dang-nhap">
              <span className="icon-brain">🧠</span>
              <h1>Brain UI</h1>
            </div>
            <h2>Đăng Nhập Vào Hệ Thống</h2>
            <p>Truy cập giao diện quản lý Brain System</p>
          </div>

          <form onSubmit={xuLyDangNhap} className="form-nhap-lieu">
            <div className="nhom-input">
              <label htmlFor="username">Tên Đăng Nhập</label>
              <div className="input-wrapper">
                <User size={20} />
                <input
                  id="username"
                  type="text"
                  value={tenDangNhap}
                  onChange={(e) => setTenDangNhap(e.target.value)}
                  placeholder="Nhập tên đăng nhập"
                  required
                  disabled={dangDangNhap}
                />
              </div>
            </div>

            <div className="nhom-input">
              <label htmlFor="password">Mật Khẩu</label>
              <div className="input-wrapper">
                <Lock size={20} />
                <input
                  id="password"
                  type={hienMatKhau ? 'text' : 'password'}
                  value={matKhau}
                  onChange={(e) => setMatKhau(e.target.value)}
                  placeholder="Nhập mật khẩu"
                  required
                  disabled={dangDangNhap}
                />
                <button
                  type="button"
                  className="nut-hien-mat-khau"
                  onClick={() => setHienMatKhau(!hienMatKhau)}
                  disabled={dangDangNhap}
                >
                  {hienMatKhau ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {loi && (
              <div className="thong-bao-loi">
                {loi}
              </div>
            )}

            <button 
              type="submit" 
              className="nut-dang-nhap"
              disabled={dangDangNhap || !tenDangNhap || !matKhau}
            >
              {dangDangNhap ? (
                <>
                  <div className="spinner"></div>
                  Đang Đăng Nhập...
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  Đăng Nhập
                </>
              )}
            </button>
          </form>

          <div className="thong-tin-demo">
            <h3>🧪 Tài Khoản Demo</h3>
            <div className="tai-khoan-list">
              <div className="tai-khoan-item">
                <strong>admin</strong> / brain2025
                <span className="vai-tro">Quản trị viên</span>
              </div>
              <div className="tai-khoan-item">
                <strong>manager</strong> / airbnb2025  
                <span className="vai-tro">Quản lý</span>
              </div>
              <div className="tai-khoan-item">
                <strong>user</strong> / pms2025
                <span className="vai-tro">Người dùng</span>
              </div>
            </div>
          </div>
        </div>

        <div className="thong-tin-he-thong">
          <div className="card-thong-tin">
            <h3>🚀 Brain UI System</h3>
            <ul>
              <li>📋 Bảng điều khiển tổng quan dự án</li>
              <li>📑 Trình xem tài liệu markdown</li>
              <li>✅ Quản lý tasks và tiến độ</li>
              <li>🗺️ Domain mapping và workflows</li>
              <li>📱 Giao diện responsive mobile-friendly</li>
            </ul>
          </div>

          <div className="card-bao-mat">
            <h3>🔐 Bảo Mật & Quyền Truy Cập</h3>
            <p>Hệ thống Brain UI được bảo vệ để đảm bảo chỉ những người có thẩm quyền mới có thể truy cập thông tin dự án quan trọng.</p>
            <div className="tinh-nang-bao-mat">
              <span>✅ Xác thực đăng nhập</span>
              <span>✅ Session management</span>
              <span>✅ Local storage security</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DangNhap