import React, { useState, useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line, Bar, Pie } from 'react-chartjs-2'
import { TrendingUp, BarChart3, PieChart, Download, RefreshCw, FileText, Calendar } from 'lucide-react'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import './BangPhanTich.css'

// Đăng ký Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

function BangPhanTich() {
  const [duLieuDoanhThu, setDuLieuDoanhThu] = useState(null)
  const [duLieuTasks, setDuLieuTasks] = useState(null)
  const [duLieuTongQuan, setDuLieuTongQuan] = useState(null)
  const [dangTai, setDangTai] = useState(true)
  const [loi, setLoi] = useState(null)
  const [bieuDoHienThi, setBieuDoDangHienThi] = useState('tat-ca')
  const [dangXuatFile, setDangXuatFile] = useState(false)

  const dashboardRef = useRef(null)

  // Load dữ liệu từ các file JSON
  const taiDuLieu = async () => {
    setDangTai(true)
    setLoi(null)

    try {
      // Tải dữ liệu doanh thu
      const responseDoanhThu = await fetch('/brain/metrics/revenue-by-month.json')
      if (responseDoanhThu.ok) {
        const dataDoanhThu = await responseDoanhThu.json()
        setDuLieuDoanhThu(dataDoanhThu)
      }

      // Tải dữ liệu tasks
      const responseTasks = await fetch('/brain/ACTIVE_TASKS.json')
      if (responseTasks.ok) {
        const dataTasks = await responseTasks.json()
        setDuLieuTasks(dataTasks)
      }

      // Tải dữ liệu tổng quan
      const responseTongQuan = await fetch('/brain/metrics/project-overview.json')
      if (responseTongQuan.ok) {
        const dataTongQuan = await responseTongQuan.json()
        setDuLieuTongQuan(dataTongQuan)
      }

    } catch (error) {
      console.error('Lỗi tải dữ liệu:', error)
      setLoi('Không thể tải dữ liệu. Vui lòng thử lại.')
    } finally {
      setDangTai(false)
    }
  }

  useEffect(() => {
    taiDuLieu()
  }, [])

  // Cấu hình biểu đồ đường - Doanh thu theo tháng
  const cauHinhBieuDoDoanhThu = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: { family: 'Inter', size: 12 },
          color: 'var(--chu-chinh)'
        }
      },
      title: {
        display: true,
        text: 'Doanh Thu Booking Theo Tháng (VND)',
        font: { family: 'Inter', size: 16, weight: 'bold' },
        color: 'var(--chu-chinh)'
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const value = new Intl.NumberFormat('vi-VN').format(context.parsed.y)
            return `Doanh thu: ${value} VND`
          }
        }
      }
    },
    scales: {
      x: {
        grid: { color: 'var(--vien-nhe)' },
        ticks: { color: 'var(--chu-phu)' }
      },
      y: {
        grid: { color: 'var(--vien-nhe)' },
        ticks: {
          color: 'var(--chu-phu)',
          callback: function (value) {
            return new Intl.NumberFormat('vi-VN', {
              notation: 'compact',
              compactDisplay: 'short'
            }).format(value) + ' VND'
          }
        }
      }
    }
  }

  const duLieuBieuDoDoanhThu = duLieuDoanhThu ? {
    labels: duLieuDoanhThu.data.map(item => item.month),
    datasets: [
      {
        label: 'Doanh Thu',
        data: duLieuDoanhThu.data.map(item => item.revenue),
        borderColor: 'var(--mau-chinh)',
        backgroundColor: 'var(--mau-chinh-nhe)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: 'var(--mau-chinh)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5
      }
    ]
  } : null

  // Cấu hình biểu đồ cột - Tasks theo trạng thái
  const cauHinhBieuDoTasks = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: { family: 'Inter', size: 12 },
          color: 'var(--chu-chinh)'
        }
      },
      title: {
        display: true,
        text: 'Số Lượng Tasks Theo Trạng Thái',
        font: { family: 'Inter', size: 16, weight: 'bold' },
        color: 'var(--chu-chinh)'
      }
    },
    scales: {
      x: {
        grid: { color: 'var(--vien-nhe)' },
        ticks: { color: 'var(--chu-phu)' }
      },
      y: {
        grid: { color: 'var(--vien-nhe)' },
        ticks: {
          color: 'var(--chu-phu)',
          stepSize: 1
        }
      }
    }
  }

  const duLieuBieuDoTasks = duLieuTongQuan ? {
    labels: ['Hoàn Thành', 'Đang Làm', 'Chờ Làm', 'Bị Block'],
    datasets: [
      {
        label: 'Số lượng',
        data: [
          duLieuTongQuan.task_statistics.completed_tasks,
          duLieuTongQuan.task_statistics.in_progress_tasks,
          duLieuTongQuan.task_statistics.pending_tasks,
          duLieuTongQuan.task_statistics.blocked_tasks
        ],
        backgroundColor: [
          'var(--mau-thanh-cong)',
          'var(--mau-chinh)',
          'var(--mau-canh-bao)',
          'var(--mau-loi)'
        ],
        borderColor: [
          'var(--mau-thanh-cong)',
          'var(--mau-chinh)',
          'var(--mau-canh-bao)',
          'var(--mau-loi)'
        ],
        borderWidth: 1
      }
    ]
  } : null

  // Cấu hình biểu đồ tròn - Phases completion
  const cauHinhBieuDoTron = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          font: { family: 'Inter', size: 11 },
          color: 'var(--chu-chinh)',
          padding: 15
        }
      },
      title: {
        display: true,
        text: 'Tỷ Lệ Hoàn Thành Các Phase',
        font: { family: 'Inter', size: 16, weight: 'bold' },
        color: 'var(--chu-chinh)'
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.label}: ${context.parsed}%`
          }
        }
      }
    }
  }

  const duLieuBieuDoTron = duLieuTongQuan ? {
    labels: duLieuTongQuan.phases_completed.map(phase => phase.name),
    datasets: [
      {
        data: duLieuTongQuan.phases_completed.map(phase => phase.completion),
        backgroundColor: [
          '#10b981', '#3b82f6', '#8b5cf6', '#f59e0b',
          '#ef4444', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
        ],
        borderColor: 'var(--nen-the)',
        borderWidth: 2
      }
    ]
  } : null

  // Xuất file PDF
  const xuatPDF = async () => {
    if (!dashboardRef.current) return

    setDangXuatFile(true)

    try {
      const canvas = await html2canvas(dashboardRef.current, {
        scale: 1.5,
        useCORS: true,
        backgroundColor: '#ffffff'
      })

      const imgData = canvas.toDataURL('image/png')
      const pdf = new jsPDF({
        orientation: 'landscape',
        unit: 'mm',
        format: 'a4'
      })

      const imgWidth = 297 // A4 landscape width in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width

      pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight)
      pdf.save(`bang-phan-tich-${new Date().toISOString().split('T')[0]}.pdf`)

    } catch (error) {
      console.error('Lỗi xuất PDF:', error)
      alert('Không thể xuất PDF. Vui lòng thử lại.')
    } finally {
      setDangXuatFile(false)
    }
  }

  // Xuất file PNG
  const xuatPNG = async () => {
    if (!dashboardRef.current) return

    setDangXuatFile(true)

    try {
      const canvas = await html2canvas(dashboardRef.current, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff'
      })

      // Tạo link download
      const link = document.createElement('a')
      link.download = `bang-phan-tich-${new Date().toISOString().split('T')[0]}.png`
      link.href = canvas.toDataURL()
      link.click()

    } catch (error) {
      console.error('Lỗi xuất PNG:', error)
      alert('Không thể xuất PNG. Vui lòng thử lại.')
    } finally {
      setDangXuatFile(false)
    }
  }

  if (dangTai) {
    return (
      <div className="bang-phan-tich">
        <div className="dang-tai-container">
          <RefreshCw size={40} className="spinning" />
          <h2>Đang tải dữ liệu phân tích...</h2>
          <p>Vui lòng chờ trong giây lát</p>
        </div>
      </div>
    )
  }

  if (loi) {
    return (
      <div className="bang-phan-tich">
        <div className="loi-container">
          <h2>⚠️ Lỗi Tải Dữ Liệu</h2>
          <p>{loi}</p>
          <button className="nut-thu-lai" onClick={taiDuLieu}>
            <RefreshCw size={16} />
            Thử Lại
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bang-phan-tich" ref={dashboardRef}>
      <div className="header-phan-tich">
        <div className="thong-tin-header">
          <h1>📊 Bảng Phân Tích Dự Án</h1>
          <p>Dashboard analytics cho Airbnb Revenue WebApp</p>
        </div>
        <div className="nhom-nut-header">
          <button
            className="nut-tai-lai"
            onClick={taiDuLieu}
            disabled={dangTai}
            title="Tải lại dữ liệu"
          >
            <RefreshCw size={16} className={dangTai ? 'spinning' : ''} />
            Tải Lại
          </button>
          <div className="nhom-xuat-file">
            <button
              className="nut-xuat-pdf"
              onClick={xuatPDF}
              disabled={dangXuatFile}
              title="Xuất PDF"
            >
              <FileText size={16} />
              {dangXuatFile ? 'Đang xuất...' : 'Xuất PDF'}
            </button>
            <button
              className="nut-xuat-png"
              onClick={xuatPNG}
              disabled={dangXuatFile}
              title="Xuất PNG"
            >
              <Download size={16} />
              Xuất PNG
            </button>
          </div>
        </div>
      </div>

      {/* Thống kê tổng quan */}
      {duLieuTongQuan && (
        <div className="tong-quan-du-an">
          <div className="card-thong-ke">
            <div className="icon-thong-ke">
              <BarChart3 size={24} />
            </div>
            <div className="chi-tiet-thong-ke">
              <span className="gia-tri-thong-ke">{duLieuTongQuan.task_statistics.total_tasks}</span>
              <span className="nhan-thong-ke">Tổng Tasks</span>
            </div>
          </div>
          <div className="card-thong-ke">
            <div className="icon-thong-ke success">
              <TrendingUp size={24} />
            </div>
            <div className="chi-tiet-thong-ke">
              <span className="gia-tri-thong-ke">{duLieuTongQuan.timeline.overall_progress}%</span>
              <span className="nhan-thong-ke">Tiến Độ</span>
            </div>
          </div>
          <div className="card-thong-ke">
            <div className="icon-thong-ke warning">
              <PieChart size={24} />
            </div>
            <div className="chi-tiet-thong-ke">
              <span className="gia-tri-thong-ke">{duLieuTongQuan.task_statistics.blocked_tasks}</span>
              <span className="nhan-thong-ke">Tasks Bị Block</span>
            </div>
          </div>
          <div className="card-thong-ke">
            <div className="icon-thong-ke info">
              <Calendar size={24} />
            </div>
            <div className="chi-tiet-thong-ke">
              <span className="gia-tri-thong-ke">{duLieuTongQuan.timeline.days_remaining}</span>
              <span className="nhan-thong-ke">Ngày Còn Lại</span>
            </div>
          </div>
        </div>
      )}

      {/* Bộ lọc biểu đồ */}
      <div className="bo-loc-bieu-do">
        <div className="nhom-loc">
          <button
            className={`nut-loc ${bieuDoHienThi === 'tat-ca' ? 'active' : ''}`}
            onClick={() => setBieuDoDangHienThi('tat-ca')}
          >
            Tất Cả
          </button>
          <button
            className={`nut-loc ${bieuDoHienThi === 'doanh-thu' ? 'active' : ''}`}
            onClick={() => setBieuDoDangHienThi('doanh-thu')}
          >
            Doanh Thu
          </button>
          <button
            className={`nut-loc ${bieuDoHienThi === 'tasks' ? 'active' : ''}`}
            onClick={() => setBieuDoDangHienThi('tasks')}
          >
            Tasks
          </button>
          <button
            className={`nut-loc ${bieuDoHienThi === 'phases' ? 'active' : ''}`}
            onClick={() => setBieuDoDangHienThi('phases')}
          >
            Phases
          </button>
        </div>
      </div>

      {/* Biểu đồ */}
      <div className="loi-bieu-do">
        {/* Biểu đồ đường - Doanh thu */}
        {(bieuDoHienThi === 'tat-ca' || bieuDoHienThi === 'doanh-thu') && duLieuBieuDoDoanhThu && (
          <div className="card-bieu-do">
            <div className="header-bieu-do">
              <h3>📈 Biểu Đồ Doanh Thu Theo Tháng</h3>
              {duLieuDoanhThu?.summary && (
                <div className="tong-ket-nho">
                  <span>Tổng: {new Intl.NumberFormat('vi-VN').format(duLieuDoanhThu.summary.total_revenue)} VND</span>
                  <span>ADR TB: {new Intl.NumberFormat('vi-VN').format(duLieuDoanhThu.summary.average_adr)} VND</span>
                </div>
              )}
            </div>
            <div className="container-bieu-do">
              <Line data={duLieuBieuDoDoanhThu} options={cauHinhBieuDoDoanhThu} />
            </div>
          </div>
        )}

        {/* Biểu đồ cột - Tasks */}
        {(bieuDoHienThi === 'tat-ca' || bieuDoHienThi === 'tasks') && duLieuBieuDoTasks && (
          <div className="card-bieu-do">
            <div className="header-bieu-do">
              <h3>📊 Biểu Đồ Tasks Theo Trạng Thái</h3>
              <div className="tong-ket-nho">
                <span>Hoàn thành: {Math.round((duLieuTongQuan.task_statistics.completed_tasks / duLieuTongQuan.task_statistics.total_tasks) * 100)}%</span>
              </div>
            </div>
            <div className="container-bieu-do">
              <Bar data={duLieuBieuDoTasks} options={cauHinhBieuDoTasks} />
            </div>
          </div>
        )}

        {/* Biểu đồ tròn - Phases */}
        {(bieuDoHienThi === 'tat-ca' || bieuDoHienThi === 'phases') && duLieuBieuDoTron && (
          <div className="card-bieu-do">
            <div className="header-bieu-do">
              <h3>🧩 Biểu Đồ Hoàn Thành Các Phase</h3>
              <div className="tong-ket-nho">
                <span>{duLieuTongQuan.phases_completed.length} phases tổng cộng</span>
              </div>
            </div>
            <div className="container-bieu-do pie-chart">
              <Pie data={duLieuBieuDoTron} options={cauHinhBieuDoTron} />
            </div>
          </div>
        )}
      </div>

      {/* Summary cards */}
      {duLieuTongQuan && (
        <div className="bang-tom-tat">
          <div className="card-tom-tat">
            <h4>🎯 Hiệu Suất Dự Án</h4>
            <div className="chi-tiet-tom-tat">
              <div className="dong-tom-tat">
                <span>Chất lượng code:</span>
                <span>{duLieuTongQuan.performance_metrics.code_quality}%</span>
              </div>
              <div className="dong-tom-tat">
                <span>Test coverage:</span>
                <span>{duLieuTongQuan.performance_metrics.test_coverage}%</span>
              </div>
              <div className="dong-tom-tat">
                <span>Documentation:</span>
                <span>{duLieuTongQuan.performance_metrics.documentation}%</span>
              </div>
            </div>
          </div>

          <div className="card-tom-tat">
            <h4>👥 Hoạt Động Team</h4>
            <div className="chi-tiet-tom-tat">
              <div className="dong-tom-tat">
                <span>Commits tuần này:</span>
                <span>{duLieuTongQuan.team_productivity.commits_this_week}</span>
              </div>
              <div className="dong-tom-tat">
                <span>Files thay đổi:</span>
                <span>{duLieuTongQuan.team_productivity.files_changed}</span>
              </div>
              <div className="dong-tom-tat">
                <span>Contributors:</span>
                <span>{duLieuTongQuan.team_productivity.active_contributors}</span>
              </div>
            </div>
          </div>

          {duLieuDoanhThu?.summary && (
            <div className="card-tom-tat">
              <h4>💰 Doanh Thu Highlights</h4>
              <div className="chi-tiet-tom-tat">
                <div className="dong-tom-tat">
                  <span>Tháng tốt nhất:</span>
                  <span>{duLieuDoanhThu.summary.best_month}</span>
                </div>
                <div className="dong-tom-tat">
                  <span>Mùa cao điểm:</span>
                  <span>{duLieuDoanhThu.summary.peak_season}</span>
                </div>
                <div className="dong-tom-tat">
                  <span>Tăng trưởng:</span>
                  <span>+{duLieuDoanhThu.summary.growth_rate}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default BangPhanTich