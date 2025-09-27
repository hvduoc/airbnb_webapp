import React, { useState, useEffect } from 'react'
import { Filter, Search, ExternalLink, Edit, Save, X, RefreshCw } from 'lucide-react'
import './TrinhXemTasks.css'
import './TrinhXemTasks-Enhanced.css'

function TrinhXemTasks() {
  const [tasks, setTasks] = useState(null)
  const [tasksLoc, setTasksLoc] = useState([])
  const [locTrangThai, setLocTrangThai] = useState('tat-ca')
  const [locUuTien, setLocUuTien] = useState('tat-ca')
  const [tuKhoaTimKiem, setTuKhoaTimKiem] = useState('')
  const [taskDangSua, setTaskDangSua] = useState(null)
  const [dangCapNhat, setDangCapNhat] = useState(false)

  const trangThaiOptions = [
    { value: 'pending', label: 'Cần Làm', class: 'trang-thai-can-lam' },
    { value: 'in_progress', label: 'Đang Thực Hiện', class: 'trang-thai-dang-lam' },
    { value: 'completed', label: 'Hoàn Thành', class: 'trang-thai-hoan-thanh' },
    { value: 'blocked', label: 'Bị Block', class: 'trang-thai-block' },
    { value: 'cancelled', label: 'Đã Hủy', class: 'trang-thai-huy' }
  ]

  const uuTienOptions = [
    { value: 'high', label: 'Cao', class: 'uu-tien-cao' },
    { value: 'medium', label: 'Trung Bình', class: 'uu-tien-trung-binh' },
    { value: 'low', label: 'Thấp', class: 'uu-tien-thap' }
  ]

  // Dữ liệu tasks mẫu
  const duLieuTasksMau = {
    duAn: {
      ten: "Airbnb Revenue WebApp",
      phienBan: "1.0.0",
      domain: "PMS",
      trangThai: "Sẵn Sàng Production",
      capNhatCuoi: "27/09/2025"
    },
    tasks_hoat_dong: [
      {
        id: "MAINT-001",
        tieuDe: "Cập Nhật Schema Database Migration",
        moTa: "Maintain và update database schema cho expense categories và extra charges",
        trangThai: "Đang Thực Hiện",
        uuTien: "Trung Bình", 
        phanCong: "Development Team",
        hanCuoi: "15/10/2025",
        tienDo: "60%"
      },
      {
        id: "FEAT-002",
        tieuDe: "Tăng Cường Hỗ Trợ CSV Tiếng Việt", 
        moTa: "Cải thiện parsing Vietnamese headers trong CSV files từ Airbnb",
        trangThai: "Cần Làm",
        uuTien: "Thấp",
        phanCong: "Development Team", 
        hanCuoi: "01/11/2025",
        tienDo: "0%"
      },
      {
        id: "OPT-003",
        tieuDe: "Tối Ưu Performance Reports",
        moTa: "Tối ưu performance cho monthly revenue reports với large datasets", 
        trangThai: "Cần Làm",
        uuTien: "Thấp",
        phanCong: "Development Team",
        hanCuoi: "01/12/2025", 
        tienDo: "0%"
      },
      {
        id: "UI-004",
        tieuDe: "Brain UI System Hoàn Chỉnh",
        moTa: "Hoàn thiện React UI để hiển thị nội dung .brain/ với interface tiếng Việt", 
        trangThai: "Đang Thực Hiện",
        uuTien: "Cao",
        phanCong: "Frontend Team",
        hanCuoi: "30/09/2025", 
        tienDo: "85%"
      },
      {
        id: "DOC-005",
        tieuDe: "Cập Nhật Tài Liệu API",
        moTa: "Hoàn thiện documentation cho FastAPI endpoints với examples", 
        trangThai: "Hoàn Thành",
        uuTien: "Trung Bình",
        phanCong: "Development Team",
        hanCuoi: "25/09/2025", 
        tienDo: "100%"
      }
    ],
    thongKe: {
      tongTasks: 5,
      tasksHoanThanh: 1,
      tasksDangLam: 2,
      phanTramHoanThanh: 20
    }
  }

  // Load tasks từ API hoặc file JSON
  const loadTasks = async () => {
    try {
      // Thử load từ real data trước
      const response = await fetch('/brain/ACTIVE_TASKS.json')
      if (response.ok) {
        const realData = await response.json()
        setTasks(realData)
        
        // Flatten all tasks from all phases
        const allTasks = []
        if (realData.phases) {
          realData.phases.forEach(phase => {
            if (phase.tasks) {
              phase.tasks.forEach(task => {
                allTasks.push({
                  ...task,
                  phaseName: phase.phase_name
                })
              })
            }
          })
        }
        setTasksLoc(allTasks)
        return
      }
    } catch (error) {
      console.warn('Could not load real tasks, using sample data:', error)
    }

    // Fallback to sample data
    setTasks(duLieuTasksMau)
    setTasksLoc(duLieuTasksMau.tasks_hoat_dong)
  }

  const capNhatTrangThaiTask = async (taskId, newStatus, comment = '') => {
    setDangCapNhat(true)
    
    try {
      // Simulate API call - trong thực tế sẽ gọi backend API
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Update local state
      const updatedTasks = tasksLoc.map(task => {
        if (task.id === taskId) {
          const updatedTask = {
            ...task,
            status: newStatus,
            updated_at: new Date().toISOString(),
            progress: getProgressByStatus(newStatus)
          }
          
          // Add comment if provided
          if (comment) {
            if (!updatedTask.comments) {
              updatedTask.comments = []
            }
            updatedTask.comments.push({
              timestamp: new Date().toISOString(),
              comment: comment,
              status_change: `${task.status} → ${newStatus}`
            })
          }
          
          return updatedTask
        }
        return task
      })
      
      setTasksLoc(updatedTasks)
      setTaskDangSua(null)
      
      // Show success message (có thể thêm toast notification)
      console.log(`Task ${taskId} updated to ${newStatus}`)
      
    } catch (error) {
      console.error('Error updating task:', error)
      alert('Lỗi cập nhật task. Vui lòng thử lại.')
    } finally {
      setDangCapNhat(false)
    }
  }

  const getProgressByStatus = (status) => {
    switch (status) {
      case 'pending': return 0
      case 'in_progress': return 50
      case 'completed': return 100
      case 'blocked': return 25
      case 'cancelled': return 0
      default: return 0
    }
  }

  const getTrangThaiLabel = (status) => {
    const option = trangThaiOptions.find(opt => opt.value === status)
    return option ? option.label : status
  }

  const getTrangThaiClass = (status) => {
    const option = trangThaiOptions.find(opt => opt.value === status)
    return option ? option.class : 'trang-thai-can-lam'
  }

  const getUuTienLabel = (priority) => {
    const option = uuTienOptions.find(opt => opt.value === priority)
    return option ? option.label : priority
  }

  const getUuTienClass = (priority) => {
    const option = uuTienOptions.find(opt => opt.value === priority)
    return option ? option.class : 'uu-tien-trung-binh'
  }

  useEffect(() => {
    loadTasks()
  }, [])

  useEffect(() => {
    if (!tasks && !tasksLoc.length) return

    let filtered = tasksLoc

    // Lọc theo trạng thái
    if (locTrangThai !== 'tat-ca') {
      filtered = filtered.filter(task => task.status === locTrangThai)
    }

    // Lọc theo ưu tiên  
    if (locUuTien !== 'tat-ca') {
      filtered = filtered.filter(task => task.priority === locUuTien)
    }

    // Tìm kiếm
    if (tuKhoaTimKiem) {
      const search = tuKhoaTimKiem.toLowerCase()
      filtered = filtered.filter(task => 
        task.title?.toLowerCase().includes(search) ||
        task.description?.toLowerCase().includes(search) ||
        task.id?.toLowerCase().includes(search)
      )
    }

    // Only update if we have the original data
    if (tasks || tasksLoc.length > 0) {
      // Don't overwrite tasksLoc if we're filtering from it directly
      if (tasks && filtered !== tasksLoc) {
        setTasksLoc(filtered)
      }
    }
  }, [locTrangThai, locUuTien, tuKhoaTimKiem])

  const layClassUuTien = (uuTien) => {
    switch (uuTien.toLowerCase()) {
      case 'cao': return 'uu-tien-cao'
      case 'trung bình': return 'uu-tien-trung-binh'  
      case 'thấp': return 'uu-tien-thap'
      default: return 'uu-tien-trung-binh'
    }
  }

  const layClassTrangThai = (trangThai) => {
    switch (trangThai.toLowerCase()) {
      case 'hoàn thành': return 'trang-thai-hoan-thanh'
      case 'đang thực hiện': return 'trang-thai-dang-lam'
      case 'cần làm': return 'trang-thai-can-lam'
      case 'bị block': return 'trang-thai-block'
      default: return 'trang-thai-can-lam'
    }
  }

  if (!tasks) {
    return <div className="dang-tai">Đang tải tasks...</div>
  }

  return (
    <div className="trinh-xem-tasks">
      <div className="header-tasks">
        <div className="thong-tin-header">
          <h1>Tasks Đang Hoạt Động</h1>
          <p>{tasks?.duAn?.ten || 'Airbnb Revenue WebApp'} - Tasks Management</p>
        </div>
        <div className="nhom-nut-header">
          <button 
            className="nut-tai-lai"
            onClick={loadTasks}
            disabled={dangCapNhat}
            title="Tải lại tasks"
          >
            <RefreshCw size={16} className={dangCapNhat ? 'spinning' : ''} />
            Tải Lại
          </button>
          <a 
            href="/brain/ACTIVE_TASKS.json"
            target="_blank"
            rel="noopener noreferrer" 
            className="link-ngoai"
          >
            <ExternalLink size={16} />
            Xem File JSON
          </a>
        </div>
      </div>

      {/* Thống Kê Tasks */}
      <div className="thong-ke-tasks">
        {(() => {
          const stats = {
            total: tasksLoc.length,
            completed: tasksLoc.filter(t => t.status === 'completed').length,
            in_progress: tasksLoc.filter(t => t.status === 'in_progress').length,
            pending: tasksLoc.filter(t => t.status === 'pending').length,
            blocked: tasksLoc.filter(t => t.status === 'blocked').length
          }
          const percentage = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0

          return (
            <>
              <div className="muc-thong-ke">
                <span className="gia-tri-thong-ke">{stats.total}</span>
                <span className="nhan-thong-ke">Tổng Tasks</span>
              </div>
              <div className="muc-thong-ke">
                <span className="gia-tri-thong-ke text-green">{stats.completed}</span>
                <span className="nhan-thong-ke">Hoàn Thành</span>
              </div>
              <div className="muc-thong-ke">
                <span className="gia-tri-thong-ke text-blue">{stats.in_progress}</span>
                <span className="nhan-thong-ke">Đang Làm</span>
              </div>
              <div className="muc-thong-ke">
                <span className="gia-tri-thong-ke text-yellow">{stats.pending}</span>
                <span className="nhan-thong-ke">Chờ Làm</span>
              </div>
              <div className="muc-thong-ke">
                <span className="gia-tri-thong-ke text-orange">{percentage}%</span>
                <span className="nhan-thong-ke">Tiến Độ</span>
              </div>
            </>
          )
        })()}
      </div>

      {/* Bộ Lọc */}
      <div className="bo-loc">
        <div className="hop-tim-kiem">
          <Search size={20} />
          <input
            type="text"
            placeholder="Tìm kiếm tasks..."
            value={tuKhoaTimKiem}
            onChange={(e) => setTuKhoaTimKiem(e.target.value)}
          />
        </div>
        
        <div className="nhom-loc">
          <Filter size={16} />
          <select 
            value={locTrangThai} 
            onChange={(e) => setLocTrangThai(e.target.value)}
          >
            <option value="tat-ca">Tất cả trạng thái</option>
            {trangThaiOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          
          <select
            value={locUuTien}
            onChange={(e) => setLocUuTien(e.target.value)}
          >
            <option value="tat-ca">Tất cả mức độ</option>
            {uuTienOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Bảng Tasks */}
      <div className="bang-tasks">
        <div className="header-bang">
          <div className="cot-id">ID</div>
          <div className="cot-tieu-de">Tiêu Đề</div>
          <div className="cot-trang-thai">Trạng Thái</div>
          <div className="cot-uu-tien">Ưu Tiên</div>
          <div className="cot-tien-do">Tiến Độ</div>
          <div className="cot-assignee">Người Làm</div>
          <div className="cot-actions">Thao Tác</div>
        </div>
        
        {tasksLoc.length === 0 ? (
          <div className="khong-co-tasks">
            {dangCapNhat ? 'Đang cập nhật...' : 'Không tìm thấy task nào phù hợp'}
          </div>
        ) : (
          tasksLoc.map(task => (
            <div key={task.id} className="dong-task">
              <div className="cot-id">
                <span className="id-task">{task.id}</span>
                {task.phaseName && (
                  <span className="phase-name">{task.phaseName}</span>
                )}
              </div>
              <div className="cot-tieu-de">
                <h3>{task.title}</h3>
                <p>{task.description}</p>
                {task.comments && task.comments.length > 0 && (
                  <div className="latest-comment">
                    💬 {task.comments[task.comments.length - 1].comment}
                  </div>
                )}
              </div>
              <div className="cot-trang-thai">
                {taskDangSua === task.id ? (
                  <select
                    value={task.status}
                    onChange={(e) => {
                      const newTasks = tasksLoc.map(t => 
                        t.id === task.id ? { ...t, status: e.target.value } : t
                      )
                      setTasksLoc(newTasks)
                    }}
                    disabled={dangCapNhat}
                  >
                    {trangThaiOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className={`huy-hieu-trang-thai ${getTrangThaiClass(task.status)}`}>
                    {getTrangThaiLabel(task.status)}
                  </span>
                )}
              </div>
              <div className="cot-uu-tien">
                <span className={`huy-hieu-uu-tien ${getUuTienClass(task.priority)}`}>
                  {getUuTienLabel(task.priority)}
                </span>
              </div>
              <div className="cot-tien-do">
                <div className="thanh-tien-do">
                  <div 
                    className="do-tien-do"
                    style={{ width: `${task.progress || 0}%` }}
                  />
                </div>
                <span className="text-tien-do">{task.progress || 0}%</span>
              </div>
              <div className="cot-assignee">
                {task.assignee || 'Chưa phân công'}
              </div>
              <div className="cot-actions">
                {taskDangSua === task.id ? (
                  <div className="nhom-nut-sua">
                    <button
                      className="nut-luu"
                      onClick={() => capNhatTrangThaiTask(task.id, task.status)}
                      disabled={dangCapNhat}
                      title="Lưu thay đổi"
                    >
                      <Save size={16} />
                    </button>
                    <button
                      className="nut-huy"
                      onClick={() => {
                        setTaskDangSua(null)
                        loadTasks() // Reload to reset changes
                      }}
                      disabled={dangCapNhat}
                      title="Hủy thay đổi"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ) : (
                  <button
                    className="nut-sua"
                    onClick={() => setTaskDangSua(task.id)}
                    disabled={dangCapNhat}
                    title="Sửa trạng thái"
                  >
                    <Edit size={16} />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default TrinhXemTasks