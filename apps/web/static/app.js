// JavaScript for AI Personal Assistant Web Interface

class AIAssistantWebApp {
    constructor() {
        this.currentModel = 'openai';
        this.currentPersona = 'personal';
        this.messageCount = 0;
        this.websocket = null;
        this.isConnected = false;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeWebSocket();
        this.updateAgentInfo();
    }
    
    initializeElements() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.modelSelect = document.getElementById('modelSelect');
        this.personaSelect = document.getElementById('personaSelect');
        this.clearMemoryBtn = document.getElementById('clearMemoryBtn');
        this.exportChatBtn = document.getElementById('exportChatBtn');
        this.agentStatus = document.getElementById('agentStatus');
        this.messageCountEl = document.getElementById('messageCount');
        this.currentModelEl = document.getElementById('currentModel');
        this.currentPersonaEl = document.getElementById('currentPersona');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.quickActionBtns = document.querySelectorAll('.quick-action');
    }
    
    bindEvents() {
        // Send message events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Model and persona change events
        this.modelSelect.addEventListener('change', (e) => this.switchModel(e.target.value));
        this.personaSelect.addEventListener('change', (e) => this.switchPersona(e.target.value));
        
        // Action button events
        this.clearMemoryBtn.addEventListener('click', () => this.clearMemory());
        this.exportChatBtn.addEventListener('click', () => this.exportChat());
        
        // Quick action events
        this.quickActionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.target.dataset.message || e.target.closest('.quick-action').dataset.message;
                this.messageInput.value = message;
                this.sendMessage();
            });
        });
    }
    
    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.updateConnectionStatus(true);
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                
                // Try to reconnect after 3 seconds
                setTimeout(() => this.initializeWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
                this.updateConnectionStatus(false);
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            this.fallbackToHTTP();
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'response':
                this.addMessage('assistant', data.message);
                this.hideLoading();
                break;
                
            case 'error':
                this.showError(data.message);
                this.hideLoading();
                break;
                
            case 'pong':
                // Handle ping-pong for connection keep-alive
                break;
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.showLoading();
        
        if (this.isConnected && this.websocket) {
            // Send via WebSocket
            this.websocket.send(JSON.stringify({
                type: 'chat',
                message: message,
                model: this.currentModel,
                persona: this.currentPersona
            }));
        } else {
            // Fallback to HTTP API
            await this.sendMessageHTTP(message);
        }
    }
    
    async sendMessageHTTP(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: this.currentModel,
                    persona: this.currentPersona
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessage('assistant', data.response);
            } else {
                this.showError(data.error || 'Terjadi kesalahan dalam memproses pesan');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Gagal mengirim pesan. Silakan coba lagi.');
        } finally {
            this.hideLoading();
        }
    }
    
    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const icon = role === 'user' ? 'fa-user' : 'fa-robot';
        const timestamp = new Date().toLocaleTimeString('id-ID', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <i class="fas ${icon} message-icon"></i>
                <div class="message-text">
                    ${this.formatMessage(content)}
                    <div class="text-muted small mt-1">${timestamp}</div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Update message count
        this.messageCount++;
        this.messageCountEl.textContent = this.messageCount;
    }
    
    formatMessage(content) {
        // Simple markdown-like formatting
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        content = content.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');
        content = content.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Convert line breaks to HTML
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }
    
    showLoading() {
        this.loadingIndicator.style.display = 'block';
        this.sendButton.disabled = true;
        this.messageInput.disabled = true;
    }
    
    hideLoading() {
        this.loadingIndicator.style.display = 'none';
        this.sendButton.disabled = false;
        this.messageInput.disabled = false;
        this.messageInput.focus();
    }
    
    showError(message) {
        this.addMessage('assistant', `❌ **Error:** ${message}`);
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    async switchModel(model) {
        if (model === this.currentModel) return;
        
        try {
            const response = await fetch('/api/agent/switch-model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model: model })
            });
            
            if (response.ok) {
                this.currentModel = model;
                this.updateCurrentModelDisplay();
                this.addMessage('assistant', `🔄 Model AI berubah ke ${model === 'openai' ? 'OpenAI GPT' : 'Google Gemini'}`);
            }
        } catch (error) {
            console.error('Error switching model:', error);
        }
    }
    
    async switchPersona(persona) {
        if (persona === this.currentPersona) return;
        
        try {
            const response = await fetch('/api/agent/switch-persona', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ persona: persona })
            });
            
            if (response.ok) {
                this.currentPersona = persona;
                this.updateCurrentPersonaDisplay();
                
                const personaNames = {
                    personal: 'Personal Assistant',
                    research: 'Research Assistant', 
                    technical: 'Technical Assistant'
                };
                
                this.addMessage('assistant', `🎭 Persona berubah ke ${personaNames[persona]}`);
            }
        } catch (error) {
            console.error('Error switching persona:', error);
        }
    }
    
    async clearMemory() {
        if (!confirm('Yakin ingin menghapus semua riwayat percakapan?')) return;
        
        try {
            const response = await fetch('/api/memory/clear', { method: 'DELETE' });
            
            if (response.ok) {
                // Clear chat messages (keep only the welcome message)
                const welcomeMessage = this.chatMessages.firstElementChild;
                this.chatMessages.innerHTML = '';
                this.chatMessages.appendChild(welcomeMessage);
                
                this.messageCount = 0;
                this.messageCountEl.textContent = '0';
                
                this.addMessage('assistant', '🗑️ Riwayat percakapan telah dihapus.');
            }
        } catch (error) {
            console.error('Error clearing memory:', error);
            this.showError('Gagal menghapus riwayat percakapan');
        }
    }
    
    exportChat() {
        const messages = Array.from(this.chatMessages.querySelectorAll('.message')).map(msg => {
            const isUser = msg.classList.contains('user-message');
            const content = msg.querySelector('.message-text').textContent.trim();
            const timestamp = content.split('\n').pop(); // Get timestamp from last line
            const text = content.replace(timestamp, '').trim();
            
            return {
                role: isUser ? 'user' : 'assistant',
                content: text,
                timestamp: timestamp
            };
        });
        
        const exportData = {
            export_date: new Date().toISOString(),
            model: this.currentModel,
            persona: this.currentPersona,
            message_count: messages.length,
            messages: messages
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
            type: 'application/json' 
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-chat-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    updateConnectionStatus(connected) {
        if (connected) {
            this.agentStatus.textContent = 'Online';
            this.agentStatus.className = 'badge bg-success';
        } else {
            this.agentStatus.textContent = 'Offline';
            this.agentStatus.className = 'badge bg-danger';
        }
    }
    
    updateCurrentModelDisplay() {
        const modelNames = {
            'openai': 'OpenAI GPT',
            'gemini': 'Google Gemini'
        };
        this.currentModelEl.textContent = modelNames[this.currentModel];
    }
    
    updateCurrentPersonaDisplay() {
        const personaNames = {
            'personal': 'Personal',
            'research': 'Research',
            'technical': 'Technical'
        };
        this.currentPersonaEl.textContent = personaNames[this.currentPersona];
    }
    
    async updateAgentInfo() {
        try {
            const response = await fetch('/api/agent/info');
            const data = await response.json();
            
            this.messageCount = data.memory_status.stm_messages;
            this.messageCountEl.textContent = this.messageCount;
        } catch (error) {
            console.error('Error updating agent info:', error);
        }
    }
    
    fallbackToHTTP() {
        console.log('Using HTTP fallback for communication');
        // All communication will go through HTTP API
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AIAssistantWebApp();
});

// Handle page visibility change to manage WebSocket connection
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, could pause some operations
    } else {
        // Page is visible again, ensure connection is active
    }
});
