import React, { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { ExternalLink, AlertCircle } from 'lucide-react'
import './MarkdownViewer.css'

function MarkdownViewer({ file }) {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Since this is a static site, we'll need to copy brain files to public folder
    // For now, we'll use sample content
    const loadContent = async () => {
      try {
        setLoading(true)

        // Try to fetch from public folder
        const response = await fetch(`/brain/${file}`)
        if (response.ok) {
          const text = await response.text()
          setContent(text)
        } else {
          // Fallback to sample content
          setContent(getSampleContent(file))
        }
      } catch (err) {
        setContent(getSampleContent(file))
      } finally {
        setLoading(false)
      }
    }

    loadContent()
  }, [file])

  const getSampleContent = (filename) => {
    const samples = {
      'SCOPE.md': `# 📋 Airbnb Revenue WebApp - SCOPE DEFINITION

> **Domain**: PMS | **Status**: Production Ready | **Version**: 1.0.0

---

## 🎯 **PROJECT GOALS**

### **Primary Goals**
- [ ] **Revenue Management System**: Quản lý doanh thu từ booking Airbnb với báo cáo theo tháng
- [ ] **CSV Data Processing**: Upload và xử lý file reservations.csv từ Airbnb với normalization tự động  
- [ ] **Property & Booking Tracking**: Theo dõi properties, bookings, và tính toán ADR (Average Daily Rate)

### **Success Criteria**
- **Performance**: Upload CSV < 30 giây, reports load < 5 giây
- **Functionality**: Vietnamese/English CSV headers được parse đúng 100%
- **Quality**: Zero data loss trong quá trình normalization, ADR calculation chính xác

---

## ❌ **NON-GOALS**

- ❌ **Multi-platform Integration**: Chỉ Airbnb, không Booking.com/Expedia
- ❌ **Advanced Analytics**: Chưa có ML, predictive forecasting  
- ❌ **Multi-currency**: Chỉ VND

---

## 🔧 **TECHNICAL SCOPE**

**Tech Stack**: FastAPI + SQLAlchemy + Jinja2 + SQLite
**Key Features**: Vietnamese CSV headers, VND processing, ADR calculation`,

      'SESSION_CONTEXT.md': `# 🧠 SESSION CONTEXT - Airbnb Revenue WebApp

> **Domain**: PMS | **Status**: Production Ready (75%) | **Version**: 1.0.0

---

## 📋 **DỰ ÁN & MỤC TIÊU**

**Dự án**: FastAPI-based web application để quản lý booking và doanh thu từ Airbnb
**Domain**: Property Management System (PMS)

### **🎯 Core Goals**  
- Revenue Management với báo cáo theo tháng
- CSV Processing Vietnamese/English headers
- Property Tracking với ADR calculation

---

## 📦 **TECH STACK**

\`\`\`
Backend: FastAPI + SQLAlchemy + Uvicorn
Frontend: Jinja2 Templates + Bootstrap 5  
Database: SQLite + Alembic migrations
CSV Processing: Pandas + Custom header mapping
\`\`\`

---

## 🛠 **CURRENT TASKS**

**In Progress**: Database Migration Schema Updates (60%)
**Todo**: Enhanced Vietnamese CSV Support`,

      'DOMAIN_MAP.md': `# 🗺️ Airbnb Revenue WebApp - DOMAIN MAP

## 🏗️ **CORE ENTITIES**

### **Booking** (Primary Entity)
- reservation_id, property_id, checkin_date, checkout_date
- total_amount, nights, adr_per_night
- Relations: belongs_to Property, Salesperson

### **Property** (Secondary)  
- building_code, unit_number, property_name
- Relations: has_many Bookings

### **Salesperson** (Supporting)
- salesperson_name, contact_info
- Relations: has_many Bookings

---

## 🔄 **KEY WORKFLOWS**

### **CSV Upload Flow**
1. User uploads reservations.csv
2. utils.py parses Vietnamese/English headers  
3. Data normalization (VND, dates, building codes)
4. Upsert to SQLite database
5. Generate success report

### **Revenue Reporting**
1. Query bookings by date range
2. Calculate ADR (prorated by nights)
3. Group by month/property
4. Render Jinja2 template with charts`,

      'default': `# 📄 ${filename}

Đây là nội dung mẫu cho file **${filename}**.

Để hiển thị nội dung thực tế, bạn cần:
1. Copy các file từ \`.brain/\` vào \`public/brain/\`  
2. Build và deploy static site
3. Files sẽ được load từ server

---

## 📁 Cấu trúc files brain

- **SCOPE.md**: Project scope definition
- **SESSION_CONTEXT.md**: Quick context loading  
- **ACTIVE_TASKS.json**: Current tasks tracking
- **DOMAIN_MAP.md**: Domain entities mapping
- **PLAYBOOKS/**: Development guidelines`
    }

    return samples[filename] || samples['default']
  }

  const getGitHubLink = () => {
    const baseUrl = 'https://github.com/your-org/airbnb-webapp/blob/main/.brain'
    return `${baseUrl}/${file}`
  }

  if (loading) {
    return <div className="loading">Đang tải nội dung...</div>
  }

  if (error) {
    return (
      <div className="error">
        <AlertCircle size={24} />
        <p>Không thể tải file {file}</p>
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div className="markdown-viewer">
      <div className="viewer-header">
        <h1>{file}</h1>
        <a
          href={getGitHubLink()}
          target="_blank"
          rel="noopener noreferrer"
          className="external-link"
        >
          <ExternalLink size={16} />
          Xem file gốc
        </a>
      </div>

      <div className="markdown-content">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  )
}

export default MarkdownViewer