# Payment Ledger Module - Complete Documentation

## 🎯 **Overview**

The Payment Ledger module provides a comprehensive solution for managing Airbnb payment collections using **Google Sheets as the database**. This eliminates the need for traditional database servers while providing real-time collaboration and easy access to raw data.

## 🏗️ **Architecture**

### **Backend (FastAPI)**
- **Authentication**: JWT-based with role-based access control
- **Google Sheets Integration**: Service account authentication for seamless data access
- **API Routes**: RESTful endpoints for payments, cashflow, and dashboard
- **Real-time Data**: Direct integration with Google Sheets API

### **Frontend (HTML + JavaScript)**
- **Responsive Design**: TailwindCSS for modern, mobile-friendly UI
- **Charts**: Chart.js for revenue analytics and performance dashboards  
- **Real-time Updates**: AJAX calls for live data without page refreshes
- **Role-based UI**: Different interfaces for Assistant/Manager/Owner

### **Data Storage (Google Sheets)**
- **Payments Sheet**: Transaction records with full audit trail
- **Cashflow Sheet**: Cash handover tracking between roles
- **Dashboard Data**: Aggregated metrics for reporting

## 🔧 **Features**

### **Payment Recording**
- ✅ Booking ID linking
- ✅ Multiple payment methods (Cash, Transfer, Airbnb, MoMo, ZaloPay, VietQR)
- ✅ Amount validation and status tracking
- ✅ Real-time Google Sheets synchronization

### **Cash Management**
- ✅ Handover tracking (Assistant → Manager → Owner)
- ✅ Cash balance monitoring
- ✅ Approval workflow with audit trail

### **Dashboard & Analytics**
- ✅ KPI cards (Total collected, Collection rate, Cash balance)
- ✅ Revenue trends by period (Day/Week/Month)
- ✅ Collector performance analysis
- ✅ Real-time data visualization

### **Security & Access Control**
- ✅ JWT authentication with role-based permissions
- ✅ Assistant: Own payments only
- ✅ Manager: All payments + cash handover
- ✅ Owner: Full system access

## 📁 **File Structure**

```
├── services/google_sheets/
│   ├── __init__.py
│   ├── config.py                 # Google Sheets configuration
│   ├── service.py               # Google Sheets API service
│   └── models.py                # Pydantic models for requests/responses
├── auth/
│   ├── __init__.py
│   └── auth_service.py          # JWT authentication service
├── templates/payments/
│   ├── login.html               # Login interface
│   └── dashboard.html           # Main dashboard UI
├── routes_payments.py           # Payment API routes
├── create_payment_users.py      # Demo users setup script
├── setup_payment_ledger.py      # Installation script
├── requirements_payments.txt    # Python dependencies
├── .env.payment.example         # Environment configuration example
└── credentials/
    ├── README.md               # Google API setup instructions
    └── service-account.json    # Google service account credentials (not in git)
```

## 🚀 **Installation & Setup**

### **1. Quick Setup**
```bash
# Run the automated setup script
python setup_payment_ledger.py
```

### **2. Manual Setup**

```bash
# Install dependencies
pip install -r requirements_payments.txt

# Create environment configuration
cp .env.payment.example .env

# Create demo users
python create_payment_users.py

# Start server
uvicorn main:app --reload
```

### **3. Google Sheets Setup**

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project: "payment-ledger"

2. **Enable APIs**
   - Enable Google Sheets API
   - Enable Google Drive API

3. **Create Service Account**
   - Go to IAM & Admin → Service Accounts
   - Create service account: "payment-ledger-service"
   - Download JSON credentials
   - Save as `credentials/service-account.json`

4. **Configure Spreadsheet**
   - Create new Google Spreadsheet
   - Share with service account email (from JSON file)
   - Copy spreadsheet ID from URL
   - Add to .env: `GOOGLE_SPREADSHEET_ID=your_id_here`

## 🔑 **Demo Accounts**

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Assistant | `assistant` | `assistant123` | Record payments, view own transactions |
| Manager | `manager` | `manager123` | All payments, cash handover, reports |
| Owner | `owner` | `owner123` | Full system access, all features |

## 🌐 **API Endpoints**

### **Authentication**
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Current user info
- `POST /api/auth/logout` - Logout

### **Payments**
- `POST /api/payments/add` - Add payment record
- `GET /api/payments/list` - List payments with filters
- `GET /api/payments/dashboard` - Dashboard metrics

### **Cash Management**
- `POST /api/payments/cashflow/handover` - Record handover
- `GET /api/payments/cashflow/list` - Cashflow history

### **Analytics**
- `GET /api/payments/dashboard/revenue-by-period` - Revenue trends
- `GET /api/payments/dashboard/collector-performance` - Performance metrics

## 📊 **Data Sheets Structure**

### **Payments Sheet**
| Column | Description |
|--------|-------------|
| Timestamp | Record creation time |
| Booking ID | Airbnb booking reference |
| Guest Name | Customer name |
| Amount Due (VND) | Expected payment amount |
| Amount Collected (VND) | Actual payment received |
| Payment Method | cash, bank_transfer, airbnb_payout, etc. |
| Collected By | Staff member name |
| Transaction ID | External payment reference |
| Notes | Additional comments |
| Status | completed, pending, partial, cancelled |

### **Cashflow Sheet**
| Column | Description |
|--------|-------------|
| Timestamp | Transaction time |
| Transaction Type | handover, collection, expense, adjustment |
| From Person | Person giving money |
| To Person | Person receiving money |
| Amount (VND) | Transfer amount |
| Cash Balance | Running balance after transaction |
| Description | Transaction description |
| Approved By | Authorizing person |
| Status | Transaction status |

## 🎨 **UI Components**

### **Dashboard**
- **KPI Cards**: Total collected, collection rate, cash balance, transaction count
- **Revenue Chart**: Monthly/weekly revenue trends with Chart.js
- **Collector Performance**: Bar chart showing staff performance
- **Real-time Updates**: Auto-refresh every 30 seconds

### **Payment Form**
- **Booking Integration**: Link to existing booking system
- **Payment Methods**: Dropdown with Vietnamese payment options
- **Validation**: Client and server-side validation
- **Auto-completion**: Staff name suggestions

### **Cash Handover**
- **Role-based Flow**: Assistant → Manager → Owner workflow
- **Balance Tracking**: Real-time cash balance display
- **Approval System**: Required approval for large amounts
- **History View**: Complete handover audit trail

## 🔐 **Security Features**

- **JWT Tokens**: Secure authentication with configurable expiration
- **Password Hashing**: bcrypt for secure password storage
- **Role-based Access**: Granular permissions by user role
- **Input Validation**: Both client and server-side validation
- **API Rate Limiting**: Protection against abuse
- **Audit Trail**: Complete logging of all financial transactions

## 🌟 **Benefits**

### **For Business**
- ✅ **No Database Server**: Use Google Sheets as database
- ✅ **Real-time Collaboration**: Multiple users can access data simultaneously
- ✅ **Easy Backup**: Google's automatic backup and version history
- ✅ **Mobile Access**: Works on any device with web browser
- ✅ **Cost Effective**: No additional infrastructure costs

### **For Development**
- ✅ **Quick Deployment**: No database setup required
- ✅ **Easy Integration**: Simple Google Sheets API
- ✅ **Scalable**: Can handle thousands of transactions
- ✅ **Maintainable**: Clean separation of concerns
- ✅ **Extensible**: Easy to add new features

### **For Users**
- ✅ **Intuitive Interface**: Vietnamese language support
- ✅ **Fast Performance**: Optimized for mobile and desktop
- ✅ **Real-time Updates**: See changes immediately
- ✅ **Offline Support**: Can work with cached data
- ✅ **Export Capabilities**: Direct access to Google Sheets for reports

## 🚀 **Future Enhancements**

### **Phase 2 Features**
- [ ] **Mobile App**: React Native app for field collection
- [ ] **QR Code Payments**: Integration with Vietnamese QR payment systems
- [ ] **Automated Reconciliation**: Match Airbnb payouts with collections
- [ ] **Advanced Analytics**: Predictive analytics and forecasting
- [ ] **Multi-language**: English/Vietnamese language switching

### **Phase 3 Integration**
- [ ] **Airbnb API**: Direct booking integration
- [ ] **Banking API**: Automated bank transaction matching
- [ ] **Accounting System**: Export to popular accounting software
- [ ] **SMS Notifications**: Payment reminders and confirmations
- [ ] **WhatsApp Integration**: Customer communication automation

## 📞 **Support & Maintenance**

### **Troubleshooting**
- Check Google Sheets API quotas and limits
- Verify service account permissions
- Monitor JWT token expiration
- Review error logs in FastAPI dashboard

### **Monitoring**
- Google Sheets API usage tracking
- User session monitoring
- Payment volume analytics
- Error rate monitoring

### **Backup Strategy**
- Google Sheets automatic versioning
- Daily database exports via API
- Configuration backup in version control
- User credential backup procedures

---

## 🎯 **Getting Started**

1. **Run Setup**: `python setup_payment_ledger.py`
2. **Configure Google Sheets**: Follow credentials/README.md
3. **Start Server**: `uvicorn main:app --reload`
4. **Access System**: http://localhost:8000/payments/login
5. **Login**: Use demo credentials above
6. **Start Recording**: Add your first payment!

**Ready to revolutionize your Airbnb payment management! 🚀**