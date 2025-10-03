#!/usr/bin/env python3
"""
AIRBNB WEBAPP - Database Index Monitoring System
Hệ thống giám sát và tối ưu hóa indexes
Author: AI Assistant
Created: 2024-12-28
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from sqlmodel import Session, text

from db import get_session_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseIndexMonitor:
    """Monitor và phân tích hiệu quả của database indexes"""
    
    def __init__(self):
        self.index_stats = {}
        self.recommendations = []
    
    def analyze_index_usage(self, session: Session) -> Dict[str, Any]:
        """Phân tích việc sử dụng indexes"""
        
        # Query để lấy thống kê index usage (PostgreSQL specific)
        index_usage_query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan as index_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched,
                CASE 
                    WHEN idx_scan = 0 THEN 'UNUSED'
                    WHEN idx_scan < 10 THEN 'LOW_USAGE'
                    WHEN idx_scan < 100 THEN 'MODERATE_USAGE'
                    ELSE 'HIGH_USAGE'
                END as usage_level
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC
        """)
        
        try:
            results = session.exec(index_usage_query).all()
            
            index_stats = []
            for row in results:
                index_stats.append({
                    'schema': row[0],
                    'table': row[1], 
                    'index': row[2],
                    'scans': row[3],
                    'tuples_read': row[4],
                    'tuples_fetched': row[5],
                    'usage_level': row[6]
                })
            
            self.index_stats['usage'] = index_stats
            return {'index_usage': index_stats}
            
        except Exception as e:
            logger.warning(f"PostgreSQL index stats không khả dụng: {e}")
            return {'index_usage': 'Not available - requires PostgreSQL'}
    
    def analyze_table_sizes(self, session: Session) -> Dict[str, Any]:
        """Phân tích kích thước tables và indexes"""
        
        table_size_query = text("""
            SELECT 
                tablename,
                pg_size_pretty(pg_total_relation_size(tablename::regclass)) as total_size,
                pg_size_pretty(pg_relation_size(tablename::regclass)) as table_size,
                pg_size_pretty(pg_indexes_size(tablename::regclass)) as indexes_size,
                pg_stat_get_tuples_returned(c.oid) as tuples_returned,
                pg_stat_get_tuples_fetched(c.oid) as tuples_fetched
            FROM pg_tables t
            JOIN pg_class c ON c.relname = t.tablename
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(tablename::regclass) DESC
        """)
        
        try:
            results = session.exec(table_size_query).all()
            
            table_stats = []
            for row in results:
                table_stats.append({
                    'table': row[0],
                    'total_size': row[1],
                    'table_size': row[2], 
                    'indexes_size': row[3],
                    'tuples_returned': row[4],
                    'tuples_fetched': row[5]
                })
                
            self.index_stats['table_sizes'] = table_stats
            return {'table_sizes': table_stats}
            
        except Exception as e:
            logger.warning(f"PostgreSQL table stats không khả dụng: {e}")
            return {'table_sizes': 'Not available - requires PostgreSQL'}
    
    def check_missing_indexes(self, session: Session) -> List[str]:
        """Kiểm tra các indexes có thể bị thiếu"""
        
        missing_indexes_query = text("""
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats 
            WHERE schemaname = 'public'
            AND n_distinct > 10  -- Columns with good selectivity
            AND correlation < 0.1  -- Columns with low correlation
            ORDER BY n_distinct DESC
        """)
        
        recommendations = []
        
        try:
            results = session.exec(missing_indexes_query).all()
            
            for row in results:
                table = row[1]
                column = row[2]
                n_distinct = row[3]
                
                # Check if index already exists
                index_check = text(f"""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = '{table}' 
                    AND indexdef LIKE '%{column}%'
                """)
                
                existing = session.exec(index_check).first()
                
                if not existing and n_distinct > 50:
                    recommendations.append(
                        f"Xem xét tạo index cho {table}.{column} (n_distinct: {n_distinct})"
                    )
                    
        except Exception as e:
            logger.warning(f"Missing index analysis không khả dụng: {e}")
            recommendations.append("Missing index analysis - requires PostgreSQL")
        
        self.recommendations.extend(recommendations)
        return recommendations
    
    def analyze_slow_queries(self, session: Session) -> List[str]:
        """Phân tích slow queries có thể cần indexes"""
        
        # Kiểm tra pg_stat_statements extension
        slow_query_analysis = text("""
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                rows
            FROM pg_stat_statements 
            WHERE mean_time > 100  -- Queries > 100ms
            ORDER BY mean_time DESC
            LIMIT 10
        """)
        
        recommendations = []
        
        try:
            results = session.exec(slow_query_analysis).all()
            
            for row in results:
                query = row[0][:100] + "..." if len(row[0]) > 100 else row[0]
                mean_time = row[3]
                
                recommendations.append(
                    f"Slow query ({mean_time:.2f}ms): {query}"
                )
                
        except Exception as e:
            logger.warning(f"Slow query analysis không khả dụng: {e}")
            recommendations.append("Slow query analysis - requires pg_stat_statements extension")
        
        self.recommendations.extend(recommendations)
        return recommendations
    
    def generate_index_recommendations(self) -> List[str]:
        """Tạo các khuyến nghị tối ưu index"""
        
        general_recommendations = [
            "📊 KHUYẾN NGHỊ TỔNG QUÁT:",
            "",
            "✅ Indexes đã được tối ưu cho:",
            "   • User model: role, is_active, last_login composite indexes",
            "   • Property model: building_id, room_type, price_per_night indexes", 
            "   • Booking model: date ranges, property availability, revenue queries",
            "   • Expense model: category, vendor, allocation method indexes",
            "",
            "🔧 KHUYẾN NGHỊ BẢO TRÌ:",
            "   • Chạy ANALYZE định kỳ để cập nhật statistics",
            "   • Monitor index usage với pg_stat_user_indexes",
            "   • Xem xét REINDEX cho tables lớn định kỳ",
            "   • Kiểm tra disk space cho index growth",
            "",
            "⚡ KHUYẾN NGHỊ HIỆU SUẤT:",
            "   • Sử dụng composite indexes cho multi-column WHERE clauses",
            "   • Index foreign keys để tối ưu JOINs",
            "   • Partial indexes cho filtered queries thường xuyên",
            "   • VACUUM ANALYZE sau bulk operations",
        ]
        
        return general_recommendations + self.recommendations
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Chạy phân tích đầy đủ về indexes"""
        logger.info("🔍 Bắt đầu phân tích Database Indexes...")
        
        analysis_results = {}
        
        with get_session_context() as session:
            # Index usage analysis
            analysis_results.update(self.analyze_index_usage(session))
            
            # Table size analysis  
            analysis_results.update(self.analyze_table_sizes(session))
            
            # Missing index recommendations
            missing_indexes = self.check_missing_indexes(session)
            analysis_results['missing_indexes'] = missing_indexes
            
            # Slow query analysis
            slow_queries = self.analyze_slow_queries(session)
            analysis_results['slow_queries'] = slow_queries
            
            # General recommendations
            recommendations = self.generate_index_recommendations()
            analysis_results['recommendations'] = recommendations
        
        return analysis_results
    
    def generate_monitoring_report(self, analysis_results: Dict[str, Any]) -> str:
        """Tạo báo cáo monitoring chi tiết"""
        
        report = "\n" + "="*70 + "\n"
        report += "📈 DATABASE INDEX MONITORING REPORT\n"
        report += "="*70 + "\n"
        report += f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Index Usage Section
        if 'index_usage' in analysis_results:
            report += "🔍 INDEX USAGE ANALYSIS:\n"
            report += "-" * 50 + "\n"
            
            usage_data = analysis_results['index_usage']
            if isinstance(usage_data, str):
                report += f"   {usage_data}\n\n"
            else:
                for idx in usage_data[:10]:  # Top 10 indexes
                    report += f"   📊 {idx['table']}.{idx['index']}\n"
                    report += f"      Scans: {idx['scans']}, Usage: {idx['usage_level']}\n"
                report += "\n"
        
        # Table Sizes Section  
        if 'table_sizes' in analysis_results:
            report += "💾 TABLE SIZE ANALYSIS:\n"
            report += "-" * 50 + "\n"
            
            size_data = analysis_results['table_sizes']
            if isinstance(size_data, str):
                report += f"   {size_data}\n\n"
            else:
                for table in size_data[:5]:  # Top 5 largest tables
                    report += f"   📦 {table['table']}\n"
                    report += f"      Total: {table['total_size']}, "
                    report += f"Indexes: {table['indexes_size']}\n"
                report += "\n"
        
        # Recommendations Section
        if 'recommendations' in analysis_results:
            report += "💡 KHUYẾN NGHỊ:\n"
            report += "-" * 50 + "\n"
            for rec in analysis_results['recommendations']:
                report += f"   {rec}\n"
            report += "\n"
        
        report += "="*70 + "\n"
        
        return report

def main():
    """Main function để chạy index monitoring"""
    monitor = DatabaseIndexMonitor()
    
    try:
        # Chạy full analysis
        results = monitor.run_full_analysis()
        
        # Tạo và hiển thị report
        report = monitor.generate_monitoring_report(results)
        print(report)
        
        # Lưu detailed results
        with open('index_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        
        # Lưu report
        with open('index_monitoring_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("✅ Index monitoring hoàn thành!")
        logger.info("📄 Báo cáo chi tiết: index_monitoring_report.txt")
        logger.info("📊 Dữ liệu JSON: index_analysis.json")
        
    except Exception as e:
        logger.error(f"❌ Lỗi trong quá trình monitoring: {e}")
        raise

if __name__ == "__main__":
    main()