#!/usr/bin/env python3
"""
AIRBNB WEBAPP - Database Performance Validation
Kiểm tra hiệu suất cơ sở dữ liệu sau khi tối ưu
Author: AI Assistant
Created: 2024-12-28
"""

import time
import asyncio
from datetime import datetime, date, timedelta
from sqlmodel import Session, select, text
from typing import Dict, List, Any
import logging

from db import get_session_context
from models import User, Property, Booking, Expense, ExpenseCategory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabasePerformanceValidator:
    """Validator cho hiệu suất database sau optimization"""
    
    def __init__(self):
        self.results = {}
    
    def measure_query_time(self, query_name: str, query_func) -> float:
        """Đo thời gian thực thi query"""
        start_time = time.time()
        try:
            result = query_func()
            execution_time = time.time() - start_time
            logger.info(f"✅ {query_name}: {execution_time:.4f}s")
            return execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {query_name}: {execution_time:.4f}s - ERROR: {e}")
            return execution_time
    
    def test_user_queries(self, session: Session) -> Dict[str, float]:
        """Test User model queries với indexes"""
        results = {}
        
        # Test 1: Role-based user lookup
        results['user_by_role'] = self.measure_query_time(
            "User by Role Query",
            lambda: session.exec(select(User).where(User.role == "admin")).all()
        )
        
        # Test 2: Active users lookup
        results['active_users'] = self.measure_query_time(
            "Active Users Query", 
            lambda: session.exec(select(User).where(User.is_active == True)).all()
        )
        
        # Test 3: User login analytics (composite index)
        results['user_login_analytics'] = self.measure_query_time(
            "User Login Analytics",
            lambda: session.exec(select(User).where(
                User.role == "manager",
                User.is_active == True,
                User.last_login.isnot(None)
            )).all()
        )
        
        return results
    
    def test_property_queries(self, session: Session) -> Dict[str, float]:
        """Test Property model queries với indexes"""
        results = {}
        
        # Test 1: Active properties per building
        results['property_building_active'] = self.measure_query_time(
            "Active Properties per Building",
            lambda: session.exec(select(Property).where(
                Property.building_id == 1,
                Property.is_active == True
            )).all()
        )
        
        # Test 2: Property type + price filtering
        results['property_type_price'] = self.measure_query_time(
            "Property Type & Price Filter",
            lambda: session.exec(select(Property).where(
                Property.room_type == "studio",
                Property.price_per_night.between(1000000, 2000000)
            )).all()
        )
        
        return results
    
    def test_booking_queries(self, session: Session) -> Dict[str, float]:
        """Test Booking model queries - quan trọng nhất"""
        results = {}
        
        # Test date range cho availability check
        today = date.today()
        next_month = today + timedelta(days=30)
        
        # Test 1: Date range availability (core booking query)
        results['booking_date_range'] = self.measure_query_time(
            "Booking Date Range Query",
            lambda: session.exec(select(Booking).where(
                Booking.start_date >= today,
                Booking.end_date <= next_month
            )).all()
        )
        
        # Test 2: Property availability (composite index)
        results['property_availability'] = self.measure_query_time(
            "Property Availability Query",
            lambda: session.exec(select(Booking).where(
                Booking.property_id == 1,
                Booking.start_date >= today,
                Booking.end_date <= next_month
            )).all()
        )
        
        # Test 3: Revenue reporting (composite index)
        results['booking_revenue'] = self.measure_query_time(
            "Booking Revenue Query",
            lambda: session.exec(select(Booking).where(
                Booking.property_id == 1,
                Booking.booking_date >= today - timedelta(days=90),
                Booking.total_payout_vnd.isnot(None)
            )).all()
        )
        
        # Test 4: Channel performance
        results['channel_performance'] = self.measure_query_time(
            "Channel Performance Query",
            lambda: session.exec(select(Booking).where(
                Booking.channel_id == 1,
                Booking.status == "confirmed"
            )).all()
        )
        
        return results
    
    def test_expense_queries(self, session: Session) -> Dict[str, float]:
        """Test Expense model queries với indexes"""
        results = {}
        
        # Test 1: Property monthly expenses
        results['expense_property_month'] = self.measure_query_time(
            "Property Monthly Expenses",
            lambda: session.exec(select(Expense).where(
                Expense.property_id == 1,
                Expense.month == "2024-12"
            )).all()
        )
        
        # Test 2: Category analysis
        results['expense_category_analysis'] = self.measure_query_time(
            "Expense Category Analysis",
            lambda: session.exec(select(Expense).where(
                Expense.category_id == 1,
                Expense.month >= "2024-10"
            )).all()
        )
        
        # Test 3: Vendor performance
        results['vendor_performance'] = self.measure_query_time(
            "Vendor Performance Query",
            lambda: session.exec(select(Expense).where(
                Expense.vendor == "Test Vendor",
                Expense.amount > 100000
            )).all()
        )
        
        return results
    
    def test_complex_queries(self, session: Session) -> Dict[str, float]:
        """Test complex queries sử dụng multiple indexes"""
        results = {}
        
        # Test 1: Property financial summary (JOIN multiple tables)
        results['property_financial_summary'] = self.measure_query_time(
            "Property Financial Summary",
            lambda: session.exec(text("""
                SELECT p.id, p.room_number, 
                       COUNT(b.id) as booking_count,
                       SUM(b.total_payout_vnd) as total_revenue,
                       SUM(e.amount) as total_expenses
                FROM property p 
                LEFT JOIN booking b ON p.id = b.property_id 
                LEFT JOIN expenses e ON p.id = e.property_id 
                WHERE p.is_active = true 
                GROUP BY p.id, p.room_number
                LIMIT 10
            """)).all()
        )
        
        # Test 2: Monthly performance report
        results['monthly_performance'] = self.measure_query_time(
            "Monthly Performance Report",
            lambda: session.exec(text("""
                SELECT 
                    DATE_TRUNC('month', b.booking_date) as month,
                    COUNT(b.id) as bookings,
                    AVG(b.total_payout_vnd) as avg_revenue,
                    SUM(e.amount) as total_expenses
                FROM booking b
                LEFT JOIN expenses e ON b.property_id = e.property_id 
                    AND DATE_TRUNC('month', b.booking_date::date) = DATE_TRUNC('month', e.date::date)
                WHERE b.booking_date >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY DATE_TRUNC('month', b.booking_date)
                ORDER BY month DESC
                LIMIT 6
            """)).all()
        )
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Chạy tất cả performance tests"""
        logger.info("🚀 Bắt đầu Database Performance Validation...")
        
        with get_session_context() as session:
            self.results['user_queries'] = self.test_user_queries(session)
            self.results['property_queries'] = self.test_property_queries(session)
            self.results['booking_queries'] = self.test_booking_queries(session)
            self.results['expense_queries'] = self.test_expense_queries(session)
            self.results['complex_queries'] = self.test_complex_queries(session)
        
        return self.results
    
    def generate_performance_report(self) -> str:
        """Tạo báo cáo hiệu suất"""
        report = "\n" + "="*60 + "\n"
        report += "📊 DATABASE PERFORMANCE VALIDATION REPORT\n"
        report += "="*60 + "\n"
        
        total_queries = 0
        total_time = 0
        
        for category, queries in self.results.items():
            report += f"\n🔍 {category.upper()}:\n"
            report += "-" * 40 + "\n"
            
            for query_name, execution_time in queries.items():
                status = "✅" if execution_time < 0.1 else "⚠️" if execution_time < 0.5 else "❌"
                report += f"{status} {query_name}: {execution_time:.4f}s\n"
                total_queries += 1
                total_time += execution_time
        
        # Summary
        avg_time = total_time / total_queries if total_queries > 0 else 0
        report += "\n" + "="*60 + "\n"
        report += f"📈 TỔNG KẾT:\n"
        report += f"   • Tổng số queries: {total_queries}\n"
        report += f"   • Tổng thời gian: {total_time:.4f}s\n"
        report += f"   • Thời gian trung bình: {avg_time:.4f}s\n"
        
        # Performance thresholds
        if avg_time < 0.1:
            report += f"   • Kết quả: 🟢 XUẤT SẮC (< 0.1s)\n"
        elif avg_time < 0.5:
            report += f"   • Kết quả: 🟡 TỐT (< 0.5s)\n"
        else:
            report += f"   • Kết quả: 🔴 CẦN CẢI THIỆN (> 0.5s)\n"
            
        report += "="*60 + "\n"
        
        return report

def main():
    """Main function để chạy performance validation"""
    validator = DatabasePerformanceValidator()
    
    try:
        # Chạy tất cả tests
        results = validator.run_all_tests()
        
        # Tạo và hiển thị report
        report = validator.generate_performance_report()
        print(report)
        
        # Lưu report vào file
        with open('performance_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("✅ Performance validation hoàn thành!")
        logger.info("📄 Báo cáo đã được lưu vào: performance_report.txt")
        
    except Exception as e:
        logger.error(f"❌ Lỗi trong quá trình validation: {e}")
        raise

if __name__ == "__main__":
    main()