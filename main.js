// 对话页面JavaScript

let isLoading = false;

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    loadChatHistory();
    setupEventListeners();
    adjustTextareaHeight();
});

// 设置事件监听器
function setupEventListeners() {
    // 发送消息
    document.getElementById('chatForm').addEventListener('submit', handleSendMessage);
    
    // 文本框自动调整高度
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('input', adjustTextareaHeight);
    
    // Enter发送，Shift+Enter换行
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            document.getElementById('chatForm').dispatchEvent(new Event('submit'));
        }
    });
    
    // 退出登录
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    
    // 清空历史
    document.getElementById('clearHistoryBtn').addEventListener('click', handleClearHistory);
}

// 自动调整文本框高度
function adjustTextareaHeight() {
    const textarea = document.getElementById('messageInput');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// 加载对话历史
async function loadChatHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.success && data.history.length > 0) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = ''; // 清空欢迎消息
            
            data.history.forEach(item => {
                appendMessage('user', item.user, item.timestamp);
                appendMessage('assistant', item.assistant, item.timestamp);
            });
            
            scrollToBottom();
        }
    } catch (error) {
        console.error('加载历史记录失败:', error);
    }
}

// 发送消息
async function handleSendMessage(e) {
    e.preventDefault();
    
    if (isLoading) return;
    
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // 清空输入框
    messageInput.value = '';
    adjustTextareaHeight();
    
    // 移除欢迎消息
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // 显示用户消息
    const timestamp = new Date().toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    appendMessage('user', message, timestamp);
    
    // 显示加载状态
    showTypingIndicator();
    setLoading(true);
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // 移除加载状态
        removeTypingIndicator();
        
        if (data.success) {
            appendMessage('assistant', data.message, timestamp);
        } else {
            appendMessage('assistant', data.message || '抱歉，出现了错误，请稍后重试。', timestamp);
        }
    } catch (error) {
        removeTypingIndicator();
        appendMessage('assistant', '抱歉，网络连接失败，请检查网络后重试。', timestamp);
        console.error('发送消息失败:', error);
    } finally {
        setLoading(false);
    }
}

// 添加消息到聊天区域
function appendMessage(role, content, timestamp) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageWrapper = document.createElement('div');
    messageWrapper.className = `message-wrapper ${role}`;
    
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';
    messageBubble.textContent = content;
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = timestamp;
    
    messageWrapper.appendChild(messageBubble);
    if (role === 'user') {
        messageBubble.appendChild(messageTime);
    } else {
        messageWrapper.appendChild(messageTime);
    }
    
    chatMessages.appendChild(messageWrapper);
    scrollToBottom();
}

// 显示输入中指示器
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message-wrapper assistant';
    typingDiv.id = 'typingIndicator';
    
    const typingBubble = document.createElement('div');
    typingBubble.className = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        typingBubble.appendChild(dot);
    }
    
    typingDiv.appendChild(typingBubble);
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

// 移除输入中指示器
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// 设置加载状态
function setLoading(loading) {
    isLoading = loading;
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = loading;
}

// 滚动到底部
function scrollToBottom() {
    const chatContent = document.querySelector('.chat-content');
    setTimeout(() => {
        chatContent.scrollTop = chatContent.scrollHeight;
    }, 100);
}

// 退出登录
async function handleLogout() {
    if (!confirm('确定要退出登录吗？')) return;
    
    try {
        const response = await fetch('/api/logout', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.location.href = '/login';
        }
    } catch (error) {
        alert('退出登录失败，请重试');
        console.error('退出登录失败:', error);
    }
}

// 清空对话历史
async function handleClearHistory() {
    if (!confirm('确定要清空所有对话历史吗？此操作不可恢复。')) return;
    
    try {
        const response = await fetch('/api/clear_history', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 清空聊天区域并显示欢迎消息
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">👋</div>
                    <h2>您好！我是AI医生助手</h2>
                    <p>我可以帮您了解健康问题，提供初步的健康建议。</p>
                    <p class="disclaimer">⚠️ 提醒：我的建议仅供参考，不能替代专业医生的诊断。如有严重症状，请及时就医。</p>
                </div>
            `;
            alert('对话历史已清空');
        } else {
            alert(data.message || '清空失败，请重试');
        }
    } catch (error) {
        alert('清空失败，请重试');
        console.error('清空历史失败:', error);
    }
}

