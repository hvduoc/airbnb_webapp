# 🇻🇳 Hướng Dẫn Triển Khai Hệ Thống Monitoring - PROD-003

## 🎯 Tổng Quan
Hệ thống monitoring hoàn chỉnh với giao diện tiếng Việt, bao gồm:
- **ELK Stack** (Elasticsearch, Logstash, Kibana, Filebeat)
- **Prometheus & Grafana** với dashboard tiếng Việt
- **AlertManager** với thông báo tiếng Việt
- **Business Intelligence Dashboards** cho Airbnb WebApp

## 📋 Kiến Trúc Hệ Thống

### 🏗️ Thành Phần Chính
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Airbnb App    │───►│   Prometheus    │───►│    Grafana      │
│   (Metrics)     │    │   (Collector)   │    │  (Dashboards)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Filebeat     │───►│    Logstash     │───►│ Elasticsearch   │
│ (Log Shipping)  │    │ (Processing)    │    │  (Storage)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                     ┌─────────────────┐    ┌─────────────────┐
                     │  AlertManager   │    │     Kibana      │
                     │ (Notifications) │    │ (Log Analysis)  │
                     └─────────────────┘    └─────────────────┘
```

## 🚀 Triển Khai

### 1️⃣ Khởi Động Hệ Thống Monitoring
```powershell
# Di chuyển đến thư mục dự án
cd d:\DUAN1\Airbnb\airbnb_webapp

# Khởi động toàn bộ hệ thống monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Kiểm tra trạng thái
docker-compose -f docker-compose.monitoring.yml ps
```

### 2️⃣ Xác Nhận Các Dịch Vụ
```powershell
# Kiểm tra logs
docker-compose -f docker-compose.monitoring.yml logs -f

# Kiểm tra health
curl http://localhost:9090/api/v1/query?query=up  # Prometheus
curl http://localhost:3000/api/health              # Grafana  
curl http://localhost:9200/_cluster/health         # Elasticsearch
curl http://localhost:5601/api/status              # Kibana
```

## 🌐 Truy Cập Giao Diện Web

### 📊 Grafana - Business Dashboards
- **URL**: http://localhost:3000
- **Login**: admin / admin123
- **Dashboards**:
  - 📈 **Doanh Thu**: `/d/revenue-tracking` - Theo dõi doanh thu theo thời gian thực
  - 🎯 **Booking Performance**: `/d/booking-performance` - Phân tích hiệu suất đặt phòng
  - 🏢 **Property Utilization**: `/d/property-utilization` - Sử dụng bất động sản
  - 💳 **Payment Processing**: `/d/payment-processing` - Xử lý thanh toán
  - ⚡ **System Performance**: `/d/system-performance` - Hiệu suất hệ thống

### 🔍 Kibana - Log Analysis
- **URL**: http://localhost:5601
- **Features**:
  - Index Patterns: `airbnb-logs-*`, `airbnb-errors-*`
  - Dashboards: Business logs, Error analysis
  - Visualizations: Vietnamese business metrics

### 📊 Prometheus - Metrics
- **URL**: http://localhost:9090
- **Features**:
  - Metrics Explorer với business metrics
  - Alert Rules với mô tả tiếng Việt
  - Targets monitoring

### 🚨 AlertManager - Notifications
- **URL**: http://localhost:9093
- **Features**:
  - Vietnamese email templates
  - Business-context alerts
  - Escalation procedures

## 📊 Dashboard Descriptions

### 1. 📈 Revenue Tracking Dashboard
**Mục đích**: Theo dõi doanh thu và hiệu suất tài chính

**Metrics chính**:
- 💰 Doanh thu hôm nay (VNĐ)
- 📊 Tỷ lệ tăng trưởng doanh thu
- 🏠 Doanh thu theo bất động sản  
- 📅 Xu hướng doanh thu 30 ngày
- 💳 Tỷ lệ thanh toán thành công
- 📈 Average Daily Rate (ADR)

**Filtering**: Theo loại BĐS, khu vực, thời gian

### 2. 🎯 Booking Performance Dashboard  
**Mục đích**: Phân tích hiệu suất đặt phòng và hành trình khách hàng

**Metrics chính**:
- 🎯 Tỷ lệ đặt phòng thành công
- 🆕 Booking mới hôm nay
- ❌ Tỷ lệ hủy booking
- 🛒 Phễu chuyển đổi khách hàng
- 🏠 Booking theo loại BĐS
- 📅 Lead time trung bình
- 🏆 Top BĐS có nhiều booking
- ⏰ Xu hướng booking theo giờ

### 3. 🏢 Property Utilization Dashboard
**Mục đích**: Phân tích sử dụng và hiệu suất vận hành BĐS

**Metrics chính**:
- 🏠 Tỷ lệ sử dụng trung bình
- ✅ BĐS đang hoạt động
- ⚠️ BĐS cần bảo trì
- 📊 Tỷ lệ sử dụng theo BĐS
- 💰 Phân bố doanh thu theo BĐS
- 🧹 Thời gian dọn dẹp
- ⭐ Đánh giá khách hàng
- 💸 Chi phí vận hành

### 4. 💳 Payment Processing Dashboard
**Mục đích**: Giám sát hệ thống thanh toán

**Metrics chính**:
- 💳 Tỷ lệ thanh toán thành công
- ⏱️ Thời gian xử lý trung bình
- 💰 Tổng giá trị giao dịch
- 📈 Xu hướng giao dịch
- 💳 Phương thức thanh toán
- 🌐 Thời gian phản hồi gateway
- 🚨 Top lỗi thanh toán
- 💵 Giá trị giao dịch trung bình

### 5. ⚡ System Performance Dashboard
**Mục đích**: Giám sát hiệu suất hệ thống

**Metrics chính**:
- 🖥️ Sử dụng CPU
- 💾 Sử dụng RAM
- 🌐 Request/giây
- ⏱️ Thời gian phản hồi
- 📊 Tài nguyên hệ thống
- 📈 HTTP response codes
- 🚀 Response time theo endpoint
- 🗄️ Kết nối database
- 🐌 Top endpoint chậm nhất

## 🚨 Alert Rules

### 🔥 Critical Alerts
```yaml
# High Error Rate - Tỷ lệ lỗi cao
- alert: TyLeLoi_Cao
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 2m
  annotations:
    summary: "🚨 Tỷ lệ lỗi hệ thống cao"
    description: "Tỷ lệ lỗi 5xx đã vượt quá 10% trong 2 phút"

# Database Down - Cơ sở dữ liệu ngừng hoạt động  
- alert: CoSoDuLieu_NgungHoatDong
  expr: up{job="postgres"} == 0
  for: 1m
  annotations:
    summary: "💀 Cơ sở dữ liệu ngừng hoạt động"
    description: "Không thể kết nối đến cơ sở dữ liệu chính"
```

### ⚠️ Warning Alerts
```yaml
# High CPU Usage - Sử dụng CPU cao
- alert: SuDung_CPU_Cao  
  expr: rate(process_cpu_seconds_total[5m]) * 100 > 80
  for: 5m
  annotations:
    summary: "⚠️ Sử dụng CPU cao"
    description: "CPU sử dụng > 80% trong 5 phút"

# Low Booking Success Rate - Tỷ lệ booking thành công thấp
- alert: TyLeBooking_Thap
  expr: rate(airbnb_booking_success_total[1h]) / rate(airbnb_booking_attempts_total[1h]) < 0.8
  for: 10m
  annotations:
    summary: "📉 Tỷ lệ booking thành công thấp"
    description: "Tỷ lệ booking thành công < 80% trong 1 giờ"
```

## 📧 Email Notifications

### 🎨 Template Tiếng Việt
```html
<h2>🚨 Cảnh Báo Hệ Thống Airbnb WebApp</h2>
<p><strong>Thời gian:</strong> {{ .Alerts.CommonLabels.alertname }}</p>
<p><strong>Mức độ:</strong> {{ .Alerts.CommonLabels.severity }}</p>
<p><strong>Dịch vụ:</strong> {{ .Alerts.CommonLabels.service }}</p>
<p><strong>Mô tả:</strong> {{ .Alerts.CommonAnnotations.description }}</p>

<h3>📋 Chi Tiết Cảnh Báo:</h3>
{{ range .Alerts }}
<ul>
  <li><strong>Metric:</strong> {{ .Labels.alertname }}</li>
  <li><strong>Instance:</strong> {{ .Labels.instance }}</li>
  <li><strong>Giá trị:</strong> {{ .Labels.value }}</li>
</ul>
{{ end }}

<p><em>Hệ thống monitoring Airbnb WebApp - Vietnam</em></p>
```

## 🔧 Cấu Hình Nâng Cao

### 📊 Custom Business Metrics
```python
# Trong main.py hoặc payment_production.py
from prometheus_client import Counter, Histogram, Gauge

# Business metrics
revenue_total = Counter('airbnb_revenue_total', 'Total revenue in VND', ['property_id'])
booking_success = Counter('airbnb_booking_success_total', 'Successful bookings', ['property_type'])
payment_processing_time = Histogram('airbnb_payment_processing_duration_seconds', 'Payment processing time')
property_occupancy = Gauge('airbnb_property_occupancy_rate', 'Property occupancy rate', ['property_id'])

# Usage example
@app.post("/api/bookings")
async def create_booking(booking_data: BookingData):
    start_time = time.time()
    
    try:
        # Business logic here
        result = await process_booking(booking_data)
        
        # Record metrics
        booking_success.labels(property_type=booking_data.property_type).inc()
        revenue_total.labels(property_id=booking_data.property_id).inc(booking_data.amount)
        
        return result
    finally:
        payment_processing_time.observe(time.time() - start_time)
```

### 🌍 Timezone Configuration
```yaml
# grafana.ini
[defaults]
default_timezone = Asia/Ho_Chi_Minh

# Prometheus
global:
  evaluation_interval: 30s
  scrape_interval: 15s
  external_labels:
    timezone: 'Asia/Ho_Chi_Minh'
    region: 'Vietnam'
    environment: 'production'
```

## 🛠️ Troubleshooting

### ❌ Common Issues

#### 1. Grafana không hiển thị data
```powershell
# Kiểm tra Prometheus targets
curl http://localhost:9090/api/v1/targets

# Kiểm tra metrics
curl http://localhost:9090/api/v1/query?query=up

# Restart Grafana
docker-compose -f docker-compose.monitoring.yml restart grafana
```

#### 2. Elasticsearch không nhận logs
```powershell
# Kiểm tra Filebeat
docker-compose -f docker-compose.monitoring.yml logs filebeat

# Kiểm tra Logstash pipeline
docker-compose -f docker-compose.monitoring.yml logs logstash

# Test Elasticsearch
curl -X GET "localhost:9200/_cat/indices?v"
```

#### 3. AlertManager không gửi email
```powershell
# Kiểm tra config
docker-compose -f docker-compose.monitoring.yml exec alertmanager \
  amtool config show

# Test email template
docker-compose -f docker-compose.monitoring.yml exec alertmanager \
  amtool template test-template.tmpl
```

### 🔍 Log Analysis Commands
```powershell
# Xem logs real-time
docker-compose -f docker-compose.monitoring.yml logs -f grafana
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
docker-compose -f docker-compose.monitoring.yml logs -f elasticsearch

# Kiểm tra resource usage
docker stats

# Backup configuration
docker-compose -f docker-compose.monitoring.yml exec grafana \
  tar -czf /tmp/grafana-backup.tar.gz /var/lib/grafana
```

## 📈 Performance Optimization

### 🚀 Elasticsearch
```yaml
# elk/elasticsearch/elasticsearch.yml
bootstrap.memory_lock: true
indices.memory.index_buffer_size: 20%
indices.memory.min_index_buffer_size: 96mb
thread_pool.write.queue_size: 1000
```

### 🎯 Prometheus
```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 30s
  
rule_files:
  - "rules/*.yml"
  
scrape_configs:
  - job_name: 'airbnb-webapp'
    scrape_interval: 10s
    static_configs:
      - targets: ['airbnb-app:8000']
```

### 📊 Grafana
```ini
# grafana/grafana.ini
[database]
type = postgres
host = postgres:5432
name = grafana
user = grafana
password = grafana123

[caching]
enabled = true
ttl = 300s
```

## 🔒 Security Best Practices

### 🛡️ Authentication
```yaml
# grafana/grafana.ini
[auth]
disable_login_form = false
disable_signout_menu = false

[auth.basic]
enabled = true

[security]
admin_user = admin
admin_password = $__file{/run/secrets/admin_password}
secret_key = $__file{/run/secrets/secret_key}
```

### 🔐 SSL/TLS
```yaml
# nginx/nginx.conf for production
server {
    listen 443 ssl http2;
    server_name monitoring.airbnb-webapp.vn;
    
    ssl_certificate /etc/ssl/certs/monitoring.crt;
    ssl_certificate_key /etc/ssl/private/monitoring.key;
    
    location /grafana/ {
        proxy_pass http://grafana:3000/;
    }
    
    location /prometheus/ {
        proxy_pass http://prometheus:9090/;
    }
}
```

## 📚 Tài Liệu Tham Khảo

### 🔗 Links Hữu Ích
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)

### 📖 Vietnamese Resources
- [Hướng dẫn Grafana tiếng Việt](https://grafana.com/docs/grafana/latest/administration/internationalization/)
- [Cấu hình Prometheus cho ứng dụng Việt Nam](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)

---

## ✅ Checklist Triển Khai

- [ ] Docker containers khởi động thành công
- [ ] Prometheus targets UP
- [ ] Grafana dashboards hiển thị data
- [ ] Elasticsearch nhận logs
- [ ] Kibana index patterns created
- [ ] AlertManager rules configured
- [ ] Email notifications tested
- [ ] Vietnamese locale configured
- [ ] Business metrics tracking
- [ ] Performance optimized

**🎉 Chúc mừng! Hệ thống monitoring với giao diện tiếng Việt đã sẵn sàng cho production!**