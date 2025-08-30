"""
Management command to analyze and optimize database performance.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.conf import settings
import logging
import time
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Analyze and optimize database performance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze-queries',
            action='store_true',
            help='Analyze slow queries and suggest optimizations'
        )
        parser.add_argument(
            '--check-indexes',
            action='store_true',
            help='Check for missing indexes and suggest improvements'
        )
        parser.add_argument(
            '--optimize-tables',
            action='store_true',
            help='Optimize table structure and analyze statistics'
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Run VACUUM ANALYZE on PostgreSQL tables'
        )
        parser.add_argument(
            '--report-only',
            action='store_true',
            help='Generate report without making changes'
        )
        parser.add_argument(
            '--table',
            type=str,
            help='Focus on specific table'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Starting Database Performance Analysis')
        )
        
        try:
            if options['analyze_queries']:
                self.analyze_slow_queries()
            
            if options['check_indexes']:
                self.check_missing_indexes(options.get('table'))
            
            if options['optimize_tables']:
                self.optimize_table_structure(options.get('table'))
            
            if options['vacuum'] and not options['report_only']:
                self.vacuum_analyze_tables(options.get('table'))
            
            # If no specific option, run all analyses
            if not any([
                options['analyze_queries'],
                options['check_indexes'], 
                options['optimize_tables'],
                options['vacuum']
            ]):
                self.run_full_analysis(options.get('table'), options['report_only'])
            
            self.stdout.write(
                self.style.SUCCESS('✅ Database performance analysis completed')
            )
            
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
            raise CommandError(f"Database optimization failed: {e}")
    
    def analyze_slow_queries(self):
        """Analyze slow queries and provide optimization suggestions"""
        self.stdout.write("📊 Analyzing slow queries...")
        
        with connection.cursor() as cursor:
            try:
                # Check if pg_stat_statements extension is available
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                    );
                """)
                
                has_pg_stat_statements = cursor.fetchone()[0]
                
                if has_pg_stat_statements:
                    # Get slow queries from pg_stat_statements
                    cursor.execute("""
                        SELECT 
                            query,
                            calls,
                            total_time,
                            mean_time,
                            rows,
                            100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                        FROM pg_stat_statements 
                        WHERE mean_time > 100  -- Queries taking more than 100ms on average
                        ORDER BY mean_time DESC 
                        LIMIT 10;
                    """)
                    
                    slow_queries = cursor.fetchall()
                    
                    if slow_queries:
                        self.stdout.write("🐌 Top 10 Slow Queries:")
                        for i, query_data in enumerate(slow_queries, 1):
                            query, calls, total_time, mean_time, rows, hit_percent = query_data
                            self.stdout.write(f"\n{i}. Query (avg: {mean_time:.2f}ms, calls: {calls}):")
                            self.stdout.write(f"   {query[:100]}...")
                            if hit_percent:
                                self.stdout.write(f"   Cache hit ratio: {hit_percent:.1f}%")
                            
                            # Provide optimization suggestions
                            suggestions = self.get_query_optimization_suggestions(query, mean_time, hit_percent)
                            for suggestion in suggestions:
                                self.stdout.write(f"   💡 {suggestion}")
                    else:
                        self.stdout.write("✅ No slow queries found")
                else:
                    self.stdout.write("⚠️ pg_stat_statements extension not available")
                    self.stdout.write("   Enable it with: CREATE EXTENSION pg_stat_statements;")
                    
            except Exception as e:
                self.stdout.write(f"❌ Error analyzing queries: {e}")
    
    def get_query_optimization_suggestions(self, query: str, mean_time: float, hit_percent: float) -> List[str]:
        """Generate optimization suggestions for a query"""
        suggestions = []
        
        query_lower = query.lower()
        
        # Check for missing WHERE clauses
        if 'select' in query_lower and 'where' not in query_lower and 'limit' not in query_lower:
            suggestions.append("Consider adding WHERE clause to limit results")
        
        # Check for SELECT *
        if 'select *' in query_lower:
            suggestions.append("Avoid SELECT *, specify only needed columns")
        
        # Check for missing indexes
        if 'where' in query_lower and mean_time > 500:
            suggestions.append("Consider adding indexes on WHERE clause columns")
        
        # Check for JOINs without proper indexes
        if 'join' in query_lower and mean_time > 200:
            suggestions.append("Ensure JOIN columns are properly indexed")
        
        # Check cache hit ratio
        if hit_percent and hit_percent < 90:
            suggestions.append(f"Low cache hit ratio ({hit_percent:.1f}%) - check buffer pool size")
        
        # Check for ORDER BY without LIMIT
        if 'order by' in query_lower and 'limit' not in query_lower:
            suggestions.append("ORDER BY without LIMIT can be expensive - consider pagination")
        
        return suggestions
    
    def check_missing_indexes(self, table_name: str = None):
        """Check for missing indexes and suggest improvements"""
        self.stdout.write("🔍 Checking for missing indexes...")
        
        with connection.cursor() as cursor:
            try:
                # Get table statistics
                table_filter = f"AND tablename = '{table_name}'" if table_name else ""
                
                cursor.execute(f"""
                    SELECT 
                        schemaname,
                        tablename,
                        attname,
                        n_distinct,
                        correlation,
                        null_frac
                    FROM pg_stats 
                    WHERE schemaname = 'public'
                    AND n_distinct > 100  -- High cardinality columns
                    {table_filter}
                    ORDER BY n_distinct DESC;
                """)
                
                high_cardinality_columns = cursor.fetchall()
                
                if high_cardinality_columns:
                    self.stdout.write("📈 High cardinality columns (consider indexing):")
                    for schema, table, column, n_distinct, correlation, null_frac in high_cardinality_columns:
                        self.stdout.write(f"  {table}.{column}: {n_distinct} distinct values")
                        
                        # Check if index already exists
                        cursor.execute("""
                            SELECT COUNT(*) FROM pg_indexes 
                            WHERE tablename = %s AND indexdef LIKE %s;
                        """, [table, f'%{column}%'])
                        
                        has_index = cursor.fetchone()[0] > 0
                        
                        if not has_index:
                            self.stdout.write(f"    💡 Consider: CREATE INDEX idx_{table}_{column} ON {table}({column});")
                        else:
                            self.stdout.write(f"    ✅ Index exists")
                
                # Check for foreign keys without indexes
                cursor.execute(f"""
                    SELECT 
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                    {table_filter.replace('tablename', 'tc.table_name') if table_filter else ''}
                    ORDER BY tc.table_name, kcu.column_name;
                """)
                
                foreign_keys = cursor.fetchall()
                
                if foreign_keys:
                    self.stdout.write("\n🔗 Foreign key columns (should be indexed):")
                    for table, column, foreign_table, foreign_column in foreign_keys:
                        # Check if index exists
                        cursor.execute("""
                            SELECT COUNT(*) FROM pg_indexes 
                            WHERE tablename = %s AND indexdef LIKE %s;
                        """, [table, f'%{column}%'])
                        
                        has_index = cursor.fetchone()[0] > 0
                        
                        if not has_index:
                            self.stdout.write(f"  ❌ {table}.{column} -> {foreign_table}.{foreign_column}")
                            self.stdout.write(f"    💡 CREATE INDEX idx_{table}_{column} ON {table}({column});")
                        else:
                            self.stdout.write(f"  ✅ {table}.{column} -> {foreign_table}.{foreign_column}")
                
            except Exception as e:
                self.stdout.write(f"❌ Error checking indexes: {e}")
    
    def optimize_table_structure(self, table_name: str = None):
        """Analyze table structure and suggest optimizations"""
        self.stdout.write("🔧 Analyzing table structure...")
        
        with connection.cursor() as cursor:
            try:
                # Get table sizes
                table_filter = f"AND tablename = '{table_name}'" if table_name else ""
                
                cursor.execute(f"""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                        pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    {table_filter}
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
                """)
                
                tables = cursor.fetchall()
                
                self.stdout.write("📊 Table sizes:")
                for schema, table, size, size_bytes in tables:
                    self.stdout.write(f"  {table}: {size}")
                    
                    # Analyze table statistics
                    cursor.execute(f"""
                        SELECT 
                            n_tup_ins,
                            n_tup_upd,
                            n_tup_del,
                            n_live_tup,
                            n_dead_tup,
                            last_vacuum,
                            last_autovacuum,
                            last_analyze,
                            last_autoanalyze
                        FROM pg_stat_user_tables 
                        WHERE relname = %s;
                    """, [table])
                    
                    stats = cursor.fetchone()
                    if stats:
                        n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup, last_vacuum, last_autovacuum, last_analyze, last_autoanalyze = stats
                        
                        # Check for bloat
                        if n_dead_tup > n_live_tup * 0.1:  # More than 10% dead tuples
                            self.stdout.write(f"    ⚠️ High dead tuple ratio: {n_dead_tup}/{n_live_tup}")
                            self.stdout.write(f"    💡 Consider VACUUM {table};")
                        
                        # Check analyze freshness
                        if not last_analyze and not last_autoanalyze:
                            self.stdout.write(f"    ⚠️ Table never analyzed")
                            self.stdout.write(f"    💡 Run ANALYZE {table};")
                
            except Exception as e:
                self.stdout.write(f"❌ Error analyzing table structure: {e}")
    
    def vacuum_analyze_tables(self, table_name: str = None):
        """Run VACUUM ANALYZE on tables"""
        self.stdout.write("🧹 Running VACUUM ANALYZE...")
        
        with connection.cursor() as cursor:
            try:
                if table_name:
                    tables = [table_name]
                else:
                    # Get all user tables
                    cursor.execute("""
                        SELECT tablename FROM pg_tables 
                        WHERE schemaname = 'public'
                        ORDER BY tablename;
                    """)
                    tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    self.stdout.write(f"  Processing {table}...")
                    start_time = time.time()
                    
                    # Run VACUUM ANALYZE
                    cursor.execute(f"VACUUM ANALYZE {table};")
                    
                    duration = time.time() - start_time
                    self.stdout.write(f"    ✅ Completed in {duration:.2f}s")
                
            except Exception as e:
                self.stdout.write(f"❌ Error running VACUUM ANALYZE: {e}")
    
    def run_full_analysis(self, table_name: str = None, report_only: bool = False):
        """Run complete database performance analysis"""
        self.stdout.write("🔍 Running full database performance analysis...")
        
        self.analyze_slow_queries()
        self.check_missing_indexes(table_name)
        self.optimize_table_structure(table_name)
        
        if not report_only:
            self.vacuum_analyze_tables(table_name)
        
        # Generate summary report
        self.generate_performance_report()
    
    def generate_performance_report(self):
        """Generate a comprehensive performance report"""
        self.stdout.write("\n📋 Performance Report Summary:")
        
        with connection.cursor() as cursor:
            try:
                # Database size
                cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
                db_size = cursor.fetchone()[0]
                self.stdout.write(f"  Database size: {db_size}")
                
                # Connection count
                cursor.execute("SELECT count(*) FROM pg_stat_activity;")
                connections = cursor.fetchone()[0]
                self.stdout.write(f"  Active connections: {connections}")
                
                # Cache hit ratio
                cursor.execute("""
                    SELECT 
                        sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_ratio
                    FROM pg_statio_user_tables;
                """)
                cache_hit = cursor.fetchone()[0]
                if cache_hit:
                    self.stdout.write(f"  Cache hit ratio: {cache_hit:.1f}%")
                    if cache_hit < 90:
                        self.stdout.write("    ⚠️ Consider increasing shared_buffers")
                
                # Index usage
                cursor.execute("""
                    SELECT 
                        sum(idx_scan) / (sum(seq_scan) + sum(idx_scan)) * 100 as index_usage_ratio
                    FROM pg_stat_user_tables
                    WHERE seq_scan + idx_scan > 0;
                """)
                index_usage = cursor.fetchone()[0]
                if index_usage:
                    self.stdout.write(f"  Index usage ratio: {index_usage:.1f}%")
                    if index_usage < 80:
                        self.stdout.write("    ⚠️ Low index usage - check for missing indexes")
                
            except Exception as e:
                self.stdout.write(f"❌ Error generating report: {e}")
        
        self.stdout.write("\n💡 Recommendations:")
        self.stdout.write("  1. Monitor slow queries regularly")
        self.stdout.write("  2. Keep table statistics up to date with ANALYZE")
        self.stdout.write("  3. Add indexes for frequently queried columns")
        self.stdout.write("  4. Use EXPLAIN ANALYZE to understand query plans")
        self.stdout.write("  5. Consider partitioning for very large tables")