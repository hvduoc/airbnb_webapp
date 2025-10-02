#!/usr/bin/env python3
"""
AIRBNB WEBAPP - Health Check Endpoint
Endpoint kiểm tra tình trạng sức khỏe cho container orchestration
Author: AI Assistant
Created: 2024-12-28
"""

import time
import psutil
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import text
from db import get_session_context
from production_config import settings
import logging

logger = logging.getLogger(__name__)

# Tạo router cho health checks
health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    """
    Comprehensive health check cho Docker containers
    Kiểm tra: Database, Redis, System resources, Application status
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT.value,
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    try:
        # ==================== DATABASE CHECK ====================
        db_start = time.time()
        try:
            with get_session_context() as session:
                result = session.exec(text("SELECT 1")).first()
                if result:
                    health_status["checks"]["database"] = {
                        "status": "healthy",
                        "response_time_ms": round((time.time() - db_start) * 1000, 2),
                        "type": settings.DATABASE_TYPE
                    }
                else:
                    raise Exception("Database query returned no result")
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round((time.time() - db_start) * 1000, 2)
            }
            health_status["status"] = "degraded"
        
        # ==================== REDIS CHECK ====================
        redis_start = time.time()
        try:
            import redis
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5
            )
            redis_client.ping()
            health_status["checks"]["redis"] = {
                "status": "healthy",
                "response_time_ms": round((time.time() - redis_start) * 1000, 2)
            }
        except Exception as e:
            health_status["checks"]["redis"] = {
                "status": "unhealthy", 
                "error": str(e),
                "response_time_ms": round((time.time() - redis_start) * 1000, 2)
            }
            # Redis failure không làm app unhealthy hoàn toàn
            if health_status["status"] == "healthy":
                health_status["status"] = "degraded"
        
        # ==================== SYSTEM RESOURCES CHECK ====================
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            health_status["checks"]["system_resources"] = {
                "status": "healthy" if cpu_percent < 90 and memory_percent < 90 and disk_percent < 90 else "warning",
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "available_memory_gb": round(memory.available / (1024**3), 2)
            }
            
            # Cảnh báo nếu resources cao
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                health_status["status"] = "warning"
                
        except Exception as e:
            health_status["checks"]["system_resources"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # ==================== APPLICATION STATUS ====================
        health_status["checks"]["application"] = {
            "status": "healthy",
            "uptime_seconds": time.time() - psutil.Process().create_time(),
            "environment": settings.ENVIRONMENT.value,
            "debug_mode": settings.DEBUG,
            "ssl_enabled": settings.SSL_ENABLED
        }
        
        # ==================== DEPENDENCIES STATUS ====================
        dependencies_status = "healthy"
        dependencies = {}
        
        # Check critical dependencies
        if health_status["checks"]["database"]["status"] != "healthy":
            dependencies_status = "critical"
        
        if health_status["checks"].get("redis", {}).get("status") != "healthy":
            if dependencies_status == "healthy":
                dependencies_status = "degraded"
        
        dependencies["status"] = dependencies_status
        health_status["checks"]["dependencies"] = dependencies
        
        # ==================== OVERALL STATUS DETERMINATION ====================
        # Determine overall status dựa trên individual checks
        critical_failures = [
            check for check in health_status["checks"].values() 
            if isinstance(check, dict) and check.get("status") == "unhealthy"
        ]
        
        if critical_failures:
            health_status["status"] = "unhealthy"
        elif health_status["status"] not in ["unhealthy", "degraded"]:
            # Nếu chưa có status degraded từ individual checks
            warning_checks = [
                check for check in health_status["checks"].values()
                if isinstance(check, dict) and check.get("status") == "warning"
            ]
            if warning_checks:
                health_status["status"] = "warning"
        
        # ==================== RESPONSE LOGIC ====================
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )
        elif health_status["status"] in ["degraded", "warning"]:
            # Return 200 but log warning
            logger.warning(f"Health check shows {health_status['status']} status: {health_status}")
            return health_status
        else:
            return health_status
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Health check failed with unexpected error: {e}")
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "environment": settings.ENVIRONMENT.value
        }
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_response
        )

@health_router.get("/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe - kiểm tra app có còn sống không
    Đơn giản chỉ return 200 nếu process còn running
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT.value
    }

@health_router.get("/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe - kiểm tra app có sẵn sàng nhận traffic không
    Kiểm tra database connection và critical dependencies
    """
    try:
        # Quick database check
        with get_session_context() as session:
            session.exec(text("SELECT 1")).first()
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENVIRONMENT.value,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@health_router.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint
    Export metrics theo Prometheus format
    """
    try:
        # Basic system metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application metrics
        process = psutil.Process()
        app_memory = process.memory_info().rss / 1024 / 1024  # MB
        app_cpu = process.cpu_percent()
        
        # Generate Prometheus format metrics
        metrics = f"""# HELP airbnb_webapp_info Application information
# TYPE airbnb_webapp_info gauge
airbnb_webapp_info{{version="{settings.APP_VERSION}",environment="{settings.ENVIRONMENT.value}"}} 1

# HELP airbnb_webapp_cpu_usage_percent CPU usage percentage
# TYPE airbnb_webapp_cpu_usage_percent gauge
airbnb_webapp_cpu_usage_percent {cpu_percent}

# HELP airbnb_webapp_memory_usage_percent Memory usage percentage
# TYPE airbnb_webapp_memory_usage_percent gauge
airbnb_webapp_memory_usage_percent {memory.percent}

# HELP airbnb_webapp_disk_usage_percent Disk usage percentage
# TYPE airbnb_webapp_disk_usage_percent gauge
airbnb_webapp_disk_usage_percent {disk.percent}

# HELP airbnb_webapp_process_memory_mb Process memory usage in MB
# TYPE airbnb_webapp_process_memory_mb gauge
airbnb_webapp_process_memory_mb {app_memory}

# HELP airbnb_webapp_process_cpu_percent Process CPU usage percentage
# TYPE airbnb_webapp_process_cpu_percent gauge
airbnb_webapp_process_cpu_percent {app_cpu}

# HELP airbnb_webapp_uptime_seconds Application uptime in seconds
# TYPE airbnb_webapp_uptime_seconds counter
airbnb_webapp_uptime_seconds {time.time() - process.create_time()}
"""

        return Response(content=metrics, media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to generate metrics"}
        )

# Export router
__all__ = ["health_router"]