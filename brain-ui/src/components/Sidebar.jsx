import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  Target, 
  FileText, 
  CheckSquare, 
  Map, 
  Workflow, 
  Shield,
  Book,
  Brain
} from 'lucide-react'
import './Sidebar.css'

const menuItems = [
  {
    section: 'Dashboard',
    items: [
      { icon: Home, label: 'Tổng quan', path: '/' }
    ]
  },
  {
    section: 'Core Documentation',
    items: [
      { icon: Target, label: 'Project Scope', path: '/scope' },
      { icon: Brain, label: 'Session Context', path: '/session-context' },
      { icon: FileText, label: 'Context Index', path: '/context-index' }
    ]
  },
  {
    section: 'Tasks & Planning',
    items: [
      { icon: CheckSquare, label: 'Active Tasks', path: '/tasks' },
      { icon: Map, label: 'Domain Map', path: '/domain-map' },
      { icon: Workflow, label: 'Workflow', path: '/workflow' }
    ]
  },
  {
    section: 'Guidelines',
    items: [
      { icon: Shield, label: 'Copilot Guardrails', path: '/guardrails' },
      { icon: Book, label: 'README', path: '/readme' }
    ]
  }
]

function Sidebar({ isOpen, onClose }) {
  const location = useLocation()

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <Brain size={32} className="logo" />
          <div className="header-text">
            <h1>Brain UI</h1>
            <p>Airbnb WebApp Docs</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map((section, idx) => (
            <div key={idx} className="nav-section">
              <h3 className="section-title">{section.section}</h3>
              <ul className="nav-items">
                {section.items.map((item, itemIdx) => (
                  <li key={itemIdx}>
                    <Link 
                      to={item.path} 
                      className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                      onClick={onClose}
                    >
                      <item.icon size={20} />
                      <span>{item.label}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <p>Version 1.0.0</p>
          <p>Updated: 2025-09-27</p>
        </div>
      </aside>
    </>
  )
}

export default Sidebar