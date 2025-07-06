"""
Detailed Error Analysis Report Generator
"""
import json
import os
from datetime import datetime
from pathlib import Path

def analyze_error_logs():
    """Generate detailed error analysis report"""
    
    print("=" * 70)
    print("🔍 DETAILED ERROR ANALYSIS REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    logs_dir = Path("logs")
    error_dir = logs_dir / "errors"
    
    if not error_dir.exists():
        print("❌ Error logs directory not found!")
        return
    
    # Analyze error log files
    error_files = list(error_dir.glob("*.log"))
    critical_files = list(error_dir.glob("critical_error_*.json"))
    
    print(f"\n📁 Found {len(error_files)} error log files")
    print(f"📁 Found {len(critical_files)} critical error files")
    
    # Parse main error log
    total_errors = 0
    error_types = {}
    error_modules = {}
    error_contexts = {}
    
    for error_file in error_files:
        print(f"\n📄 Analyzing: {error_file.name}")
        
        try:
            with open(error_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Count JSON error entries
                entries = []
                current_entry = ""
                brace_count = 0
                
                for line in content.split('\n'):
                    if line.strip():
                        # Extract JSON from log line
                        if ' - {' in line:
                            json_start = line.find(' - {')
                            json_part = line[json_start + 3:]
                            current_entry = json_part
                            brace_count = json_part.count('{') - json_part.count('}')
                        elif current_entry and brace_count != 0:
                            current_entry += '\n' + line
                            brace_count += line.count('{') - line.count('}')
                        
                        if current_entry and brace_count == 0:
                            try:
                                error_data = json.loads(current_entry)
                                entries.append(error_data)
                                current_entry = ""
                            except json.JSONDecodeError:
                                current_entry = ""
                
                # Analyze entries
                for entry in entries:
                    total_errors += 1
                    
                    error_type = entry.get('error_type', 'Unknown')
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                    
                    module = entry.get('module', 'Unknown')
                    error_modules[module] = error_modules.get(module, 0) + 1
                    
                    context = entry.get('context', {})
                    if context:
                        for key, value in context.items():
                            context_key = f"{key}:{value}"
                            error_contexts[context_key] = error_contexts.get(context_key, 0) + 1
                
                print(f"  📊 Found {len(entries)} error entries")
                
        except Exception as e:
            print(f"  ❌ Error reading {error_file}: {e}")
    
    # Print summary
    print(f"\n" + "="*50)
    print(f"📊 ERROR SUMMARY")
    print(f"="*50)
    print(f"Total Errors: {total_errors}")
    
    if error_types:
        print(f"\n🎯 Error Types:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {error_type}: {count}")
    
    if error_modules:
        print(f"\n📦 Error Modules:")
        for module, count in sorted(error_modules.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {module}: {count}")
    
    if error_contexts:
        print(f"\n🔍 Error Contexts (Top 10):")
        for context, count in sorted(error_contexts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {context}: {count}")
    
    # Analyze critical errors
    if critical_files:
        print(f"\n" + "="*50)
        print(f"🚨 CRITICAL ERRORS ANALYSIS")
        print(f"="*50)
        
        for critical_file in critical_files:
            print(f"\n📄 {critical_file.name}")
            try:
                with open(critical_file, 'r', encoding='utf-8') as f:
                    critical_data = json.load(f)
                    print(f"  🎯 Type: {critical_data.get('error_type', 'Unknown')}")
                    print(f"  💬 Message: {critical_data.get('error_message', 'No message')}")
                    print(f"  📦 Module: {critical_data.get('module', 'Unknown')}")
                    
                    context = critical_data.get('context', {})
                    if context:
                        print(f"  🔍 Context:")
                        for key, value in context.items():
                            print(f"    - {key}: {value}")
            except Exception as e:
                print(f"  ❌ Error reading critical file: {e}")
    
    # Check other log files for additional insights
    print(f"\n" + "="*50)
    print(f"📋 OTHER LOG FILES STATUS")
    print(f"="*50)
    
    log_types = ["debug", "chat", "performance"]
    for log_type in log_types:
        log_dir = logs_dir / log_type
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log"))
            total_size = sum(f.stat().st_size for f in log_files)
            print(f"📁 {log_type.title()}: {len(log_files)} files, {total_size/1024:.2f} KB")
        else:
            print(f"📁 {log_type.title()}: Directory not found")
    
    print(f"\n" + "="*70)
    print("✅ Error analysis completed!")
    print("💡 Use this information to identify and fix recurring issues.")
    print(f"="*70)

if __name__ == "__main__":
    analyze_error_logs()
