import React, { useState, useEffect } from 'react'
import { Home, BarChart3, ExternalLink } from 'lucide-react'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState(null)

  // Sample dashboard data
  const sampleData = {
    project: {
      name: "Airbnb Revenue WebApp",
      version: "1.0.0",
      domain: "Property Management System (PMS)",
      status: "Production Ready",
      last_updated: "2025-09-27",
      tech_stack: ["FastAPI", "SQLAlchemy", "SQLite", "Jinja2", "Alembic"]
    },
    brain_stats: {
      total_files: 12,
      documentation_files: 8,
      active_tasks: 3,
      completed_tasks: 5,
      last_sync: "2025-09-27 00:33"
    },
    quick_links: [
      {
        title: "Project Scope",
        description: "Domain focus và business requirements",
        path: "/scope",
        icon: "📋"
      },
      {
        title: "Active Tasks",
        description: "Current development priorities",
        path: "/tasks",
        icon: "✅"
      },
      {
        title: "Session Context",
        description: "Quick AI onboarding guide",
        path: "/context",
        icon: "🧠"
      },
      {
        title: "Domain Map",
        description: "Business domain architecture",
        path: "/domain",
        icon: "🗺️"
      }
    ],
    recent_activity: [
      {
        action: "Brain Template Integration",
        timestamp: "2025-09-27 00:33",
        description: "Integrated standardized brain system với backup"
      },
      {
        action: "SESSION_CONTEXT.md Created", 
        timestamp: "2025-09-27 00:30",
        description: "Quick AI context loading document"
      },
      {
        action: "Automation Scripts Added",
        timestamp: "2025-09-27 00:25",
        description: "PowerShell scripts for brain setup"
      }
    ]
  }

  useEffect(() => {
    setStats(sampleData)
  }, [])

  if (!stats) {
    return <div className="loading">Đang tải dashboard...</div>
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <div className="project-info">
            <h1>{stats.project.name}</h1>
            <p className="project-domain">{stats.project.domain}</p>
            <div className="project-meta">
              <span className="version">v{stats.project.version}</span>
              <span className="status">{stats.project.status}</span>
              <span className="updated">Updated {stats.project.last_updated}</span>
            </div>
          </div>
          <a 
            href="https://github.com/your-org/airbnb-webapp"
            target="_blank"
            rel="noopener noreferrer"
            className="github-link"
          >
            <ExternalLink size={20} />
            View Repository
          </a>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📁</div>
          <div className="stat-content">
            <h3>{stats.brain_stats.total_files}</h3>
            <p>Brain Files</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📖</div>
          <div className="stat-content">
            <h3>{stats.brain_stats.documentation_files}</h3>
            <p>Documentation</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <h3>{stats.brain_stats.active_tasks}</h3>
            <p>Active Tasks</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{stats.brain_stats.completed_tasks}</h3>
            <p>Completed</p>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="content-grid">
        {/* Quick Links */}
        <div className="content-section">
          <h2>Quick Navigation</h2>
          <div className="quick-links">
            {stats.quick_links.map((link, index) => (
              <a key={index} href={`#${link.path}`} className="quick-link-card">
                <div className="link-icon">{link.icon}</div>
                <div className="link-content">
                  <h3>{link.title}</h3>
                  <p>{link.description}</p>
                </div>
              </a>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="content-section">
          <h2>Technology Stack</h2>
          <div className="tech-stack">
            {stats.project.tech_stack.map((tech, index) => (
              <span key={index} className="tech-badge">{tech}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="content-section">
        <h2>Recent Brain Activity</h2>
        <div className="activity-list">
          {stats.recent_activity.map((activity, index) => (
            <div key={index} className="activity-item">
              <div className="activity-content">
                <h3>{activity.action}</h3>
                <p>{activity.description}</p>
              </div>
              <div className="activity-time">
                {activity.timestamp}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Info */}
      <div className="dashboard-footer">
        <div className="sync-info">
          <BarChart3 size={16} />
          <span>Last brain sync: {stats.brain_stats.last_sync}</span>
        </div>
        <div className="brain-info">
          <Home size={16} />
          <span>Brain System Active</span>
        </div>
      </div>
    </div>
  )
}

export default Dashboard