"""
Streamlit Web Interface for AI Personal Assistant Agent
Alternatif yang lebih sederhana untuk web interface
"""

import streamlit as st
import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_agent
from src.config import settings
from src.tools.calculator import CalculatorTool
from src.tools.file_manager import FileManagerTool
from src.utils.logging import agent_logger, log_debug, log_error

# Page configuration
st.set_page_config(
    page_title="AI Personal Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        background-color: #f0f2f6;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .user-message {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        margin-right: 2rem;
        color: #212529;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .assistant-message strong {
        color: #495057;
    }
    
    .user-message strong {
        color: #ffffff;
    }
    
    .tool-result {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 1rem 0;
        color: #2e7d32;
    }
    
    .error-message {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 1rem 0;
        color: #c62828;
    }
    
    /* Ensure text in markdown content is dark */
    .assistant-message p, .assistant-message div, .assistant-message span {
        color: #212529 !important;
    }
    
    .user-message p, .user-message div, .user-message span {
        color: #ffffff !important;
    }
    
    /* Style for code blocks in responses */
    .assistant-message code {
        background-color: #e9ecef;
        color: #d63384;
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 12px;
    }
    
    .assistant-message pre {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 10px;
        border-radius: 5px;
        color: #212529;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Halo! Saya adalah AI Personal Assistant. Saya dapat membantu Anda dengan berbagai tugas seperti kalkulasi, pencarian informasi, manajemen file, dan banyak lagi. Bagaimana saya bisa membantu Anda hari ini?",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        ]
    
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    
    if 'current_model' not in st.session_state:
        st.session_state.current_model = settings.DEFAULT_MODEL
    
    if 'current_persona' not in st.session_state:
        st.session_state.current_persona = 'personal'

def create_agent_sync(model, persona):
    """Create agent synchronously"""
    try:
        # create_agent is synchronous, use correct parameter name
        agent = create_agent(model_type=model, persona=persona)
        return agent, None
    except Exception as e:
        return None, str(e)

def run_async_function(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def display_chat_message(message):
    """Display a chat message"""
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 Anda ({timestamp}):</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant ({timestamp}):</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

async def process_message_async(agent, message):
    """Process message asynchronously"""
    try:
        # First try to use agent if it's available
        if agent is not None:
            response = await agent.chat(message)
            return response, None
        else:
            # Fallback: use tools directly if agent is not available
            return await process_with_tools(message)
    except Exception as e:
        # If agent fails, try fallback tools
        try:
            fallback_response, fallback_error = await process_with_tools(message)
            if fallback_response and not fallback_error:
                return f"⚠️ Agent tidak tersedia, menggunakan tools dasar:\n\n{fallback_response}", None
            else:
                return None, str(e)
        except Exception:
            return None, str(e)

async def process_with_tools(message):
    """Process message using tools directly (fallback when agent is not available)"""
    message_lower = message.lower()
    
    # Check if it's a calculation request
    calc_keywords = ['hitung', 'kalkulasi', 'calculate', '+', '-', '*', '/', '=', 'sqrt', 'sin', 'cos']
    if any(keyword in message_lower for keyword in calc_keywords):
        try:
            calc_tool = CalculatorTool()
            # Extract mathematical expression from message
            import re
            # Simple extraction - look for mathematical expressions
            math_pattern = r'[\d+\-*/().\s]+|sqrt\([^)]+\)|sin\([^)]+\)|cos\([^)]+\)'
            matches = re.findall(math_pattern, message)
            
            if matches:
                expression = max(matches, key=len).strip()
                result = await calc_tool.execute(expression)
                if result.success:
                    calc_result = result.result['result']
                    return f"Hasil kalkulasi: **{expression} = {calc_result}**", None
                else:
                    return f"Maaf, saya tidak dapat menghitung ekspresi tersebut: {result.error}", None
        except Exception as e:
            pass
    
    # Check if it's a file operation request
    file_keywords = ['file', 'folder', 'directory', 'list', 'daftar', 'tampilkan']
    if any(keyword in message_lower for keyword in file_keywords):
        try:
            fm_tool = FileManagerTool()
            result = await fm_tool.execute('list', directory_path='.')
            if result.success:
                items = result.result['items'][:10]  # Show first 10 items
                file_list = "\n".join([f"📁 {item['name']}" if item['type'] == 'directory' 
                                     else f"📄 {item['name']}" for item in items])
                return f"Berikut adalah daftar file dan folder:\n\n{file_list}", None
        except Exception as e:
            pass
    
    # Default response - provide more helpful fallback
    return ("Saya menerima pesan Anda, tetapi untuk memberikan respons yang optimal, saya memerlukan agent AI yang aktif. "
            "Saat ini saya hanya dapat membantu dengan:\n\n"
            "🧮 **Kalkulasi** - gunakan kata kunci: hitung, kalkulasi, atau operasi matematika\n"
            "📁 **File Management** - gunakan kata kunci: file, folder, list, daftar, tampilkan\n\n"
            "Untuk akses penuh ke semua fitur, pastikan API keys valid telah dikonfigurasi."), None

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Personal Assistant</h1>
        <p>Asisten AI Pribadi - Siap Membantu Anda</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Pengaturan")
        
        # Model selection
        model_option = st.selectbox(
            "Model AI:",
            ["gemini", "openai"],  # Put gemini first since it's default and working
            index=0 if st.session_state.current_model == "gemini" else 1,
            help="Pilih model AI yang ingin digunakan"
        )
        
        # Persona selection
        persona_option = st.selectbox(
            "Persona:",
            ["personal", "research", "technical"],
            index=["personal", "research", "technical"].index(st.session_state.current_persona),
            format_func=lambda x: {
                "personal": "Personal Assistant",
                "research": "Research Assistant", 
                "technical": "Technical Assistant"
            }[x],
            help="Pilih kepribadian asisten AI"
        )
        
        # Update settings if changed
        if model_option != st.session_state.current_model or persona_option != st.session_state.current_persona:
            st.session_state.current_model = model_option
            st.session_state.current_persona = persona_option
            st.session_state.agent = None  # Reset agent
        
        st.markdown("---")
        
        # Agent status
        st.subheader("📊 Status Agent")
        
        # Check API keys with better validation
        api_keys_available = False
        api_key_status = ""
        
        # Use the improved validation from settings
        if settings.is_api_key_valid(model_option):
            api_keys_available = True
            api_key_status = f"✅ {model_option.title()} API Key valid"
        else:
            if model_option == "openai":
                if settings.OPENAI_API_KEY:
                    if "dummy" in settings.OPENAI_API_KEY.lower() or "test" in settings.OPENAI_API_KEY.lower():
                        api_key_status = "⚠️ OpenAI API Key terdeteksi sebagai dummy/test key"
                    else:
                        api_key_status = "⚠️ OpenAI API Key format tidak valid"
                else:
                    api_key_status = "❌ OpenAI API Key tidak ditemukan"
            elif model_option == "gemini":
                if settings.GOOGLE_API_KEY:
                    if "dummy" in settings.GOOGLE_API_KEY.lower() or "test" in settings.GOOGLE_API_KEY.lower():
                        api_key_status = "⚠️ Google API Key terdeteksi sebagai dummy/test key"
                    else:
                        api_key_status = "⚠️ Google API Key format tidak valid"
                else:
                    api_key_status = "❌ Google API Key tidak ditemukan"
        
        # Display API key status
        if api_keys_available:
            st.success(api_key_status)
        else:
            st.warning(api_key_status)
            st.info("Mode fallback: Hanya kalkulasi dan file manager")
        
        # Debug information (can be removed in production)
        with st.expander("🔍 Debug Info"):
            st.write(f"Model: {model_option}")
            st.write(f"OpenAI Key: {'✓' if settings.OPENAI_API_KEY else '✗'} ({settings.OPENAI_API_KEY[:10] + '...' if settings.OPENAI_API_KEY else 'None'})")
            st.write(f"Google Key: {'✓' if settings.GOOGLE_API_KEY else '✗'} ({settings.GOOGLE_API_KEY[:10] + '...' if settings.GOOGLE_API_KEY else 'None'})")
            st.write(f"API Keys Available: {api_keys_available}")
            st.write(f"Agent Status: {'✓ Initialized' if st.session_state.agent is not None else '✗ Not Initialized'}")
            
            # More detailed key validation info
            st.write(f"OpenAI Key Valid: {settings.is_api_key_valid('openai')}")
            st.write(f"Gemini Key Valid: {settings.is_api_key_valid('gemini')}")
            st.write(f"Current Model Valid: {settings.is_api_key_valid(model_option)}")
            
            # Show agent type if available
            if st.session_state.agent is not None:
                agent_type = type(st.session_state.agent).__name__
                st.write(f"Agent Type: {agent_type}")
            
            # Error Summary
            st.markdown("**📊 Error Summary (Today):**")
            try:
                error_summary = agent_logger.create_error_summary()
                if error_summary["total_errors"] > 0:
                    st.error(f"🚨 {error_summary['total_errors']} errors today")
                    st.json(error_summary["error_types"])
                else:
                    st.success("✅ No errors today")
            except Exception as e:
                st.warning(f"Could not load error summary: {e}")
            
            # Test button to force agent initialization
            if st.button("🔄 Force Reinitialize Agent"):
                st.session_state.agent = None
                try:
                    agent, error = create_agent_sync(st.session_state.current_model, st.session_state.current_persona)
                    if agent:
                        st.session_state.agent = agent
                        st.success("Agent berhasil diinisialisasi!")
                    else:
                        st.error(f"Gagal: {error}")
                except Exception as e:
                    st.error(f"Error: {e}")
                    log_error(e, {"action": "force_reinitialize"}, "streamlit_app")
        
        st.metric("Jumlah Pesan", len(st.session_state.messages))
        st.metric("Model Aktif", model_option.upper())
        st.metric("Persona", persona_option.title())
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("🚀 Aksi Cepat")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧮 Kalkulasi", help="Contoh kalkulasi"):
                st.session_state.quick_message = "Hitung 25 * 15 + 100"
        
        with col2:
            if st.button("📁 List File", help="Tampilkan file"):
                st.session_state.quick_message = "Tampilkan daftar file dalam folder ini"
        
        if st.button("🗑️ Hapus Riwayat", help="Hapus semua pesan"):
            st.session_state.messages = st.session_state.messages[:1]  # Keep welcome message
            st.rerun()
        
        if st.button("💾 Export Chat", help="Download riwayat chat"):
            chat_data = {
                "export_date": datetime.now().isoformat(),
                "model": st.session_state.current_model,
                "persona": st.session_state.current_persona,
                "messages": st.session_state.messages
            }
            
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(chat_data, indent=2, ensure_ascii=False),
                file_name=f"ai-chat-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Percakapan")
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                display_chat_message(message)
        
        # Message input
        with st.form("message_form", clear_on_submit=True):
            col_input, col_send = st.columns([4, 1])
            
            with col_input:
                user_input = st.text_input(
                    "Pesan Anda:",
                    placeholder="Ketik pesan Anda di sini...",
                    key="user_input",
                    value=st.session_state.get('quick_message', '')
                )
                
                # Clear quick message after use
                if 'quick_message' in st.session_state:
                    del st.session_state.quick_message
            
            with col_send:
                send_button = st.form_submit_button("📤 Kirim", use_container_width=True)
        
        # Process message
        if send_button and user_input:
            # Add user message
            user_message = {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.messages.append(user_message)
            
            # Show processing indicator
            with st.spinner("🤖 Agent sedang memproses..."):
                # Initialize agent if needed (try even if API keys are not validated)
                if st.session_state.agent is None:
                    with st.spinner("🤖 Menginisialisasi agent..."):
                        try:
                            st.info(f"Mencoba membuat agent dengan model: {st.session_state.current_model}")
                            agent, error = create_agent_sync(st.session_state.current_model, st.session_state.current_persona)
                            if agent:
                                st.session_state.agent = agent
                                st.success(f"✅ Agent berhasil diinisialisasi dengan model {st.session_state.current_model}")
                            else:
                                if api_keys_available:
                                    st.error(f"❌ Gagal menginisialisasi agent: {error}")
                                else:
                                    st.warning(f"⚠️ Agent tidak dapat diinisialisasi (API key tidak valid): {error}")
                        except Exception as e:
                            st.error(f"❌ Exception saat inisialisasi agent: {str(e)}")
                            if api_keys_available:
                                st.error(f"❌ Error initializing agent: {e}")
                            else:
                                st.info(f"⚠️ Agent initialization failed (expected without valid API keys): {e}")
                
                # Debug: Show agent status before processing
                if st.session_state.agent:
                    st.info(f"🎯 Agent tersedia: {type(st.session_state.agent).__name__}")
                else:
                    st.warning("⚠️ Agent tidak tersedia, akan menggunakan fallback tools")
                
                # Process message - prioritize agent if available
                response, error = run_async_function(
                    process_message_async(st.session_state.agent, user_input)
                )
                
                if response:
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.messages.append(assistant_message)
                else:
                    error_message = {
                        "role": "assistant",
                        "content": f"❌ Maaf, terjadi kesalahan: {error}",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.messages.append(error_message)
            
            # Rerun to show new messages
            st.rerun()
    
    with col2:
        st.subheader("ℹ️ Informasi")
        
        st.info("""
        **Fitur yang tersedia:**
        
        🧮 **Kalkulasi**
        - Aritmatika dasar
        - Fungsi matematika
        - Contoh: "Hitung 2+2*5"
        
        📁 **File Manager**
        - List file dan folder
        - Operasi file dasar
        
        🌐 **Web Search** (dengan API)
        - Pencarian informasi
        - Ekstraksi konten web
        
        🌤️ **Cuaca** (dengan API)
        - Informasi cuaca terkini
        - Prakiraan cuaca
        
        💾 **Memory**
        - Riwayat percakapan
        - Preferensi pengguna
        """)
        
        if not api_keys_available:
            st.warning("""
            ⚠️ **Mode Terbatas**
            
            Untuk mengakses semua fitur, 
            tambahkan API keys yang valid di file `.env`:
            
            **Untuk OpenAI:**
            ```
            OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx
            ```
            Dapatkan di: https://platform.openai.com/api-keys
            
            **Untuk Google Gemini:**
            ```
            GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxx
            ```
            Dapatkan di: https://aistudio.google.com/app/apikey
            
            **Untuk Weather API:**
            ```
            WEATHER_API_KEY=xxxxxxxxxxxxxxxxxx
            ```
            Dapatkan di: https://openweathermap.org/api
            
            ⚠️ **Catatan:** API keys yang ada saat ini terdeteksi sebagai dummy/test keys.
            """)

if __name__ == "__main__":
    main()
