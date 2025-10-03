import React, { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import ThanhDieuHuong from './components/ThanhDieuHuong'
import BangDieuKhien from './components/BangDieuKhien'
import TrinhXemMarkdown from './components/TrinhXemMarkdown'
import TrinhXemTasks from './components/TrinhXemTasks'
import BangPhanTich from './components/BangPhanTich'
import DangNhap from './components/DangNhap'
import ThongBaoSync from './components/ThongBaoSync'
import { Menu, X } from 'lucide-react'
import './App.css'

function App() {
  const [sidebarMo, setSidebarMo] = useState(false)
  const [daDangNhap, setDaDangNhap] = useState(false)
  const [dangTaiPhien, setDangTaiPhien] = useState(true)

  useEffect(() => {
    // Kiểm tra localStorage để xem user đã đăng nhập chưa
    const phienLamViec = localStorage.getItem('brain-ui-session')
    const thoiGianHetHan = localStorage.getItem('brain-ui-session-expiry')
    
    if (phienLamViec && thoiGianHetHan) {
      const hienTai = new Date().getTime()
      if (hienTai < parseInt(thoiGianHetHan)) {
        setDaDangNhap(true)
      } else {
        // Phiên đã hết hạn
        localStorage.removeItem('brain-ui-session')
        localStorage.removeItem('brain-ui-session-expiry')
        localStorage.removeItem('brain-ui-user-info')
      }
    }
    setDangTaiPhien(false)
  }, [])

  const xuLyDangNhapThanhCong = () => {
    setDaDangNhap(true)
  }

  const xuLyDangXuat = () => {
    localStorage.removeItem('brain-ui-session')
    localStorage.removeItem('brain-ui-session-expiry')
    localStorage.removeItem('brain-ui-user-info')
    setDaDangNhap(false)
  }

  if (dangTaiPhien) {
    return (
      <div className="app loading">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Đang tải Brain UI...</p>
        </div>
      </div>
    )
  }

  if (!daDangNhap) {
    return <DangNhap onDangNhapThanhCong={xuLyDangNhapThanhCong} />
  }

  return (
    <div className="app">
      <button 
        className="nut-menu-mobile"
        onClick={() => setSidebarMo(!sidebarMo)}
      >
        {sidebarMo ? <X size={24} /> : <Menu size={24} />}
      </button>
      
      <ThanhDieuHuong 
        isOpen={sidebarMo} 
        onClose={() => setSidebarMo(false)}
        onDangXuat={xuLyDangXuat}
      />
      
      <main className="noi-dung-chinh">
        <Routes>
          <Route path="/" element={<BangDieuKhien />} />
          <Route path="/analytics" element={<BangPhanTich />} />
          <Route path="/scope" element={<TrinhXemMarkdown file="SCOPE.md" />} />
          <Route path="/session-context" element={<TrinhXemMarkdown file="SESSION_CONTEXT.md" />} />
          <Route path="/context-index" element={<TrinhXemMarkdown file="context/CONTEXT_INDEX.md" />} />
          <Route path="/tasks" element={<TrinhXemTasks />} />
          <Route path="/domain-map" element={<TrinhXemMarkdown file="DOMAIN_MAP.md" />} />
          <Route path="/workflow" element={<TrinhXemMarkdown file="WORKFLOW_SIMPLE.md" />} />
          <Route path="/guardrails" element={<TrinhXemMarkdown file="PLAYBOOKS/COPILOT_GUARDRAILS.md" />} />
          <Route path="/readme" element={<TrinhXemMarkdown file="README.md" />} />
        </Routes>
      </main>
      
      {/* Sync notification system */}
      <ThongBaoSync />
    </div>
  )
}

export default App