import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { ExternalLink, FileText } from 'lucide-react'
import './TrinhXemMarkdown.css'

function TrinhXemMarkdown({ file }) {
  const { fileName } = useParams()
  const [noiDung, setNoiDung] = useState('')
  const [dangTai, setDangTai] = useState(true)
  const [loi, setLoi] = useState(null)
  
  const tenFile = file || fileName || 'README.md'

  // Dữ liệu markdown mẫu cho các file khác nhau
  const duLieuMau = {
    'SCOPE.md': `# Phạm Vi Dự Án (SCOPE)

## 🎯 Mục Tiêu Chính

**Airbnb Revenue WebApp** là hệ thống quản lý doanh thu và booking cho các tài sản Airbnb, tập trung vào domain **Property Management System (PMS)**.

## 🏢 Domain Business

### Core Functions
- **Booking Management**: Quản lý đặt phòng từ Airbnb CSV uploads
- **Revenue Tracking**: Theo dõi doanh thu theo tháng với ADR (Average Daily Rate)
- **Expense Management**: Quản lý chi phí vận hành
- **Property Portfolio**: Quản lý danh mục tài sản

### Vietnamese Market Focus
- Hỗ trợ CSV headers tiếng Việt từ Airbnb Vietnam
- Parsing VND currency và date formats Việt Nam
- Xử lý building codes và unit numbers theo chuẩn VN

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM và database management
- **SQLite** - Lightweight database cho development
- **Alembic** - Database migrations
- **Jinja2** - HTML templating engine

### Data Processing
- **Pandas** - CSV data processing
- **Python datetime** - Date parsing và timezone handling

## 📊 Key Features

### 1. CSV Upload & Processing
- Upload reservation files từ Airbnb
- Automatic header mapping (EN/VN)
- Data normalization và validation
- Upsert operations để avoid duplicates

### 2. Revenue Reports  
- Monthly revenue summaries
- ADR calculations
- Prorated revenue by actual nights stayed
- Building/unit breakdown

### 3. Expense Tracking
- Categorized expense management
- Property-specific cost allocation
- Monthly expense reports

## 🔧 Current Status
- ✅ Core booking system functional
- ✅ CSV upload với Vietnamese support
- ✅ Basic revenue reports
- ⏳ Enhanced expense categorization
- ⏳ Advanced analytics dashboard

---
*Cập nhật: 27/09/2025*`,

    'SESSION_CONTEXT.md': `# Ngữ Cảnh Session - Brain AI Context

## 📋 Thông Tin Dự Án

**Tên Dự Án**: Airbnb Revenue WebApp  
**Domain**: Property Management System (PMS)  
**Tech Stack**: FastAPI + SQLAlchemy + SQLite  
**Trạng Thái**: Production Ready  
**Ngôn Ngữ**: Python, HTML, CSS, JavaScript  

## 🎯 Mục Tiêu Hiện Tại

### Active Tasks
1. **Database Migration Enhancement** - Cải thiện schema cho expense categories
2. **Vietnamese CSV Support** - Tăng cường parsing headers tiếng Việt  
3. **Performance Optimization** - Tối ưu monthly reports với large datasets

### Completed Recently
- ✅ Brain Template System integration
- ✅ Automation scripts (17,400x speed improvement)
- ✅ React UI for brain content visualization

## 🧠 Brain System Context

### File Structure
\`\`\`
.brain/
├── SCOPE.md              # Project scope và domain definition
├── SESSION_CONTEXT.md    # Quick AI context (this file)
├── DOMAIN_MAP.md         # Business domain architecture  
├── ACTIVE_TASKS.json     # Current development priorities
├── WORKFLOW_SIMPLE.md    # Development workflow
└── context/              # Additional documentation
\`\`\`

### Quick References
- **Main App**: \`main.py\` - FastAPI routes và app setup
- **Models**: \`models.py\` - SQLAlchemy database models
- **Utils**: \`utils.py\` - CSV parsing và Vietnamese header mapping
- **Templates**: \`templates/\` - Jinja2 HTML templates
- **Migrations**: \`alembic/\` - Database schema migrations

## 🔧 Development Workflow

### Setup Commands
\`\`\`powershell
# Virtual environment
python -m venv venv
.\\venv\\Scripts\\activate

# Dependencies  
pip install -r requirements.txt

# Run application
uvicorn main:app --reload
\`\`\`

### Brain Commands
\`\`\`powershell
# Quick brain setup (0.1 second)
.\\create-brain-simple.ps1

# Validate brain structure
.\\validate-brain-template.ps1
\`\`\`

## 🎨 UI Development

### Brain UI (React)
- **Location**: \`brain-ui/\`
- **Purpose**: Web interface untuk .brain/ content
- **Tech**: React + Vite + Tiếng Việt UI
- **Components**: BangDieuKhien, ThanhDieuHuong, TrinhXemMarkdown

## 🚨 Guardrails

### Code Style
- Follow existing patterns dalam codebase
- Use Vietnamese comments trong UI components
- Maintain FastAPI best practices
- Keep SQLAlchemy models normalized

### Data Handling
- Always validate CSV inputs  
- Use header mapping từ \`utils.py\`
- Handle VND currency parsing properly
- Maintain data consistency với upserts

---
*AI Quick Context: Dự án PMS cho Airbnb với brain system hoàn chỉnh*`,

    'DOMAIN_MAP.md': `# Bản Đồ Domain - Business Architecture

## 🏗️ Domain Architecture

### Core Domains

#### 1. Property Management
\`\`\`
Property
├── Building (Tòa nhà)
├── Unit (Căn hộ)  
├── Property Details
└── Ownership Info
\`\`\`

#### 2. Booking Management  
\`\`\`
Reservation
├── Guest Information
├── Check-in/Check-out Dates
├── Pricing Details
├── Status Tracking
└── Revenue Calculations
\`\`\`

#### 3. Financial Management
\`\`\`
Financial
├── Revenue Tracking
├── Expense Categories
├── Monthly Reports
└── ADR Calculations
\`\`\`

## 📊 Data Flow

### CSV Upload Process
1. **File Upload** → Airbnb reservation CSV
2. **Header Mapping** → Vietnamese/English headers  
3. **Data Parsing** → Normalize dates, currency, building codes
4. **Validation** → Check required fields và consistency
5. **Upsert** → Insert new or update existing records

### Revenue Calculation
1. **Base Data** → Reservation records từ database
2. **Prorating** → Calculate actual nights stayed  
3. **Aggregation** → Group by month, property, building
4. **ADR Calculation** → Average Daily Rate per property
5. **Report Generation** → Monthly summary với breakdowns

## 🔄 Business Processes

### Monthly Reporting Cycle
1. **Data Collection** → Gather reservations cho tháng
2. **Revenue Calculation** → Sum prorated amounts
3. **Expense Allocation** → Apply operating costs
4. **Performance Analysis** → ADR, occupancy rates
5. **Report Distribution** → Generate formatted reports

### Property Onboarding
1. **Property Registration** → Add new property to system
2. **Building/Unit Setup** → Configure unit structure
3. **Pricing Configuration** → Set base rates và rules
4. **Integration Testing** → Verify CSV uploads work

---
*Domain Map updated: 27/09/2025*`,

    'README.md': `# Brain UI - Giao Diện Web Cho Hệ Thống Brain

Chào mừng đến với **Brain UI** - giao diện web React để hiển thị và quản lý nội dung hệ thống "bộ não dự án".

## 🧠 Về Hệ Thống Brain

Brain System là một framework để tổ chức và quản lý context, documentation, tasks và knowledge cho các dự án phần mềm. Nó giúp:

- **Team members** hiểu nhanh dự án
- **AI assistants** có context đầy đủ  
- **Documentation** được tổ chức có hệ thống
- **Knowledge transfer** hiệu quả

## 🎯 Mục Tiêu Brain UI

### Cho Developers
- Xem nhanh project scope và current tasks
- Theo dõi progress và milestones
- Access documentation dễ dàng
- Mobile-friendly interface

### Cho AI Assistants  
- Quick context loading từ SESSION_CONTEXT.md
- Structured information access
- Current state awareness
- Task prioritization

## 🚀 Tính Năng Chính

### 🏠 Bảng Điều Khiển
- Project overview với key metrics
- Quick navigation đến tài liệu quan trọng
- Recent activity timeline
- Tech stack summary

### 📑 Trình Xem Markdown
- Render beautiful markdown files
- Code syntax highlighting  
- Responsive design
- External link handling

### ✅ Quản Lý Tasks
- View ACTIVE_TASKS.json trong table format
- Filter và search capabilities
- Progress tracking với visual indicators
- Priority-based organization

### 🧭 Thanh Điều Hướng
- Categorized menu structure
- Collapsible sections
- External links integration
- Brain system status indicator

---

**Đây là sample content - trong thực tế sẽ load từ file .brain/ thực tế của dự án!**`
  }

  useEffect(() => {
    const taiNoiDung = async () => {
      setDangTai(true)
      setLoi(null)
      
      try {
        // Trong production, sẽ fetch từ /brain/fileName
        // const response = await fetch(`/brain/${tenFile}`)
        // const text = await response.text()
        
        // Hiện tại dùng dữ liệu mẫu
        const content = duLieuMau[tenFile] || duLieuMau['README.md']
        
        // Simulate loading delay
        await new Promise(resolve => setTimeout(resolve, 500))
        
        setNoiDung(content)
      } catch (error) {
        console.error('Lỗi tải file:', error)
        setLoi(`Không thể tải file ${tenFile}`)
      } finally {
        setDangTai(false)
      }
    }

    taiNoiDung()
  }, [tenFile])

  if (dangTai) {
    return <div className="dang-tai">Đang tải {tenFile}...</div>
  }

  if (loi) {
    return (
      <div className="loi-tai-file">
        <h2>Lỗi Tải File</h2>
        <p>{loi}</p>
      </div>
    )
  }

  return (
    <div className="trinh-xem-markdown">
      <div className="header-markdown">
        <div className="thong-tin-file">
          <FileText size={24} />
          <div>
            <h1>{tenFile}</h1>
            <p>Tài liệu Brain System</p>
          </div>
        </div>
        <a 
          href={`https://github.com/your-org/airbnb-webapp/blob/main/.brain/${tenFile}`}
          target="_blank"
          rel="noopener noreferrer"
          className="link-nguon"
        >
          <ExternalLink size={16} />
          Xem File Gốc
        </a>
      </div>

      <div className="noi-dung-wrapper">
        <ReactMarkdown className="noi-dung-markdown">
          {noiDung}
        </ReactMarkdown>
      </div>
    </div>
  )
}

export default TrinhXemMarkdown