#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🇻🇳 Airbnb WebApp Monitoring Management CLI
Enhanced Monitoring & Logging Management Script
PROD-003: Advanced Monitoring System with Vietnamese Interface

Usage:
    python monitoring_manager.py [command] [options]
    
Commands:
    start       - Khởi động hệ thống monitoring
    stop        - Dừng hệ thống monitoring  
    restart     - Khởi động lại hệ thống
    status      - Kiểm tra trạng thái
    logs        - Xem logs
    backup      - Sao lưu cấu hình
    restore     - Khôi phục cấu hình
    health      - Kiểm tra sức khỏe hệ thống
    metrics     - Hiển thị metrics quan trọng
    alerts      - Quản lý alerts
    help        - Hiển thị trợ giúp
"""

import os
import subprocess
import time

import requests


class VietnameseMonitoringManager:
    """
    CLI tool để quản lý ELK Stack và Alert Management
    với Vietnamese interface cho Airbnb WebApp
    """
    
    def __init__(self):
        self.compose_files = {
            'base': 'docker-compose.yml',
            'dev': 'docker-compose.dev.yml', 
            'monitoring': 'docker-compose.monitoring.yml'
        }
        
        self.services = {
            'elk': ['elasticsearch', 'logstash', 'kibana', 'filebeat'],
            'alerting': ['alertmanager', 'prometheus'],
            'core': ['webapp', 'postgres', 'redis', 'nginx'],
            'monitoring': ['grafana']
        }
        
        self.endpoints = {
            'elasticsearch': 'http://localhost:9200',
            'kibana': 'http://localhost:5601',
            'logstash': 'http://localhost:9600',
            'prometheus': 'http://localhost:9090',
            'alertmanager': 'http://localhost:9093',
            'grafana': 'http://localhost:3000',
            'webapp': 'http://localhost:8000'
        }
        
    def run_command(self, command: str, capture_output: bool = True) -> tuple:
        """Execute shell command với error handling"""
        try:
            print(f"🔧 Executing: {command}")
            if capture_output:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=300
                )
                return result.returncode == 0, result.stdout, result.stderr
            else:
                result = subprocess.run(command, shell=True, timeout=300)
                return result.returncode == 0, "", ""
        except subprocess.TimeoutExpired:
            print("❌ Command timeout after 5 minutes")
            return False, "", "Command timeout"
        except Exception as e:
            print(f"❌ Command failed: {str(e)}")
            return False, "", str(e)
    
    def check_prerequisites(self) -> bool:
        """Kiểm tra Docker và compose files"""
        print("📋 Kiểm tra prerequisites...")
        
        # Check Docker
        success, _, _ = self.run_command("docker --version")
        if not success:
            print("❌ Docker không khả dụng. Vui lòng cài đặt Docker Desktop.")
            return False
        print("✅ Docker available")
        
        # Check Docker Compose
        success, _, _ = self.run_command("docker-compose --version")
        if not success:
            print("❌ Docker Compose không khả dụng.")
            return False
        print("✅ Docker Compose available")
        
        # Check compose files
        for name, file in self.compose_files.items():
            if not os.path.exists(file):
                print(f"❌ Missing {name} compose file: {file}")
                return False
            print(f"✅ {name} compose file found: {file}")
            
        return True
    
    def setup_monitoring_stack(self):
        """Deploy complete monitoring stack"""
        print("🚀 Deploying Complete Monitoring Stack...")
        print("🎯 Bao gồm: ELK Stack + AlertManager + Enhanced Prometheus")
        
        if not self.check_prerequisites():
            return
            
        # Create required directories
        directories = [
            'data/elasticsearch', 'data/kibana', 'data/filebeat', 
            'data/alertmanager', 'logs', 'uploads', 'backups'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Created/verified: {directory}")
        
        # Set environment variables
        os.environ.update({
            'POSTGRES_DB': 'airbnb_app',
            'POSTGRES_USER': 'airbnb_user',
            'POSTGRES_PASSWORD': 'monitoring_password_123',
            'REDIS_PASSWORD': 'monitoring_redis_123',
            'SECRET_KEY': 'monitoring_secret_key_for_development',
            'ENVIRONMENT': 'monitoring'
        })
        
        print("✅ Environment variables set for monitoring")
        
        # Deploy base infrastructure first
        print("🏗️ Deploying base infrastructure...")
        success, _, error = self.run_command(
            f"docker-compose -f {self.compose_files['base']} up -d"
        )
        
        if not success:
            print(f"❌ Failed to deploy base infrastructure: {error}")
            return
            
        # Wait for base services
        print("⏳ Waiting for base services...")
        time.sleep(30)
        
        # Deploy monitoring stack
        print("🏗️ Deploying monitoring stack (ELK + AlertManager)...")
        success, _, error = self.run_command(
            f"docker-compose -f {self.compose_files['monitoring']} up -d"
        )
        
        if not success:
            print(f"❌ Failed to deploy monitoring stack: {error}")
            return
            
        print("✅ Monitoring stack deployment initiated")
        
        # Wait for services to start
        print("⏳ Waiting for monitoring services to start (60s)...")
        time.sleep(60)
        
        # Check service health
        self.check_monitoring_health()
        
    def check_monitoring_health(self):
        """Kiểm tra health của monitoring services"""
        print("\n📊 Checking Monitoring Services Health...")
        
        health_status = {}
        
        for service, url in self.endpoints.items():
            try:
                response = requests.get(f"{url}/_cluster/health" if service == 'elasticsearch' 
                                     else f"{url}/api/health" if service == 'grafana'
                                     else f"{url}/-/healthy" if service in ['prometheus', 'alertmanager']
                                     else f"{url}/app/monitoring" if service == 'kibana'
                                     else f"{url}/health", timeout=10)
                
                if response.status_code == 200:
                    health_status[service] = "✅ Healthy"
                    print(f"✅ {service.title()}: {url} - Healthy")
                else:
                    health_status[service] = f"⚠️ Status {response.status_code}"
                    print(f"⚠️ {service.title()}: {url} - Status {response.status_code}")
                    
            except requests.exceptions.RequestException:
                health_status[service] = "❌ Not accessible"
                print(f"❌ {service.title()}: {url} - Not accessible")
        
        # Display summary
        print("\n📋 MONITORING HEALTH SUMMARY:")
        for service, status in health_status.items():
            print(f"   {service.ljust(15)}: {status}")
            
    def view_logs(self, service: str = "all", follow: bool = False):
        """Xem logs của monitoring services"""
        if service == "all":
            print("📜 Viewing all monitoring logs...")
            " ".join(self.services['elk'] + self.services['alerting'])
            command = f"docker-compose -f {self.compose_files['monitoring']} logs"
        else:
            print(f"📜 Viewing {service} logs...")
            command = f"docker-compose -f {self.compose_files['monitoring']} logs {service}"
            
        if follow:
            command += " -f"
            
        self.run_command(command, capture_output=False)
        
    def restart_monitoring(self, service: str = "all"):
        """Restart monitoring services"""
        if service == "all":
            print("🔄 Restarting all monitoring services...")
            command = f"docker-compose -f {self.compose_files['monitoring']} restart"
        else:
            print(f"🔄 Restarting {service}...")
            command = f"docker-compose -f {self.compose_files['monitoring']} restart {service}"
            
        success, _, error = self.run_command(command)
        if success:
            print(f"✅ Restart completed for {service}")
        else:
            print(f"❌ Restart failed: {error}")
            
    def stop_monitoring(self):
        """Stop monitoring stack"""
        print("🛑 Stopping monitoring stack...")
        success, _, error = self.run_command(
            f"docker-compose -f {self.compose_files['monitoring']} down"
        )
        if success:
            print("✅ Monitoring stack stopped")
        else:
            print(f"❌ Failed to stop: {error}")
            
    def cleanup_monitoring(self):
        """Cleanup monitoring stack và data"""
        print("🧹 Cleaning up monitoring stack...")
        confirmation = input("⚠️ Bạn có chắc muốn xóa ALL monitoring data? (yes/no): ")
        
        if confirmation.lower() == 'yes':
            # Stop and remove containers
            self.run_command(f"docker-compose -f {self.compose_files['monitoring']} down -v")
            
            # Remove monitoring volumes
            monitoring_volumes = [
                'airbnb_webapp_elasticsearch_data',
                'airbnb_webapp_kibana_data', 
                'airbnb_webapp_filebeat_data',
                'airbnb_webapp_alertmanager_data'
            ]
            
            for volume in monitoring_volumes:
                self.run_command(f"docker volume rm {volume}")
                
            print("✅ Monitoring cleanup completed")
        else:
            print("ℹ️ Cleanup cancelled")
            
    def setup_kibana_dashboards(self):
        """Setup Kibana dashboards với Vietnamese content"""
        print("📊 Setting up Kibana dashboards...")
        
        # Wait for Kibana to be ready
        kibana_ready = False
        max_attempts = 12
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.endpoints['kibana']}/api/status", timeout=10)
                if response.status_code == 200:
                    kibana_ready = True
                    break
            except:
                pass
                
            print(f"⏳ Waiting for Kibana... ({attempt + 1}/{max_attempts})")
            time.sleep(15)
            
        if not kibana_ready:
            print("❌ Kibana not ready for dashboard setup")
            return
            
        print("✅ Kibana ready, creating Vietnamese dashboards...")
        
        # Vietnamese index patterns
        index_patterns = [
            {
                "title": "airbnb-logs-application-*",
                "timeFieldName": "@timestamp"
            },
            {
                "title": "airbnb-logs-nginx-*", 
                "timeFieldName": "@timestamp"
            },
            {
                "title": "airbnb-logs-postgres-*",
                "timeFieldName": "@timestamp"
            }
        ]
        
        for pattern in index_patterns:
            try:
                response = requests.post(
                    f"{self.endpoints['kibana']}/api/saved_objects/index-pattern",
                    headers={'Content-Type': 'application/json', 'kbn-xsrf': 'true'},
                    json={"attributes": pattern}
                )
                if response.status_code in [200, 409]:  # 409 = already exists
                    print(f"✅ Index pattern created: {pattern['title']}")
                else:
                    print(f"⚠️ Failed to create index pattern: {pattern['title']}")
            except Exception as e:
                print(f"❌ Error creating index pattern: {e}")
                
        print("📊 Vietnamese Kibana setup completed")
        
    def display_monitoring_urls(self):
        """Display all monitoring URLs"""
        print("\n🔗 MONITORING DASHBOARD URLs:")
        print("=" * 60)
        
        urls = {
            "📊 Kibana (Log Analysis)": "http://localhost:5601",
            "📈 Grafana (Metrics Dashboard)": "http://localhost:3000", 
            "🎯 Prometheus (Metrics Storage)": "http://localhost:9090",
            "🚨 AlertManager (Alert Management)": "http://localhost:9093",
            "🔍 Elasticsearch (Search Engine)": "http://localhost:9200",
            "⚙️ Logstash (Log Processing)": "http://localhost:9600",
            "💖 FastAPI Health Check": "http://localhost:8000/health",
            "📱 FastAPI Documentation": "http://localhost:8000/docs"
        }
        
        for name, url in urls.items():
            print(f"   {name}: {url}")
            
        print("\n📝 VIETNAMESE BUSINESS DASHBOARDS:")
        print("   • Revenue Tracking (Theo dõi doanh thu)")
        print("   • Booking Analytics (Phân tích đặt phòng)")  
        print("   • Payment Performance (Hiệu suất thanh toán)")
        print("   • Property Utilization (Sử dụng bất động sản)")
        print("   • Customer Journey (Hành trình khách hàng)")
        
    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("🎯 AIRBNB WEBAPP - ADVANCED MONITORING MANAGER")
        print("📊 PROD-003: ELK Stack + Alert Management") 
        print("🌐 Vietnamese Interface")
        print("="*60)
        
        options = {
            "1": "🚀 Deploy Complete Monitoring Stack",
            "2": "📊 Check Monitoring Health", 
            "3": "📜 View Service Logs",
            "4": "🔄 Restart Monitoring Services",
            "5": "🛑 Stop Monitoring Stack",
            "6": "🧹 Cleanup Monitoring Data",
            "7": "📊 Setup Kibana Dashboards",
            "8": "🔗 Display Monitoring URLs",
            "9": "❓ Help & Documentation",
            "0": "🚪 Exit"
        }
        
        for key, value in options.items():
            print(f"   {key}. {value}")
            
        return input("\n👉 Chọn option (0-9): ").strip()

def main():
    """Main function"""
    manager = VietnameseMonitoringManager()
    
    print("🌅 CHÀO MỪNG ĐẾN MONITORING MANAGEMENT!")
    print("🎯 PROD-003: Advanced Monitoring & Logging System")
    print("🌐 Vietnamese Localized Interface\n")
    
    while True:
        choice = manager.show_menu()
        
        if choice == "1":
            manager.setup_monitoring_stack()
            
        elif choice == "2":
            manager.check_monitoring_health()
            
        elif choice == "3":
            service = input("📜 Service name (hoặc 'all' cho tất cả): ").strip()
            follow = input("🔄 Follow logs? (y/n): ").strip().lower() == 'y'
            manager.view_logs(service, follow)
            
        elif choice == "4":
            service = input("🔄 Service name (hoặc 'all' cho tất cả): ").strip()
            manager.restart_monitoring(service)
            
        elif choice == "5":
            manager.stop_monitoring()
            
        elif choice == "6":
            manager.cleanup_monitoring()
            
        elif choice == "7":
            manager.setup_kibana_dashboards()
            
        elif choice == "8":
            manager.display_monitoring_urls()
            
        elif choice == "9":
            print("\n📚 HELP & DOCUMENTATION:")
            print("🔗 GitHub: https://github.com/your-repo/airbnb-webapp")
            print("📖 Wiki: https://wiki.company.com/airbnb-monitoring")
            print("💬 Slack: #airbnb-devops")
            print("📧 Email: devops@your-company.com")
            
        elif choice == "0":
            print("👋 Goodbye! Cảm ơn bạn đã sử dụng Monitoring Manager!")
            break
            
        else:
            print("❌ Invalid option. Vui lòng chọn 0-9.")
            
        input("\n📝 Press Enter để tiếp tục...")

if __name__ == "__main__":
    main()