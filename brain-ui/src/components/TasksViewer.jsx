import React, { useState, useEffect } from 'react'
import { Filter, Search, ExternalLink } from 'lucide-react'
import './TasksViewer.css'

function TasksViewer() {
  const [tasks, setTasks] = useState(null)
  const [filteredTasks, setFilteredTasks] = useState([])
  const [statusFilter, setStatusFilter] = useState('all')
  const [priorityFilter, setPriorityFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  // Sample tasks data - in real app, this would come from ACTIVE_TASKS.json
  const sampleTasks = {
    project: {
      name: "Airbnb Revenue WebApp",
      version: "1.0.0",
      domain: "PMS",
      status: "Production Ready",
      last_updated: "2025-09-27"
    },
    active_tasks: [
      {
        id: "MAINT-001",
        title: "Database Migration Schema Updates",
        description: "Maintain and update database schema cho expense categories và extra charges",
        status: "In Progress",
        priority: "Medium",
        assigned_to: "Development Team",
        due_date: "2025-10-15",
        progress: "60%"
      },
      {
        id: "FEAT-002",
        title: "Enhanced Vietnamese CSV Support",
        description: "Cải thiện parsing Vietnamese headers trong CSV files từ Airbnb",
        status: "Todo",
        priority: "Low",
        assigned_to: "Development Team",
        due_date: "2025-11-01",
        progress: "0%"
      },
      {
        id: "OPT-003",
        title: "Performance Optimization Reports",
        description: "Tối ưu performance cho monthly revenue reports với large datasets",
        status: "Todo",
        priority: "Low",
        assigned_to: "Development Team",
        due_date: "2025-12-01",
        progress: "0%"
      }
    ],
    metrics: {
      total_tasks: 5,
      completed_tasks: 3,
      in_progress_tasks: 1,
      completion_percentage: 75
    }
  }

  useEffect(() => {
    // Load tasks - in real app, fetch from /brain/tasks/ACTIVE_TASKS.json
    setTasks(sampleTasks)
    setFilteredTasks(sampleTasks.active_tasks)
  }, [])

  useEffect(() => {
    if (!tasks) return

    let filtered = tasks.active_tasks

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(task => task.status.toLowerCase() === statusFilter)
    }

    // Filter by priority  
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(task => task.priority.toLowerCase() === priorityFilter)
    }

    // Search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      filtered = filtered.filter(task =>
        task.title.toLowerCase().includes(search) ||
        task.description.toLowerCase().includes(search) ||
        task.id.toLowerCase().includes(search)
      )
    }

    setFilteredTasks(filtered)
  }, [tasks, statusFilter, priorityFilter, searchTerm])

  const getPriorityClass = (priority) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'priority-high'
      case 'medium': return 'priority-medium'
      case 'low': return 'priority-low'
      default: return 'priority-medium'
    }
  }

  const getStatusClass = (status) => {
    switch (status.toLowerCase()) {
      case 'done': return 'status-done'
      case 'in progress': return 'status-progress'
      case 'todo': return 'status-todo'
      case 'blocked': return 'status-blocked'
      default: return 'status-todo'
    }
  }

  if (!tasks) {
    return <div className="loading">Đang tải tasks...</div>
  }

  return (
    <div className="tasks-viewer">
      <div className="tasks-header">
        <div className="header-info">
          <h1>Active Tasks</h1>
          <p>{tasks.project.name} - {tasks.project.domain}</p>
        </div>
        <a
          href="https://github.com/your-org/airbnb-webapp/blob/main/.brain/tasks/ACTIVE_TASKS.json"
          target="_blank"
          rel="noopener noreferrer"
          className="external-link"
        >
          <ExternalLink size={16} />
          Xem file JSON
        </a>
      </div>

      {/* Project Metrics */}
      <div className="project-metrics">
        <div className="metric">
          <span className="metric-value">{tasks.metrics.total_tasks}</span>
          <span className="metric-label">Total Tasks</span>
        </div>
        <div className="metric">
          <span className="metric-value">{tasks.metrics.completed_tasks}</span>
          <span className="metric-label">Completed</span>
        </div>
        <div className="metric">
          <span className="metric-value">{tasks.metrics.in_progress_tasks}</span>
          <span className="metric-label">In Progress</span>
        </div>
        <div className="metric">
          <span className="metric-value">{tasks.metrics.completion_percentage}%</span>
          <span className="metric-label">Complete</span>
        </div>
      </div>

      {/* Filters */}
      <div className="filters">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Tìm kiếm tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <Filter size={16} />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="todo">Todo</option>
            <option value="in progress">In Progress</option>
            <option value="done">Done</option>
            <option value="blocked">Blocked</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="all">Tất cả mức độ</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Tasks Table */}
      <div className="tasks-table">
        <div className="table-header">
          <div className="col-id">ID</div>
          <div className="col-title">Title</div>
          <div className="col-status">Status</div>
          <div className="col-priority">Priority</div>
          <div className="col-progress">Progress</div>
          <div className="col-due">Due Date</div>
        </div>

        {filteredTasks.length === 0 ? (
          <div className="no-tasks">Không tìm thấy task nào phù hợp</div>
        ) : (
          filteredTasks.map(task => (
            <div key={task.id} className="task-row">
              <div className="col-id">
                <span className="task-id">{task.id}</span>
              </div>
              <div className="col-title">
                <h3>{task.title}</h3>
                <p>{task.description}</p>
              </div>
              <div className="col-status">
                <span className={`status-badge ${getStatusClass(task.status)}`}>
                  {task.status}
                </span>
              </div>
              <div className="col-priority">
                <span className={`priority-badge ${getPriorityClass(task.priority)}`}>
                  {task.priority}
                </span>
              </div>
              <div className="col-progress">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: task.progress }}
                  />
                </div>
                <span className="progress-text">{task.progress}</span>
              </div>
              <div className="col-due">
                {task.due_date}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default TasksViewer