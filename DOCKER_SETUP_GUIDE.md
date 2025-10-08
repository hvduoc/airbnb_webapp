"""
PROD-002: Docker Containerization - Final Setup Guide
=====================================================

## 🎯 HOÀN THÀNH PROD-002 - Docker Infrastructure

### ✅ CÁC THÀNH PHẦN ĐÃ TRIỂN KHAI

#### 1. Multi-stage Docker Build System
- **Dockerfile**: Production-optimized với builder, production, development stages
- **Security**: Non-root user execution, minimal attack surface
- **Optimization**: Multi-stage builds giảm image size

#### 2. Complete Orchestration Stack  
- **docker-compose.yml**: Production với PostgreSQL, Redis, Nginx, Monitoring
- **docker-compose.dev.yml**: Development với hot reload, Adminer
- **Health checks**: Comprehensive cho tất cả services

#### 3. Reverse Proxy & Security
- **Nginx**: Rate limiting, security headers, SSL termination ready
- **Configuration**: Production-grade với performance optimization
- **Static files**: Efficient serving với caching

#### 4. Monitoring Infrastructure
- **Prometheus**: Metrics collection và storage
- **Grafana**: Visualization dashboards
- **Health endpoints**: /health, /health/live, /health/ready, /metrics

#### 5. Management Tools
- **docker_manager.py**: CLI tool cho container operations
- **setup_docker_dev.ps1**: Automated PowerShell setup script
- **Environment configs**: Comprehensive .env.example template

### 🚀 CÁCH SỬ DỤNG

#### Development Environment:
```powershell
# Option 1: Sử dụng PowerShell script (Recommended)
.\setup_docker_dev.ps1

# Option 2: Manual setup
python docker_manager.py dev-setup

# Option 3: Direct Docker Compose
docker-compose -f docker-compose.dev.yml up -d
```

#### Production Environment:
```powershell
# Set production environment variables
$env:POSTGRES_PASSWORD = "secure_production_password"
$env:REDIS_PASSWORD = "redis_production_password"  
$env:SECRET_KEY = "production_secret_key"

# Deploy production stack
python docker_manager.py prod-setup
```

### 📊 INFRASTRUCTURE ARCHITECTURE

```
Development Stack:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   FastAPI   │───▶│ PostgreSQL   │    │   Adminer   │
│ (Port 8000) │    │ (Port 5432)  │    │ (Port 8080) │
└─────────────┘    └──────────────┘    └─────────────┘
       │
       ▼
┌─────────────┐    ┌──────────────┐
│    Redis    │    │ Prometheus   │
│ (Port 6379) │    │ (Port 9090)  │
└─────────────┘    └──────────────┘

Production Stack:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Nginx     │───▶│   FastAPI    │───▶│ PostgreSQL  │
│ (Port 80)   │    │  (Port 8000) │    │ (Port 5432) │
└─────────────┘    └──────────────┘    └─────────────┘
                           │                    ▲
                           ▼                    │
                   ┌─────────────┐     ┌─────────────┐
                   │    Redis    │     │   Grafana   │
                   │ (Port 6379) │     │ (Port 3000) │
                   └─────────────┘     └─────────────┘
                           ▲                    ▲
                           │                    │
                   ┌─────────────┐     ┌─────────────┐
                   │ Prometheus  │─────┤  Monitoring │
                   │ (Port 9090) │     │   Stack     │
                   └─────────────┘     └─────────────┘
```

### 🔧 TROUBLESHOOTING

#### Docker Desktop Issues:
```powershell
# 1. Kiểm tra Docker service
Get-Service -Name "*docker*"

# 2. Khởi động Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 3. Kiểm tra Docker connectivity
docker --version
docker-compose --version
```

#### Container Issues:
```powershell
# View logs
docker-compose -f docker-compose.dev.yml logs -f webapp

# Restart services
docker-compose -f docker-compose.dev.yml restart

# Rebuild containers
docker-compose -f docker-compose.dev.yml build --no-cache

# Clean up
docker-compose -f docker-compose.dev.yml down --volumes
docker system prune -f
```

#### Health Check Issues:
```powershell
# Test health endpoint
curl http://localhost:8000/health

# Check service status
python docker_manager.py health

# Manual health check
docker-compose -f docker-compose.dev.yml exec webapp python -c "from health_check import check_health; print(check_health())"
```

### 📁 DIRECTORY STRUCTURE

```
airbnb_webapp/
├── Dockerfile                  # Multi-stage container build
├── docker-compose.yml          # Production stack
├── docker-compose.dev.yml      # Development stack
├── docker_manager.py           # Container management CLI
├── setup_docker_dev.ps1        # PowerShell setup script
├── health_check.py            # Health monitoring endpoints
├── .env.example               # Environment configuration template
├── nginx/
│   ├── nginx.conf             # Main Nginx configuration
│   └── conf.d/
│       └── default.conf       # Virtual host configuration
├── monitoring/
│   └── prometheus.yml         # Prometheus configuration
└── data/                      # Persistent data (created automatically)
    ├── postgres/              # PostgreSQL data
    ├── redis/                 # Redis data
    ├── prometheus/            # Prometheus metrics
    ├── grafana/               # Grafana dashboards
    ├── logs/                  # Application logs
    ├── uploads/               # File uploads
    ├── backups/               # Database backups
    └── ssl/                   # SSL certificates
```

### 🎯 NEXT PHASE: PROD-003

Với Docker infrastructure hoàn thành, sẵn sàng để chuyển sang **PROD-003: Advanced Monitoring & Logging**:

1. **ELK Stack Integration** cho centralized logging
2. **Alert Management** với notification systems  
3. **Custom Business Dashboards** cho revenue tracking
4. **Performance Profiling** với APM integration
5. **Error Tracking** với Sentry integration

### 📝 NOTES

- **Security**: Tất cả containers chạy với non-root users
- **Performance**: Multi-stage builds optimize image sizes
- **Monitoring**: Comprehensive health checks cho orchestration
- **Development**: Hot reload enabled cho rapid development
- **Production**: Rate limiting, security headers, SSL ready
- **Scalability**: Ready cho horizontal scaling với load balancer

---

**Status**: ✅ PROD-002 HOÀN THÀNH
**Infrastructure**: Production-ready Docker containerization
**Next**: PROD-003 Advanced Monitoring & Logging System
"""