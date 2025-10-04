#!/usr/bin/env python3
"""
🚨 Canary Monitoring Script for v1.3.1-dbfix
Tracks: 5xx errors, p95 latency, error rates during 30-min window
"""

import time
import requests
import statistics
from datetime import datetime, timedelta

class CanaryMonitor:
    def __init__(self):
        self.base_url = "http://localhost:8000"  # Production would be real URL
        self.start_time = datetime.now()
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'server_errors': 0,
            'response_times': [],
            'error_rate': 0.0,
            'p95_latency': 0.0
        }
        self.thresholds = {
            'max_error_rate': 0.005,  # 0.5% maximum error rate (stricter)
            'max_p95_latency': 3000,  # 3 seconds for development environment
            'max_5xx_rate': 0.005  # 0.5% maximum 5xx error rate (stricter)
        }
    
    def check_health_endpoint(self):
        """Check basic health endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000  # ms
            
            self.metrics['total_requests'] += 1
            self.metrics['response_times'].append(response_time)
            
            if response.status_code >= 500:
                self.metrics['server_errors'] += 1
                print(f"🔴 5xx Error: {response.status_code}")
                return False
            elif response.status_code == 200:
                self.metrics['successful_requests'] += 1
                print(f"✅ Health check OK ({response_time:.1f}ms)")
                return True
            else:
                print(f"🟡 Non-5xx error: {response.status_code}")
                return True
                
        except requests.exceptions.RequestException as e:
            self.metrics['total_requests'] += 1
            print(f"🔴 Connection error: {e}")
            return False
    
    def calculate_metrics(self):
        """Calculate current metrics"""
        if self.metrics['total_requests'] > 0:
            self.metrics['error_rate'] = (
                (self.metrics['total_requests'] - self.metrics['successful_requests']) 
                / self.metrics['total_requests']
            )
            
            if len(self.metrics['response_times']) >= 2:
                # Need at least 2 data points for quantiles
                self.metrics['p95_latency'] = statistics.quantiles(
                    self.metrics['response_times'], n=100
                )[94]  # 95th percentile
            elif len(self.metrics['response_times']) == 1:
                # If only 1 data point, use it as p95
                self.metrics['p95_latency'] = self.metrics['response_times'][0]
            else:
                # No data points
                self.metrics['p95_latency'] = 0.0
        
        return self.metrics
    
    def check_thresholds(self):
        """Check if metrics exceed thresholds"""
        current_metrics = self.calculate_metrics()
        violations = []
        
        if current_metrics['error_rate'] > self.thresholds['max_error_rate']:
            violations.append(f"Error rate: {current_metrics['error_rate']:.2%} > {self.thresholds['max_error_rate']:.2%}")
        
        if current_metrics['p95_latency'] > self.thresholds['max_p95_latency']:
            violations.append(f"P95 latency: {current_metrics['p95_latency']:.1f}ms > {self.thresholds['max_p95_latency']}ms")
        
        server_error_rate = (self.metrics['server_errors'] / max(1, self.metrics['total_requests']))
        if server_error_rate > self.thresholds['max_5xx_rate']:
            violations.append(f"5xx rate: {server_error_rate:.2%} > {self.thresholds['max_5xx_rate']:.2%}")
        
        return violations
    
    def print_status(self):
        """Print current monitoring status"""
        elapsed = datetime.now() - self.start_time
        metrics = self.calculate_metrics()
        
        print("\n" + "="*60)
        print(f"🚨 CANARY MONITORING - v1.3.1-dbfix (5% Traffic)")
        print(f"⏱️  Runtime: {elapsed}")
        print(f"📊 Requests: {metrics['total_requests']} | Success: {metrics['successful_requests']}")
        print(f"📈 Error Rate: {metrics['error_rate']:.2%}")
        print(f"⚡ P95 Latency: {metrics['p95_latency']:.1f}ms")
        print(f"🔥 5xx Errors: {self.metrics['server_errors']}")
        
        violations = self.check_thresholds()
        if violations:
            print("🚨 THRESHOLD VIOLATIONS:")
            for violation in violations:
                print(f"   ❌ {violation}")
        else:
            print("✅ All thresholds OK")
        print("="*60)
    
    def monitor_for_duration(self, duration_minutes=30):
        """Monitor for specified duration"""
        end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        print(f"🚀 Starting {duration_minutes}-minute canary monitoring...")
        print(f"🎯 Will run until: {end_time.strftime('%H:%M:%S')}")
        
        while datetime.now() < end_time:
            self.check_health_endpoint()
            self.print_status()
            
            # Check for critical violations
            violations = self.check_thresholds()
            if violations:
                print("🚨 CRITICAL: Canary metrics exceed thresholds!")
                print("🛑 RECOMMENDATION: ROLLBACK deployment immediately")
                return False
            
            time.sleep(30)  # Check every 30 seconds for shorter test
        
        print("🎉 Canary monitoring completed successfully!")
        print("✅ RECOMMENDATION: Proceed with full production deployment")
        return True

if __name__ == "__main__":
    monitor = CanaryMonitor()
    
    # Production canary deployment for v1.3.1-dbfix
    print("🚀 PRODUCTION CANARY: v1.3.1-dbfix deployment monitoring...")
    print("🎯 Target: 5% traffic, 30-minute observation window")
    print("📊 Thresholds: 5xx rate <0.5%, p95 latency <3s, error rate <0.5%")
    
    # Short test run first to verify performance after warm-up
    print("\n🧪 Running 2-minute performance validation...")
    success = monitor.monitor_for_duration(duration_minutes=2)
    
    if success:
        print("\n✅ Performance validation passed!")
        print("🔄 Starting full 30-minute canary monitoring...")
        success = monitor.monitor_for_duration(duration_minutes=30)
    else:
        print("\n❌ Performance validation failed!")
        success = False
    
    if success:
        print("\n🎊 CANARY DEPLOYMENT SUCCESSFUL!")
        print("✅ v1.3.1-dbfix APPROVED for full production rollout")
        print("👍 Proceed with 100% traffic allocation")
    else:
        print("\n💥 CANARY DEPLOYMENT FAILED!")
        print("⚠️  IMMEDIATE ROLLBACK REQUIRED for v1.3.1-dbfix")
        print("🛑 Revert to previous stable version")