"""
Log Analysis Tool for AI Agent
Provides summary and analysis of all logs
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import sys

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.logging import agent_logger

def analyze_logs():
    """Analyze and display log summaries"""
    print("=== AI Agent Log Analysis ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    logs_dir = Path("./logs")
    
    if not logs_dir.exists():
        print("❌ No logs directory found")
        return
    
    # Error Analysis
    print("\n📊 ERROR ANALYSIS:")
    error_summary = agent_logger.create_error_summary()
    if error_summary["total_errors"] > 0:
        print(f"🚨 Total Errors Today: {error_summary['total_errors']}")
        print("Error Types:")
        for error_type, count in error_summary["error_types"].items():
            print(f"  - {error_type}: {count}")
    else:
        print("✅ No errors today")
    
    # Recent Logs Summary
    print("\n📂 LOG FILES SUMMARY:")
    for log_type in ["errors", "debug", "chat", "performance"]:
        log_dir = logs_dir / log_type
        if log_dir.exists():
            files = list(log_dir.glob("*.log"))
            if files:
                latest_file = max(files, key=lambda f: f.stat().st_mtime)
                size_mb = latest_file.stat().st_size / (1024 * 1024)
                print(f"  📁 {log_type.title()}: {len(files)} files, latest: {latest_file.name} ({size_mb:.2f} MB)")
            else:
                print(f"  📁 {log_type.title()}: No files")
    
    # Performance Analysis
    print("\n⚡ PERFORMANCE ANALYSIS:")
    analyze_performance_logs()
    
    # Chat Statistics
    print("\n💬 CHAT STATISTICS:")
    analyze_chat_logs()

def analyze_performance_logs():
    """Analyze performance logs"""
    today = datetime.now().strftime("%Y-%m-%d")
    perf_file = Path(f"./logs/performance/performance_{today}.log")
    
    if not perf_file.exists():
        print("  No performance data today")
        return
    
    operations = defaultdict(list)
    
    try:
        with open(perf_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        parts = line.split(' - ', 1)
                        if len(parts) == 2:
                            data = json.loads(parts[1])
                            op = data.get('operation', 'unknown')
                            duration = data.get('duration_seconds', 0)
                            operations[op].append(duration)
                    except json.JSONDecodeError:
                        continue
        
        for op, durations in operations.items():
            avg_time = sum(durations) / len(durations)
            max_time = max(durations)
            print(f"  📈 {op}: {len(durations)} calls, avg: {avg_time:.2f}s, max: {max_time:.2f}s")
    
    except Exception as e:
        print(f"  ❌ Error analyzing performance: {e}")

def analyze_chat_logs():
    """Analyze chat interaction logs"""
    today = datetime.now().strftime("%Y-%m-%d")
    chat_file = Path(f"./logs/chat/chat_{today}.log")
    
    if not chat_file.exists():
        print("  No chat data today")
        return
    
    total_chats = 0
    total_response_time = 0
    
    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        parts = line.split(' - ', 1)
                        if len(parts) == 2:
                            data = json.loads(parts[1])
                            total_chats += 1
                            if 'metadata' in data and 'response_time' in data['metadata']:
                                total_response_time += data['metadata']['response_time']
                    except json.JSONDecodeError:
                        continue
        
        if total_chats > 0:
            avg_response_time = total_response_time / total_chats
            print(f"  💬 Total Conversations: {total_chats}")
            print(f"  ⏱️ Average Response Time: {avg_response_time:.2f}s")
        else:
            print("  No chat interactions recorded")
    
    except Exception as e:
        print(f"  ❌ Error analyzing chat logs: {e}")

def show_recent_errors(count=5):
    """Show recent errors in detail"""
    print(f"\n🚨 RECENT ERRORS (Last {count}):")
    
    today = datetime.now().strftime("%Y-%m-%d")
    error_file = Path(f"./logs/errors/errors_{today}.log")
    
    if not error_file.exists():
        print("  No errors today")
        return
    
    errors = []
    try:
        with open(error_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        parts = line.split(' - ERROR - ', 1)
                        if len(parts) == 2:
                            timestamp = parts[0]
                            error_data = json.loads(parts[1])
                            errors.append((timestamp, error_data))
                    except json.JSONDecodeError:
                        continue
        
        # Show last N errors
        for i, (timestamp, error_data) in enumerate(errors[-count:], 1):
            print(f"\n  {i}. {timestamp}")
            print(f"     Type: {error_data.get('error_type', 'Unknown')}")
            print(f"     Message: {error_data.get('error_message', 'No message')}")
            print(f"     Module: {error_data.get('module', 'Unknown')}")
    
    except Exception as e:
        print(f"  ❌ Error reading error logs: {e}")

def cleanup_old_logs(days=7):
    """Clean up logs older than specified days"""
    print(f"\n🧹 CLEANING UP LOGS OLDER THAN {days} DAYS:")
    
    cutoff_date = datetime.now() - timedelta(days=days)
    logs_dir = Path("./logs")
    
    if not logs_dir.exists():
        print("  No logs directory found")
        return
    
    deleted_count = 0
    for log_file in logs_dir.rglob("*.log"):
        if log_file.stat().st_mtime < cutoff_date.timestamp():
            try:
                log_file.unlink()
                deleted_count += 1
                print(f"  🗑️ Deleted: {log_file}")
            except Exception as e:
                print(f"  ❌ Failed to delete {log_file}: {e}")
    
    print(f"  ✅ Cleaned up {deleted_count} old log files")

if __name__ == "__main__":
    analyze_logs()
    print("\n" + "="*50)
    show_recent_errors(3)
    print("\n" + "="*50)
    
    # Ask if user wants to cleanup old logs
    cleanup = input("\nDo you want to cleanup logs older than 7 days? (y/N): ").lower().strip()
    if cleanup == 'y':
        cleanup_old_logs(7)
    
    print("\n🎯 For real-time monitoring, check the streamlit app Debug Info section")
    print("📁 Log files are organized in: ./logs/[errors|debug|chat|performance]/")
