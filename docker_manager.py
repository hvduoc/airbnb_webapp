#!/usr/bin/env python3
"""
AIRBNB WEBAPP - Docker Management Scripts
Scripts quản lý Docker containers cho development và production
Author: AI Assistant
Created: 2024-12-28
"""

import os
import subprocess
import sys
import time
from pathlib import Path


class DockerManager:
    """Manager class cho Docker operations"""

    def __init__(self):
        self.project_name = "airbnb-webapp"
        self.project_dir = Path(__file__).parent

    def run_command(self, command, check=True):
        """Execute shell command"""
        print(f"🔧 Executing: {command}")
        try:
            result = subprocess.run(
                command, shell=True, check=check, capture_output=True, text=True
            )
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            raise

    def check_docker(self):
        """Kiểm tra Docker có sẵn không"""
        try:
            self.run_command("docker --version")
            self.run_command("docker-compose --version")
            print("✅ Docker và Docker Compose đã sẵn sàng!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Docker hoặc Docker Compose chưa được cài đặt!")
            return False

    def create_required_directories(self):
        """Tạo các thư mục cần thiết cho volumes"""
        directories = [
            "data/postgres",
            "data/redis",
            "data/prometheus",
            "data/grafana",
            "logs",
            "uploads",
            "backups",
            "ssl",
        ]

        for directory in directories:
            dir_path = self.project_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")

    def setup_development(self):
        """Setup development environment"""
        print("🚀 Setting up Development Environment...")

        if not self.check_docker():
            return False

        self.create_required_directories()

        # Build và start development containers
        print("🏗️ Building development containers...")
        self.run_command("docker-compose -f docker-compose.dev.yml build")

        print("▶️ Starting development services...")
        self.run_command("docker-compose -f docker-compose.dev.yml up -d")

        # Chờ services khởi động
        print("⏳ Waiting for services to start...")
        time.sleep(10)

        # Check service status
        self.check_services_health("dev")

        print("✅ Development environment ready!")
        print("🌐 Application: http://localhost:8000")
        print("🗄️ Adminer: http://localhost:8080")
        print("📊 API Docs: http://localhost:8000/docs")

        return True

    def setup_production(self):
        """Setup production environment"""
        print("🚀 Setting up Production Environment...")

        if not self.check_docker():
            return False

        self.create_required_directories()

        # Check environment variables
        required_env_vars = ["POSTGRES_PASSWORD", "REDIS_PASSWORD", "SECRET_KEY"]
        missing_vars = []

        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
            print("📋 Please set these variables or create a .env file")
            return False

        # Build và start production containers
        print("🏗️ Building production containers...")
        self.run_command("docker-compose build")

        print("▶️ Starting production services...")
        self.run_command("docker-compose up -d")

        # Chờ services khởi động
        print("⏳ Waiting for services to start...")
        time.sleep(30)

        # Check service status
        self.check_services_health("prod")

        print("✅ Production environment ready!")
        print("🌐 Application: http://localhost")
        print("📊 Grafana: http://localhost:3000")
        print("🔍 Prometheus: http://localhost:9090")

        return True

    def check_services_health(self, env_type="dev"):
        """Kiểm tra tình trạng sức khỏe của services"""
        print("🏥 Checking services health...")

        compose_file = (
            "docker-compose.dev.yml" if env_type == "dev" else "docker-compose.yml"
        )

        # List running containers
        self.run_command(f"docker-compose -f {compose_file} ps", check=False)

        # Check health của webapp
        try:
            health_check = self.run_command(
                "curl -s http://localhost:8000/health", check=False
            )
            if health_check.returncode == 0:
                print("✅ WebApp health check passed")
            else:
                print("❌ WebApp health check failed")
        except:
            print("⚠️ Could not reach health endpoint")

    def stop_services(self, env_type="dev"):
        """Dừng services"""
        compose_file = (
            "docker-compose.dev.yml" if env_type == "dev" else "docker-compose.yml"
        )
        print(f"🛑 Stopping {env_type} services...")
        self.run_command(f"docker-compose -f {compose_file} down")
        print("✅ Services stopped")

    def cleanup(self, env_type="dev"):
        """Cleanup containers và volumes"""
        compose_file = (
            "docker-compose.dev.yml" if env_type == "dev" else "docker-compose.yml"
        )
        print(f"🧹 Cleaning up {env_type} environment...")
        self.run_command(f"docker-compose -f {compose_file} down -v --remove-orphans")
        print("✅ Cleanup completed")

    def logs(self, service=None, env_type="dev"):
        """Xem logs của services"""
        compose_file = (
            "docker-compose.dev.yml" if env_type == "dev" else "docker-compose.yml"
        )

        if service:
            self.run_command(f"docker-compose -f {compose_file} logs -f {service}")
        else:
            self.run_command(f"docker-compose -f {compose_file} logs -f")

    def rebuild(self, env_type="dev"):
        """Rebuild containers"""
        compose_file = (
            "docker-compose.dev.yml" if env_type == "dev" else "docker-compose.yml"
        )
        print(f"🔨 Rebuilding {env_type} containers...")
        self.run_command(f"docker-compose -f {compose_file} build --no-cache")
        print("✅ Rebuild completed")


def main():
    """Main CLI interface"""
    manager = DockerManager()

    if len(sys.argv) < 2:
        print("""
🐳 AIRBNB WEBAPP - Docker Management

Available commands:
  dev-setup     - Setup development environment
  prod-setup    - Setup production environment
  stop-dev      - Stop development services
  stop-prod     - Stop production services
  cleanup-dev   - Cleanup development environment
  cleanup-prod  - Cleanup production environment
  logs          - View all logs
  logs-webapp   - View webapp logs
  rebuild-dev   - Rebuild development containers
  rebuild-prod  - Rebuild production containers
  health        - Check services health

Examples:
  python docker_manager.py dev-setup
  python docker_manager.py logs-webapp
  python docker_manager.py stop-dev
        """)
        return

    command = sys.argv[1]

    try:
        if command == "dev-setup":
            manager.setup_development()
        elif command == "prod-setup":
            manager.setup_production()
        elif command == "stop-dev":
            manager.stop_services("dev")
        elif command == "stop-prod":
            manager.stop_services("prod")
        elif command == "cleanup-dev":
            manager.cleanup("dev")
        elif command == "cleanup-prod":
            manager.cleanup("prod")
        elif command == "logs":
            manager.logs()
        elif command == "logs-webapp":
            manager.logs("webapp-dev", "dev")
        elif command == "rebuild-dev":
            manager.rebuild("dev")
        elif command == "rebuild-prod":
            manager.rebuild("prod")
        elif command == "health":
            manager.check_services_health()
        else:
            print(f"❌ Unknown command: {command}")

    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
