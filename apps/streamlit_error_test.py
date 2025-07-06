"""
Test error detection dengan monitoring real-time di Streamlit
"""
import streamlit as st
import asyncio
import sys
import os
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_agent
from src.utils.logging import agent_logger, log_error, log_debug

def test_error_patterns():
    """Test patterns yang bisa menyebabkan error"""
    
    st.header("🔍 Error Detection & Logging Test")
    
    # Show current error status
    st.subheader("📊 Current Error Status")
    try:
        error_summary = agent_logger.create_error_summary()
        if error_summary["total_errors"] > 0:
            st.error(f"🚨 {error_summary['total_errors']} errors detected today")
            st.json(error_summary["error_types"])
        else:
            st.success("✅ No errors detected today")
    except Exception as e:
        st.warning(f"Could not load error summary: {e}")
    
    # Test scenarios
    st.subheader("🧪 Test Error Scenarios")
    
    test_scenarios = {
        "Empty Message": "",
        "Very Long Message": "Test " * 1000,
        "Special Characters": "🤖😀💻@#$%^&*()_+-=[]{}|;':\",./<>?",
        "Unicode Mix": "测试中文العربية русский 日本語 한국어",
        "Tool Request": "Hitung 25 + 15 dan tampilkan file",
        "Complex Query": "Buatkan analisis mendalam tentang implementasi neural network dengan backpropagation",
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚨 Test Invalid Model"):
            try:
                invalid_agent = create_agent(model_type="invalid_model", persona="personal")
            except Exception as e:
                st.error(f"Expected error: {e}")
                log_error(e, {"test": "streamlit_invalid_model"}, "streamlit_test")
    
    with col2:
        if st.button("🚨 Test Invalid Persona"):
            try:
                invalid_persona = create_agent(model_type="gemini", persona="invalid_persona")
            except Exception as e:
                st.error(f"Expected error: {e}")
                log_error(e, {"test": "streamlit_invalid_persona"}, "streamlit_test")
    
    # Test specific scenarios
    for scenario_name, test_message in test_scenarios.items():
        if st.button(f"Test: {scenario_name}"):
            with st.spinner(f"Testing {scenario_name}..."):
                try:
                    start_time = time.time()
                    
                    # Create agent
                    agent = create_agent(model_type="gemini", persona="personal")
                    
                    # Test chat
                    response = await agent.chat(test_message)
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    # Display results
                    st.success(f"✅ {scenario_name} completed in {duration:.2f}s")
                    st.text_area("Response:", response[:500] + "..." if len(response) > 500 else response)
                    
                    # Check for action phase error
                    if "Action failed" in response and "'str' object has no attribute 'get'" in response:
                        st.warning("⚠️ Action phase error detected!")
                        error_context = {
                            "scenario": scenario_name,
                            "message": test_message[:100] + "..." if len(test_message) > 100 else test_message,
                            "response": response,
                            "duration": duration
                        }
                        action_error = Exception(f"Action phase error in scenario: {scenario_name}")
                        log_error(action_error, error_context, "streamlit_test")
                        
                except Exception as e:
                    st.error(f"❌ Error in {scenario_name}: {e}")
                    log_error(e, {"scenario": scenario_name, "test_message": test_message}, "streamlit_test")
    
    # Real-time log monitoring
    st.subheader("📋 Recent Log Entries")
    
    if st.button("🔄 Refresh Logs"):
        st.rerun()
    
    # Show recent errors
    try:
        error_log_path = "logs/errors/errors_2025-07-06.log"
        if os.path.exists(error_log_path):
            with open(error_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    st.text_area("Recent Error Log Entries:", "".join(lines[-10:]), height=300)
                else:
                    st.info("No error log entries yet")
        else:
            st.info("Error log file not found")
    except Exception as e:
        st.error(f"Could not read error log: {e}")

if __name__ == "__main__":
    # Run the test
    test_error_patterns()
