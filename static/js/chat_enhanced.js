// 聊天增强功能JavaScript
// 确保在正确的上下文中运行
(function() {
    'use strict';
    
    let socket = null;
    let roomId = null;
    let currentUser = null;
    let participants = {};
    let mediaRecorder = null;
    let audioChunks = [];
    let recordingTimer = null;
    let recordingStartTime = null;

// 表情数据
const emojiData = {
    smileys: ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗', '🤔', '🤭', '🤫', '🤥', '😶', '😐', '😑', '😯', '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐', '🥴', '🤢', '🤮', '🤧', '😷', '🤒', '🤕'],
    animals: ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐸', '🐵', '🐔', '🐧', '🐦', '🐤', '🐣', '🦆', '🦅', '🦉', '🦇', '🐺', '🐗', '🐴', '🦄', '🐝', '🐛', '🦋', '🐌', '🐞', '🐜', '🦟', '🦗', '🕷️', '🕸️', '🦂', '🐢', '🐍', '🦎', '🦖', '🦕', '🐙', '🦑', '🦐', '🦞', '🦀', '🐡', '🐠', '🐟', '🐬', '🐳', '🐋', '🦈', '🐊', '🐅', '🐆', '🦓', '🦍', '🐘', '🦛', '🦏', '🐪', '🐫', '🦙', '🦒', '🐃', '🐂', '🐄', '🐎', '🐖', '🐏', '🐑', '🐐', '🦌', '🐕', '🐩', '🦮', '🐕‍🦺', '🐈', '🐈‍⬛', '🐓', '🦃', '🦚', '🦜', '🦢', '🦩', '🕊️', '🐇', '🦝', '🦨', '🦡', '🦫', '🦦', '🦥', '🐁', '🐀', '🐿️', '🦔'],
    food: ['🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🥑', '🥦', '🥬', '🥒', '🌶️', '🫑', '🌽', '🥕', '🫒', '🧄', '🧅', '🥔', '🍠', '🥐', '🥯', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳', '🧈', '🥞', '🧇', '🥓', '🥩', '🍗', '🍖', '🦴', '🌭', '🍔', '🍟', '🍕', '🥪', '🥙', '🧆', '🌮', '🌯', '🫔', '🥗', '🥘', '🫕', '🥫', '🍝', '🍜', '🍲', '🍛', '🍣', '🍱', '🥟', '🦪', '🍤', '🍙', '🍚', '🍘', '🍥', '🥠', '🥮', '🍢', '🍡', '🍧', '🍨', '🍦', '🥧', '🧁', '🍰', '🎂', '🍮', '🍭', '🍬', '🍫', '🍿', '🍪', '🌰', '🥜', '🍯', '🥛', '🍼', '🫖', '☕', '🍵', '🧃', '🥤', '🧋', '🍶', '🍺', '🍻', '🥂', '🍷', '🥃', '🍸', '🍹', '🧉', '🍾', '🧊', '🥄', '🍴', '🍽️', '🥄', '🥡', '🥢', '🧂'],
    activities: ['⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🥅', '⛳', '🪁', '🏹', '🎣', '🤿', '🥊', '🥋', '🎽', '🛹', '🛷', '⛸️', '🥌', '🎿', '⛷️', '🏂', '🏋️‍♀️', '🏋️', '🏋️‍♂️', '🤼‍♀️', '🤼', '🤼‍♂️', '🤸‍♀️', '🤸', '🤸‍♂️', '⛹️‍♀️', '⛹️', '⛹️‍♂️', '🤺', '🤾‍♀️', '🤾', '🤾‍♂️', '🏊‍♀️', '🏊', '🏊‍♂️', '🤽‍♀️', '🤽', '🤽‍♂️', '🚣‍♀️', '🚣', '🚣‍♂️', '🧗‍♀️', '🧗', '🧗‍♂️', '🚵‍♀️', '🚵', '🚵‍♂️', '🚴‍♀️', '🚴', '🚴‍♂️', '🏆', '🥇', '🥈', '🥉', '🏅', '🎖️', '🏵️', '🎗️', '🎫', '🎟️', '🎪', '🤹‍♀️', '🤹', '🤹‍♂️', '🎭', '🩰', '🎨', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🪘', '🎷', '🎺', '🎸', '🪕', '🎻', '🎲', '♟️', '🎯', '🎳', '🎮', '🎰', '🧩', '🎨', '📱', '📲', '💻', '⌨️', '🖥️', '🖨️', '🖱️', '🖲️', '💽', '💾', '💿', '📀', '🧮', '🎥', '📹', '📼', '📷', '📸', '📹', '📺', '📻', '🎙️', '🎚️', '🎛️', '🧭', '⏱️', '⏲️', '⏰', '🕰️', '⌛', '⏳', '📡', '🔋', '🔌', '💡', '🔦', '🕯️', '🪔', '🧯', '🛢️', '💸', '💵', '💴', '💶', '💷', '🪙', '💰', '💳', '💎', '⚖️', '🪜', '🧰', '🪛', '🔧', '🔨', '⚒️', '🛠️', '⛏️', '🪚', '🔩', '⚙️', '🪤', '🧱', '⛓️', '🧲', '🔫', '💣', '🪃', '🏹', '🪄', '🔮', '🧿', '🪬', '📿', '🧸', '🪆', '🪅', '🪩', '🪩', '🎊', '🎉', '🎈', '🎂', '🎁', '🎀', '🎗️', '🎟️', '🎫', '🎠', '🎡', '🎢', '🎪', '🎭', '🎨', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🪘', '🎷', '🎺', '🎸', '🪕', '🎻', '🎲', '♟️', '🎯', '🎳', '🎮', '🎰', '🧩'],
    objects: ['💡', '🔦', '🕯️', '🪔', '🧯', '🛢️', '💸', '💵', '💴', '💶', '💷', '🪙', '💰', '💳', '💎', '⚖️', '🪜', '🧰', '🪛', '🔧', '🔨', '⚒️', '🛠️', '⛏️', '🪚', '🔩', '⚙️', '🪤', '🧱', '⛓️', '🧲', '🔫', '💣', '🪃', '🏹', '🪄', '🔮', '🧿', '🪬', '📿', '🧸', '🪆', '🪅', '🪩', '🪩', '🎊', '🎉', '🎈', '🎂', '🎁', '🎀', '🎗️', '🎟️', '🎫', '🎠', '🎡', '🎢', '🎪', '🎭', '🎨', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🪘', '🎷', '🎺', '🎸', '🪕', '🎻', '🎲', '♟️', '🎯', '🎳', '🎮', '🎰', '🧩', '📱', '📲', '💻', '⌨️', '🖥️', '🖨️', '🖱️', '🖲️', '💽', '💾', '💿', '📀', '🧮', '🎥', '📹', '📼', '📷', '📸', '📹', '📺', '📻', '🎙️', '🎚️', '🎛️', '🧭', '⏱️', '⏲️', '⏰', '🕰️', '⌛', '⏳', '📡', '🔋', '🔌', '💡', '🔦', '🕯️', '🪔', '🧯', '🛢️', '💸', '💵', '💴', '💶', '💷', '🪙', '💰', '💳', '💎', '⚖️', '🪜', '🧰', '🪛', '🔧', '🔨', '⚒️', '🛠️', '⛏️', '🪚', '🔩', '⚙️', '🪤', '🧱', '⛓️', '🧲', '🔫', '💣', '🪃', '🏹', '🪄', '🔮', '🧿', '🪬', '📿', '🧸', '🪆', '🪅', '🪩', '🪩', '🎊', '🎉', '🎈', '🎂', '🎁', '🎀', '🎗️', '🎟️', '🎫', '🎠', '🎡', '🎢', '🎪', '🎭', '🎨', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🪘', '🎷', '🎺', '🎸', '🪕', '🎻', '🎲', '♟️', '🎯', '🎳', '🎮', '🎰', '🧩'],
    symbols: ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓', '🆔', '⚛️', '🉑', '☢️', '☣️', '📴', '📳', '🈶', '🈚', '🈸', '🈺', '🈷️', '✴️', '🆚', '💮', '🉐', '㊙️', '㊗️', '🈴', '🈵', '🈹', '🈲', '🅰️', '🅱️', '🆎', '🆑', '🅾️', '🆘', '❌', '⭕', '🛑', '⛔', '📛', '🚫', '💯', '💢', '♨️', '🚷', '🚯', '🚳', '🚱', '🔞', '📵', '🚭', '❗', '❕', '❓', '❔', '‼️', '⁉️', '🔅', '🔆', '〽️', '⚠️', '🚸', '🔱', '⚜️', '🔰', '♻️', '✅', '🈯', '💹', '❇️', '✳️', '❎', '🌐', '💠', 'Ⓜ️', '🌀', '💤', '🏧', '🚾', '♿', '🅿️', '🛗', '🛂', '🛃', '🛄', '🛅', '🚹', '🚺', '🚼', '🚻', '🚮', '🎦', '📶', '🈁', '🔣', 'ℹ️', '🔤', '🔡', '🔠', '🆖', '🆗', '🆙', '🆒', '🆕', '🆓', '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '🔢', '#️⃣', '*️⃣', '⏏️', '▶️', '⏸️', '⏯️', '⏹️', '⏺️', '⏭️', '⏮️', '⏩', '⏪', '⏫', '⏬', '◀️', '🔼', '🔽', '➡️', '⬅️', '⬆️', '⬇️', '↗️', '↘️', '↙️', '↖️', '↕️', '↔️', '↪️', '↩️', '⤴️', '⤵️', '🔀', '🔁', '🔂', '🔄', '🔃', '🎵', '🎶', '➕', '➖', '➗', '✖️', '♾️', '💲', '💱', '™️', '©️', '®️', '👁️‍🗨️', '🔚', '🔙', '🔛', '🔝', '🔜', '〰️', '➰', '➿', '✔️', '☑️', '🔘', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '⚫', '⚪', '🟤', '🔺', '🔻', '🔸', '🔹', '🔶', '🔷', '🔳', '🔲', '▪️', '▫️', '◾', '◽', '◼️', '◻️', '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '⬛', '⬜', '🟫', '🔈', '🔇', '🔉', '🔊', '🔔', '🔕', '📣', '📢', '💬', '💭', '🗯️', '♠️', '♣️', '♥️', '♦️', '🃏', '🎴', '🀄', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛', '🕜', '🕝', '🕞', '🕟', '🕠', '🕡', '🕢', '🕣', '🕤', '🕥', '🕦', '🕧']
};

// 初始化聊天功能
function initChat() {
    roomId = document.querySelector('[data-room-id]')?.dataset.roomId || 'test-room-' + Date.now();
    connectWebSocket();
    initEmojiPanel();
    initToolButtons();
    loadParticipants();
}

// 连接WebSocket
function connectWebSocket() {
    const wsUrl = `ws://${window.location.host}/ws/chat/${roomId}/`;
    
    updateConnectionStatus('connecting', '连接中...');
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = function(event) {
        updateConnectionStatus('connected', '已连接');
        console.log('WebSocket连接成功');
    };
    
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    socket.onclose = function(event) {
        updateConnectionStatus('disconnected', '连接已断开');
        console.log('WebSocket连接已关闭');
        
        // 显示重连选项
        showReconnectOptions();
    };
    
    socket.onerror = function(error) {
        updateConnectionStatus('disconnected', '连接错误');
        console.error('WebSocket错误:', error);
    };
}

// 显示重连选项
function showReconnectOptions() {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.innerHTML = `
            <div class="reconnect-options">
                <span><i class="fas fa-wifi"></i> 连接已断开</span>
                <div class="reconnect-buttons">
                    <button class="reconnect-btn" onclick="reconnectWebSocket()">
                        <i class="fas fa-redo"></i> 重新连接
                    </button>
                    <button class="refresh-btn" onclick="refreshPage()">
                        <i class="fas fa-sync"></i> 刷新页面
                    </button>
                </div>
            </div>
        `;
    }
}

// 重新连接WebSocket
function reconnectWebSocket() {
    updateConnectionStatus('connecting', '重新连接中...');
    
    setTimeout(() => {
        if (socket.readyState === WebSocket.CLOSED) {
            connectWebSocket();
        }
    }, 1000);
}

// 刷新页面
function refreshPage() {
    window.location.reload();
}

// 更新连接状态
function updateConnectionStatus(status, message) {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.className = `connection-status ${status}`;
        statusElement.innerHTML = `<i class="fas fa-wifi"></i> ${message}`;
    }
}

// 处理WebSocket消息
function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'connection_established':
            handleConnectionEstablished(data);
            break;
        case 'chat_message':
            handleChatMessage(data.message);
            break;
        case 'user_joined':
            handleUserJoined(data);
            break;
        case 'user_left':
            handleUserLeft(data);
            break;
        case 'user_typing':
            handleUserTyping(data);
            break;
        case 'read_status_update':
            handleReadStatusUpdate(data);
            break;
    }
}

// 处理连接建立
function handleConnectionEstablished(data) {
    currentUser = data.user;
    if (data.user_profile) {
        participants[data.user] = data.user_profile;
        updateParticipantsList();
    }
    addSystemMessage(`${data.user} 已连接到聊天室`);
}

// 处理聊天消息
function handleChatMessage(message) {
    addMessage(message);
}

// 处理用户加入
function handleUserJoined(data) {
    if (data.user_profile) {
        participants[data.username] = data.user_profile;
        updateParticipantsList();
    }
    addSystemMessage(`${data.username} 加入了聊天室`);
}

// 处理用户离开
function handleUserLeft(data) {
    if (participants[data.username]) {
        participants[data.username].is_online = false;
        updateParticipantsList();
    }
    addSystemMessage(`${data.username} 离开了聊天室`);
}

// 处理用户输入状态
function handleUserTyping(data) {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        if (data.is_typing) {
            typingIndicator.textContent = `${data.username} 正在输入...`;
            typingIndicator.style.display = 'block';
        } else {
            typingIndicator.style.display = 'none';
        }
    }
}

// 处理已读状态更新
function handleReadStatusUpdate(data) {
    console.log('消息已读状态更新:', data);
}

// 添加消息到聊天区域
function addMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.is_own ? 'own' : ''}`;
    
    const avatar = participants[message.sender]?.avatar_url || '/static/img/default-avatar.svg';
    const displayName = participants[message.sender]?.display_name || message.sender;
    
    let messageContent = '';
    
    // 根据消息类型生成不同的内容
    switch(message.message_type) {
        case 'image':
            messageContent = `<img src="${message.content}" alt="图片" class="message-image" onclick="openImageModal('${message.content}')">`;
            break;
        case 'video':
            messageContent = `<video src="${message.content}" controls class="message-video"></video>`;
            break;
        case 'audio':
            messageContent = `
                <div class="message-audio">
                    <button class="audio-play-button" onclick="playAudio('${message.content}')">
                        <i class="fas fa-play"></i>
                    </button>
                    <span>语音消息</span>
                </div>`;
            break;
        case 'file':
            messageContent = `
                <div class="message-file">
                    <div class="file-icon">
                        <i class="fas fa-file"></i>
                    </div>
                    <div class="file-info">
                        <div class="file-name">${message.file_name || '文件'}</div>
                        <div class="file-size">${message.file_size || ''}</div>
                    </div>
                    <button onclick="downloadFile('${message.content}', '${message.file_name}')">
                        <i class="fas fa-download"></i>
                    </button>
                </div>`;
            break;
        default:
            messageContent = `<div class="message-text">${escapeHtml(message.content)}</div>`;
    }
    
    messageDiv.innerHTML = `
        <img src="${avatar}" alt="${displayName}" class="message-avatar">
        <div class="message-content">
            <div class="message-header">
                <span class="message-sender">${displayName}</span>
                <span class="message-time">${formatTime(message.created_at)}</span>
            </div>
            ${messageContent}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 添加系统消息
function addSystemMessage(text) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.innerHTML = `
        <div class="message-content" style="background: #f8f9fa; color: #666; text-align: center; font-style: italic;">
            ${escapeHtml(text)}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 更新参与者列表
function updateParticipantsList() {
    const participantsList = document.getElementById('participantsList');
    if (!participantsList) return;
    
    participantsList.innerHTML = '';
    
    Object.values(participants).forEach(participant => {
        const participantCard = document.createElement('div');
        participantCard.className = `participant-card ${participant.is_online ? 'online' : ''}`;
        
        const avatar = participant.avatar_url || '/static/img/default-avatar.svg';
        
        participantCard.innerHTML = `
            <div class="participant-header">
                <img src="${avatar}" alt="${participant.display_name}" class="participant-avatar">
                <div class="participant-info">
                    <div class="participant-name">${escapeHtml(participant.display_name)}</div>
                    <div class="participant-status">
                        <div class="status-indicator ${participant.is_online ? 'online' : 'offline'}"></div>
                        ${participant.is_online ? '在线' : '离线'}
                    </div>
                </div>
            </div>
            <div class="participant-details">
                ${participant.bio ? `<div class="participant-bio">${escapeHtml(participant.bio)}</div>` : ''}
                <div class="participant-membership">${escapeHtml(participant.membership_type)}</div>
                <div class="participant-tags">
                    ${participant.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            </div>
        `;
        
        participantsList.appendChild(participantCard);
    });
}

// 发送消息
function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message || !socket || socket.readyState !== WebSocket.OPEN) {
        return;
    }
    
    const data = {
        type: 'message',
        content: message,
        message_type: 'text'
    };
    
    socket.send(JSON.stringify(data));
    input.value = '';
}

// 发送文件消息
function sendFileMessage(file, messageType) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        alert('连接已断开，无法发送文件');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('message_type', messageType);
    
    fetch(`/tools/api/chat/${roomId}/send-${messageType}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 文件上传成功，消息会通过WebSocket接收
            console.log('文件发送成功');
        } else {
            alert('文件发送失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('发送文件错误:', error);
        alert('发送文件失败');
    });
}

// 初始化表情面板
function initEmojiPanel() {
    const emojiPanel = document.getElementById('emojiPanel');
    const emojiList = document.getElementById('emojiList');
    const emojiButton = document.getElementById('emojiButton');
    
    if (!emojiPanel || !emojiList || !emojiButton) return;
    
    // 加载默认表情
    loadEmojis('smileys');
    
    // 表情按钮点击事件
    emojiButton.addEventListener('click', function() {
        emojiPanel.style.display = emojiPanel.style.display === 'none' ? 'block' : 'none';
    });
    
    // 表情分类点击事件
    document.querySelectorAll('.emoji-category').forEach(button => {
        button.addEventListener('click', function() {
            const category = this.dataset.category;
            
            // 更新活跃状态
            document.querySelectorAll('.emoji-category').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // 加载对应分类的表情
            loadEmojis(category);
        });
    });
    
    // 点击外部关闭表情面板
    document.addEventListener('click', function(event) {
        if (!emojiPanel.contains(event.target) && !emojiButton.contains(event.target)) {
            emojiPanel.style.display = 'none';
        }
    });
}

// 加载表情
function loadEmojis(category) {
    const emojiList = document.getElementById('emojiList');
    if (!emojiList) return;
    
    const emojis = emojiData[category] || emojiData.smileys;
    
    emojiList.innerHTML = emojis.map(emoji => `
        <button class="emoji-item" onclick="insertEmoji('${emoji}')">${emoji}</button>
    `).join('');
}

// 插入表情
function insertEmoji(emoji) {
    const input = document.getElementById('messageInput');
    const cursorPos = input.selectionStart;
    const textBefore = input.value.substring(0, cursorPos);
    const textAfter = input.value.substring(cursorPos);
    
    input.value = textBefore + emoji + textAfter;
    input.focus();
    input.setSelectionRange(cursorPos + emoji.length, cursorPos + emoji.length);
    
    // 关闭表情面板
    document.getElementById('emojiPanel').style.display = 'none';
}

// 初始化工具按钮
function initToolButtons() {
    // 图片按钮
    const imageButton = document.getElementById('imageButton');
    const imageInput = document.getElementById('imageInput');
    
    if (imageButton && imageInput) {
        imageButton.addEventListener('click', () => imageInput.click());
        imageInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                sendFileMessage(this.files[0], 'image');
            }
        });
    }
    
    // 文件按钮
    const fileButton = document.getElementById('fileButton');
    const fileInput = document.getElementById('fileInput');
    
    if (fileButton && fileInput) {
        fileButton.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                sendFileMessage(this.files[0], 'file');
            }
        });
    }
    
    // 视频按钮
    const videoButton = document.getElementById('videoButton');
    const videoInput = document.getElementById('videoInput');
    
    if (videoButton && videoInput) {
        videoButton.addEventListener('click', () => videoInput.click());
        videoInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                sendFileMessage(this.files[0], 'video');
            }
        });
    }
    
    // 语音按钮
    const voiceButton = document.getElementById('voiceButton');
    if (voiceButton) {
        voiceButton.addEventListener('click', startVoiceRecording);
    }
    
    // 发送按钮
    const sendButton = document.getElementById('sendButton');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    // 输入框事件
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // 输入状态
        let typingTimeout;
        messageInput.addEventListener('input', function() {
            sendTypingStatus(true);
            
            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(() => {
                sendTypingStatus(false);
            }, 1000);
        });
    }
}

// 发送输入状态
function sendTypingStatus(isTyping) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'typing',
            is_typing: isTyping
        }));
    }
}

// 开始语音录制
function startVoiceRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('您的浏览器不支持语音录制');
        return;
    }
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = function(event) {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = function() {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendFileMessage(audioBlob, 'audio');
                
                // 停止所有轨道
                stream.getTracks().forEach(track => track.stop());
                
                // 隐藏录制器
                document.getElementById('voiceRecorder').classList.remove('recording');
                clearInterval(recordingTimer);
            };
            
            // 开始录制
            mediaRecorder.start();
            recordingStartTime = Date.now();
            
            // 显示录制器
            const recorder = document.getElementById('voiceRecorder');
            recorder.classList.add('recording');
            
            // 开始计时
            recordingTimer = setInterval(updateRecordingTime, 1000);
            
            // 停止录制按钮
            document.getElementById('stopRecording').onclick = () => {
                mediaRecorder.stop();
            };
            
            // 取消录制按钮
            document.getElementById('cancelRecording').onclick = () => {
                mediaRecorder.stop();
                stream.getTracks().forEach(track => track.stop());
                recorder.classList.remove('recording');
                clearInterval(recordingTimer);
            };
        })
        .catch(error => {
            console.error('获取麦克风权限失败:', error);
            alert('无法访问麦克风，请检查权限设置');
        });
}

// 更新录制时间
function updateRecordingTime() {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    const timeElement = document.getElementById('recordingTime');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

// 播放音频
function playAudio(audioUrl) {
    const audio = new Audio(audioUrl);
    audio.play().catch(error => {
        console.error('播放音频失败:', error);
        alert('播放音频失败');
    });
}

// 下载文件
function downloadFile(fileUrl, fileName) {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = fileName || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 打开图片模态框
function openImageModal(imageUrl) {
    // 创建模态框
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 3000;
        cursor: pointer;
    `;
    
    const img = document.createElement('img');
    img.src = imageUrl;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
    `;
    
    modal.appendChild(img);
    document.body.appendChild(modal);
    
    // 点击关闭
    modal.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
}

// 加载参与者信息
async function loadParticipants() {
    try {
        const response = await fetch(`/tools/api/chat/${roomId}/participants/`);
        const data = await response.json();
        
        if (data.success) {
            data.data.participants.forEach(participant => {
                participants[participant.username] = participant;
            });
            updateParticipantsList();
        }
    } catch (error) {
        console.error('加载参与者信息失败:', error);
    }
}

// 工具函数
function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initChat();
});
})();
