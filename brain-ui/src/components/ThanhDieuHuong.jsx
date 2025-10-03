import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, FileText, CheckSquare, Map, Book, Settings, ExternalLink, ChevronDown, ChevronRight, LogOut, User, BarChart3 } from 'lucide-react'
import './ThanhDieuHuong.css'

function ThanhDieuHuong({ isOpen, onClose, onDangXuat }) {
  const location = useLocation()
  const [thongTinUser, setThongTinUser] = useState(null)
  const [expandedSections, setExpandedSections] = useState({
    'tai-lieu': true,
    'tasks': true,
    'cau-hinh': false
  })

  useEffect(() => {
    const userInfo = localStorage.getItem('brain-ui-user-info')
    if (userInfo) {
      setThongTinUser(JSON.parse(userInfo))
    }
  }, [])

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const xuLyDangXuat = () => {
    if (onDangXuat) {
      onDangXuat()
    }
    if (onClose) {
      onClose()
    }
  }

  const mucMenu = [
    {
      nhom: 'Tổng Quan',
      items: [
        {
          duongDan: '/',
          nhan: 'Bảng Điều Khiển',
          icon: <Home size={18} />,
          moTa: 'Trang chủ và tổng quan dự án'
        },
        {
          duongDan: '/analytics',
          nhan: 'Bảng Phân Tích',
          icon: <BarChart3 size={18} />,
          moTa: 'Dashboard analytics và báo cáo'
        }
      ]
    },
    {
      nhom: 'Tài Liệu',
      key: 'tai-lieu',
      items: [
        {
          duongDan: '/scope',
          nhan: 'Phạm Vi Dự Án',
          icon: <FileText size={18} />,
          moTa: 'Định nghĩa scope và domain'
        },
        {
          duongDan: '/session-context',
          nhan: 'Ngữ Cảnh Session',
          icon: <Book size={18} />,
          moTa: 'Context nhanh cho AI'
        },
        {
          duongDan: '/domain-map',
          nhan: 'Bản Đồ Domain',
          icon: <Map size={18} />,
          moTa: 'Kiến trúc business domain'
        },
        {
          duongDan: '/workflow',
          nhan: 'Quy Trình Làm Việc',
          icon: <Settings size={18} />,
          moTa: 'Workflow và quy trình'
        }
      ]
    },
    {
      nhom: 'Quản Lý Tasks',
      key: 'tasks',
      items: [
        {
          duongDan: '/tasks',
          nhan: 'Tasks Đang Hoạt Động',
          icon: <CheckSquare size={18} />,
          moTa: 'Danh sách task hiện tại'
        }
      ]
    }
  ]

  const linkNgoai = [
    {
      nhan: 'Repository GitHub',
      url: 'https://github.com/your-org/airbnb-webapp',
      icon: <ExternalLink size={16} />
    },
    {
      nhan: 'Tài Liệu API',
      url: 'http://localhost:8000/docs',
      icon: <ExternalLink size={16} />
    }
  ]

  return (
    <>
      {isOpen && <div className="overlay" onClick={onClose} />}
      
      <aside className={`thanh-dieu-huong ${isOpen ? 'mo' : ''}`}>
        <div className="header-sidebar">
          <div className="logo">
            <span className="logo-icon">🧠</span>
            <span className="logo-text">Brain UI</span>
          </div>
          <div className="project-info">
            <h3>Airbnb Revenue WebApp</h3>
            <span className="version">v1.0.0</span>
          </div>
        </div>

        <nav className="menu-chinh">
          {mucMenu.map((nhom, index) => (
            <div key={index} className="nhom-menu">
              <div 
                className="tieu-de-nhom"
                onClick={() => nhom.key && toggleSection(nhom.key)}
              >
                <span>{nhom.nhom}</span>
                {nhom.key && (
                  expandedSections[nhom.key] ? 
                    <ChevronDown size={16} /> : 
                    <ChevronRight size={16} />
                )}
              </div>
              
              {(!nhom.key || expandedSections[nhom.key]) && (
                <ul className="danh-sach-menu">
                  {nhom.items.map((item, itemIndex) => (
                    <li key={itemIndex}>
                      <Link
                        to={item.duongDan}
                        className={`muc-menu ${location.pathname === item.duongDan ? 'active' : ''}`}
                        onClick={onClose}
                        title={item.moTa}
                      >
                        <span className="icon">{item.icon}</span>
                        <span className="nhan">{item.nhan}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </nav>

        <div className="phan-footer">
          <div className="thong-tin-user">
            {thongTinUser && (
              <div className="user-card">
                <div className="user-avatar">
                  <User size={16} />
                </div>
                <div className="user-info">
                  <div className="user-name">{thongTinUser.tenHienThi}</div>
                  <div className="user-role">{thongTinUser.vaiTro}</div>
                </div>
                <button 
                  className="nut-dang-xuat"
                  onClick={xuLyDangXuat}
                  title="Đăng xuất"
                >
                  <LogOut size={16} />
                </button>
              </div>
            )}
          </div>

          <div className="lien-ket-ngoai">
            <h4>Liên Kết Ngoài</h4>
            {linkNgoai.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="link-ngoai"
              >
                <span className="nhan">{link.nhan}</span>
                {link.icon}
              </a>
            ))}
          </div>
          
          <div className="thong-tin-brain">
            <div className="trang-thai">
              <span className="dot active"></span>
              <span>Brain System Hoạt Động</span>
            </div>
            <div className="cap-nhat">
              Cập nhật: 27/09/2025
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

export default ThanhDieuHuong