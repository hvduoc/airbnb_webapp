import React, { useState, useEffect } from 'react'
import { RefreshCw, CheckCircle, AlertCircle, Clock, X } from 'lucide-react'
import './ThongBaoSync.css'

function ThongBaoSync() {
  const [trangThaiSync, setTrangThaiSync] = useState(null)
  const [dangKiemTra, setDangKiemTra] = useState(false)
  const [hienThongBao, setHienThongBao] = useState(false)
  const [lichSuSync, setLichSuSync] = useState([])

  const WEBHOOK_API = 'http://localhost:8002'

  const kiemTraTrangThaiSync = async () => {
    try {
      setDangKiemTra(true)
      const response = await fetch(`${WEBHOOK_API}/api/sync/status`)
      const data = await response.json()
      
      if (data.latest_sync) {
        setTrangThaiSync(data.latest_sync)
        
        // Hiển thị notification nếu có sync mới trong 1 phút gần đây
        const syncTime = new Date(data.latest_sync.timestamp)
        const now = new Date()
        const diffMinutes = (now - syncTime) / (1000 * 60)
        
        if (diffMinutes < 1 && data.latest_sync.status === 'success') {
          setHienThongBao(true)
          setTimeout(() => setHienThongBao(false), 5000)
        }
      }
    } catch (error) {
      console.error('Error checking sync status:', error)
    } finally {
      setDangKiemTra(false)
    }
  }

  const layLichSuSync = async () => {
    try {
      const response = await fetch(`${WEBHOOK_API}/api/sync/history`)
      const data = await response.json()
      setLichSuSync(data.history || [])
    } catch (error) {
      console.error('Error fetching sync history:', error)
    }
  }

  const thucHienSyncThuCong = async () => {
    try {
      setDangKiemTra(true)
      await fetch(`${WEBHOOK_API}/api/sync/manual`, { method: 'POST' })
      
      // Đợi 2 giây rồi kiểm tra status
      setTimeout(() => {
        kiemTraTrangThaiSync()
        layLichSuSync()
      }, 2000)
      
    } catch (error) {
      console.error('Error triggering manual sync:', error)
    }
  }

  useEffect(() => {
    // Kiểm tra status lần đầu
    kiemTraTrangThaiSync()
    layLichSuSync()

    // Kiểm tra định kỳ mỗi 30 giây
    const interval = setInterval(kiemTraTrangThaiSync, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const formatThoiGian = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleString('vi-VN')
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle size={16} className="text-green-500" />
      case 'error':
        return <AlertCircle size={16} className="text-red-500" />
      default:
        return <Clock size={16} className="text-yellow-500" />
    }
  }

  return (
    <div className="thong-bao-sync-container">
      {/* Notification Toast */}
      {hienThongBao && (
        <div className="notification-toast">
          <div className="toast-content">
            <CheckCircle size={20} />
            <div>
              <div className="toast-title">🧠 Brain Data Đã Cập Nhật!</div>
              <div className="toast-message">Dữ liệu mới nhất đã được đồng bộ từ GitHub</div>
            </div>
          </div>
          <button 
            className="toast-close"
            onClick={() => setHienThongBao(false)}
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* Sync Status Widget */}
      <div className="sync-status-widget">
        <div className="sync-header">
          <h4>🔄 Trạng Thái Đồng Bộ</h4>
          <button 
            className={`btn-refresh ${dangKiemTra ? 'spinning' : ''}`}
            onClick={thucHienSyncThuCong}
            disabled={dangKiemTra}
            title="Đồng bộ thủ công"
          >
            <RefreshCw size={16} />
          </button>
        </div>

        {trangThaiSync && (
          <div className="sync-status">
            <div className="status-row">
              {getStatusIcon(trangThaiSync.status)}
              <span className={`status-text ${trangThaiSync.status}`}>
                {trangThaiSync.status === 'success' ? 'Thành công' : 
                 trangThaiSync.status === 'error' ? 'Lỗi' : 'Đang xử lý'}
              </span>
              <span className="sync-time">
                {formatThoiGian(trangThaiSync.timestamp)}
              </span>
            </div>
            
            <div className="sync-details">
              <div className="commit-info">
                <strong>Commit:</strong> {trangThaiSync.commit_sha?.substring(0, 8)}
              </div>
              <div className="commit-message">
                {trangThaiSync.commit_message}
              </div>
              <div className="author">
                <strong>Author:</strong> {trangThaiSync.author}
              </div>
              
              {trangThaiSync.files_changed?.length > 0 && (
                <div className="files-changed">
                  <strong>Files:</strong> {trangThaiSync.files_changed.join(', ')}
                </div>
              )}
              
              {trangThaiSync.error && (
                <div className="error-message">
                  <strong>Lỗi:</strong> {trangThaiSync.error}
                </div>
              )}
            </div>
          </div>
        )}

        {!trangThaiSync && !dangKiemTra && (
          <div className="no-sync-data">
            Chưa có dữ liệu đồng bộ
          </div>
        )}

        {dangKiemTra && (
          <div className="loading-sync">
            <RefreshCw size={16} className="spinning" />
            <span>Đang kiểm tra...</span>
          </div>
        )}
      </div>

      {/* Sync History */}
      {lichSuSync.length > 0 && (
        <div className="sync-history">
          <h5>📝 Lịch Sử Sync</h5>
          <div className="history-list">
            {lichSuSync.slice(-5).reverse().map((sync, index) => (
              <div key={index} className={`history-item ${sync.status}`}>
                <div className="history-header">
                  {getStatusIcon(sync.status)}
                  <span className="history-time">
                    {formatThoiGian(sync.timestamp)}
                  </span>
                </div>
                <div className="history-details">
                  <div className="commit-short">
                    {sync.commit_sha?.substring(0, 8)} - {sync.commit_message?.substring(0, 50)}...
                  </div>
                  {sync.files_changed?.length > 0 && (
                    <div className="files-count">
                      {sync.files_changed.length} file(s) changed
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ThongBaoSync