// 获取留言列表
async function fetchMessages() {
    try {
        const response = await fetch('api/get_messages.php');
        const data = await response.json();
        
        if (data.success) {
            return data.messages;
        } else {
            console.error('Error fetching messages:', data.error);
            return [];
        }
    } catch (error) {
        console.error('Error:', error);
        return [];
    }
}

// 渲染留言列表
function renderMessages(messages) {
    const messagesList = document.getElementById('messagesList');
    messagesList.innerHTML = messages.map(message => `
        <div class="message-item">
            <div class="message-avatar">
                <img src="${message.avatar}" alt="${message.name}的头像">
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-name">${message.name}</span>
                    <span class="message-time">${new Date(message.created_at).toLocaleString()}</span>
                </div>
                <div class="message-text">${message.message}</div>
            </div>
        </div>
    `).join('');
}

// 添加新留言
async function addMessage(event) {
    event.preventDefault();
    
    const nameInput = document.getElementById('name');
    const messageInput = document.getElementById('message');
    
    const messageData = {
        name: nameInput.value,
        message: messageInput.value
    };
    
    try {
        const response = await fetch('api/add_message.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(messageData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 重新获取并显示留言列表
            const messages = await fetchMessages();
            renderMessages(messages);
            
            // 清空表单
            nameInput.value = '';
            messageInput.value = '';
        } else {
            alert('发送留言失败：' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('发送留言失败，请稍后重试');
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', async () => {
    // 获取并显示留言列表
    const messages = await fetchMessages();
    renderMessages(messages);
    
    // 绑定表单提交事件
    const messageForm = document.getElementById('messageForm');
    messageForm.addEventListener('submit', addMessage);
}); 