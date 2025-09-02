// 增强版聊天功能 - 支持重连机制和消息压缩
class EnhancedChatManager {
    constructor(roomId, options = {}) {
        this.roomId = roomId;
        this.options = {
            heartbeatInterval: 30000, // 30秒心跳
            reconnectDelay: 1000,     // 1秒重连延迟
            maxReconnectDelay: 30000, // 最大30秒重连延迟
            maxReconnectAttempts: 10, // 最大重连次数
            enableCompression: true,  // 启用消息压缩
            compressionThreshold: 1024, // 1KB以上压缩
            ...options
        };
        
        this.socket = null;
        this.reconnectAttempts = 0;
        this.lastReconnectTime = 0;
        this.heartbeatTimer = null;
        this.reconnectTimer = null;
        this.messageQueue = [];
        this.sentMessages = new Map();
        this.receivedMessages = new Set();
        this.isOnline = navigator.onLine;
        this.connectionState = 'disconnected';
        
        // 事件回调
        this.onMessage = options.onMessage || (() => {});
        this.onStateChange = options.onStateChange || (() => {});
        this.onUserJoined = options.onUserJoined || (() => {});
        this.onUserLeft = options.onUserLeft || (() => {});
        this.onTyping = options.onTyping || (() => {});
        this.onReadStatus = options.onReadStatus || (() => {});
        
        // 初始化
        this.init();
    }
    
    init() {
        // 监听网络状态变化
        window.addEventListener('online', () => this.handleNetworkChange(true));
        window.addEventListener('offline', () => this.handleNetworkChange(false));
        
        // 页面可见性变化处理
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.checkConnection();
            }
        });
        
        // 连接WebSocket
        this.connect();
    }
    
    connect() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }
        
        this.updateState('connecting');
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.roomId}/`;
        
        try {
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = (event) => {

                this.updateState('connected');
                this.reconnectAttempts = 0;
                this.startHeartbeat();
                this.sendQueuedMessages();
            };
            
            this.socket.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.socket.onclose = (event) => {

                this.updateState('disconnected');
                this.stopHeartbeat();
                
                // 如果不是正常关闭，尝试重连
                if (event.code !== 1000 && this.reconnectAttempts < this.options.maxReconnectAttempts) {
                    this.scheduleReconnect();
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket错误:', error);
                this.updateState('error');
            };
            
        } catch (error) {
            console.error('创建WebSocket失败:', error);
            this.updateState('error');
            this.scheduleReconnect();
        }
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.close(1000, '用户主动断开');
            this.socket = null;
        }
        this.stopHeartbeat();
        this.updateState('disconnected');
    }
    
    scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        
        const delay = Math.min(
            this.options.reconnectDelay * Math.pow(2, this.reconnectAttempts),
            this.options.maxReconnectDelay
        );
        
        this.reconnectTimer = setTimeout(() => {
            this.reconnectAttempts++;

            this.connect();
        }, delay);
    }
    
    startHeartbeat() {
        this.stopHeartbeat();
        this.heartbeatTimer = setInterval(() => {
            this.sendHeartbeat();
        }, this.options.heartbeatInterval);
    }
    
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
    
    sendHeartbeat() {
        this.sendMessage('heartbeat', { timestamp: Date.now() });
    }
    
    sendMessage(type, content, options = {}) {
        const messageId = this.generateMessageId();
        const message = {
            id: messageId,
            type: type,
            content: content,
            timestamp: Date.now(),
            retryCount: 0,
            maxRetries: options.maxRetries || 3
        };
        
        // 添加到队列
        this.messageQueue.push(message);
        
        // 如果连接正常，立即发送
        if (this.connectionState === 'connected') {
            this.sendMessageImmediate(message);
        } else {

        }
        
        return messageId;
    }
    
    sendMessageImmediate(message) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            return;
        }
        
        try {
            const data = {
                id: message.id,
                type: message.type,
                content: message.content,
                timestamp: message.timestamp
            };
            
            let dataStr = JSON.stringify(data);
            
            // 消息压缩
            if (this.options.enableCompression && dataStr.length > this.options.compressionThreshold) {
                const compressed = this.compressMessage(dataStr);
                this.socket.send(compressed);
            } else {
                this.socket.send(dataStr);
            }
            
            // 标记为已发送
            this.sentMessages.set(message.id, message);
            this.removeFromQueue(message.id);

        } catch (error) {
            console.error('发送消息失败:', error);
            // 消息发送失败，会在下次重连时重试
        }
    }
    
    sendQueuedMessages() {
        // 发送队列中的消息
        const messages = [...this.messageQueue];
        this.messageQueue = [];
        
        for (const message of messages) {
            this.sendMessageImmediate(message);
        }
        
        // 重试未确认的消息
        this.retryUnacknowledgedMessages();
    }
    
    retryUnacknowledgedMessages() {
        const currentTime = Date.now();
        for (const [messageId, message] of this.sentMessages) {
            if (!message.acknowledged && 
                message.retryCount < message.maxRetries &&
                currentTime - message.timestamp > 5000) { // 5秒后重试
                
                message.retryCount++;
                message.timestamp = currentTime;
                this.messageQueue.push(message);
                this.sentMessages.delete(messageId);
            }
        }
    }
    
    handleMessage(data) {
        try {
            // 尝试解压消息
            let messageData;
            if (typeof data === 'string') {
                messageData = JSON.parse(data);
            } else if (data instanceof ArrayBuffer) {
                const decompressed = this.decompressMessage(data);
                messageData = JSON.parse(decompressed);
            } else {
                console.error('未知消息格式:', data);
                return;
            }
            
            const messageId = messageData.id;
            const messageType = messageData.type;
            const content = messageData.content;
            
            // 标记消息已接收
            if (messageId) {
                this.receivedMessages.add(messageId);
                this.markMessageAcknowledged(messageId);
            }
            
            // 处理心跳消息
            if (messageType === 'heartbeat') {
                this.sendMessage('heartbeat_ack', { timestamp: Date.now() });
                return;
            }
            
            if (messageType === 'heartbeat_ack') {
                return;
            }
            
            // 处理连接状态
            if (messageType === 'connection_state') {
                this.updateState(content.state);
                return;
            }
            
            // 处理连接建立
            if (messageType === 'connection_established') {

                return;
            }
            
            // 处理聊天消息
            if (messageType === 'chat_message') {
                this.onMessage(content);
                return;
            }
            
            // 处理用户加入
            if (messageType === 'user_joined') {
                this.onUserJoined(content);
                return;
            }
            
            // 处理用户离开
            if (messageType === 'user_left') {
                this.onUserLeft(content);
                return;
            }
            
            // 处理打字状态
            if (messageType === 'typing_status') {
                this.onTyping(content);
                return;
            }
            
            // 处理已读状态
            if (messageType === 'read_status_update') {
                this.onReadStatus(content);
                return;
            }

        } catch (error) {
            console.error('处理消息失败:', error);
        }
    }
    
    markMessageAcknowledged(messageId) {
        if (this.sentMessages.has(messageId)) {
            const message = this.sentMessages.get(messageId);
            message.acknowledged = true;
            this.sentMessages.delete(messageId);
        }
    }
    
    removeFromQueue(messageId) {
        const index = this.messageQueue.findIndex(msg => msg.id === messageId);
        if (index !== -1) {
            this.messageQueue.splice(index, 1);
        }
    }
    
    updateState(newState) {
        if (this.connectionState !== newState) {
            this.connectionState = newState;
            this.onStateChange(newState);
        }
    }
    
    handleNetworkChange(isOnline) {
        this.isOnline = isOnline;
        
        if (isOnline && this.connectionState === 'disconnected') {

            this.connect();
        } else if (!isOnline) {

            this.updateState('error');
        }
    }
    
    checkConnection() {
        if (this.connectionState !== 'connected' && this.isOnline) {

            this.connect();
        }
    }
    
    // 消息压缩/解压
    compressMessage(data) {
        try {
            const encoder = new TextEncoder();
            const dataArray = encoder.encode(data);
            
            // 使用简单的压缩算法（在实际应用中可以使用更高效的压缩）
            const compressed = new Uint8Array(dataArray.length);
            let compressedIndex = 0;
            
            for (let i = 0; i < dataArray.length; i++) {
                if (i > 0 && dataArray[i] === dataArray[i - 1]) {
                    // 简单的重复字符压缩
                    compressed[compressedIndex - 1]++;
                } else {
                    compressed[compressedIndex] = dataArray[i];
                    compressedIndex++;
                }
            }
            
            return compressed.slice(0, compressedIndex);
        } catch (error) {
            console.error('消息压缩失败:', error);
            return new TextEncoder().encode(data);
        }
    }
    
    decompressMessage(data) {
        try {
            const decoder = new TextDecoder();
            return decoder.decode(data);
        } catch (error) {
            console.error('消息解压失败:', error);
            return '';
        }
    }
    
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    // 公共方法
    sendChatMessage(content, messageType = 'text') {
        return this.sendMessage('message', {
            content: content,
            message_type: messageType
        });
    }
    
    sendTypingStatus(isTyping) {
        return this.sendMessage('typing', { typing: isTyping });
    }
    
    sendReadStatus(messageId) {
        return this.sendMessage('read_status', { message_id: messageId });
    }
    
    sendFileUpload(fileData) {
        return this.sendMessage('file_upload', { file_data: fileData });
    }
    
    sendImageMessage(imageData) {
        return this.sendMessage('image_message', { image_data: imageData });
    }
    
    sendVoiceMessage(voiceData) {
        return this.sendMessage('voice_message', { voice_data: voiceData });
    }
    
    sendVideoMessage(videoData) {
        return this.sendMessage('video_message', { video_data: videoData });
    }
    
    getConnectionState() {
        return this.connectionState;
    }
    
    getQueueSize() {
        return this.messageQueue.length;
    }
    
    getUnacknowledgedCount() {
        return this.sentMessages.size;
    }
}

// 表情数据
const emojiData = {
    smileys: ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗', '🤔', '🤭', '🤫', '🤥', '😶', '😐', '😑', '😯', '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐', '🥴', '🤢', '🤮', '🤧', '😷', '🤒', '🤕', '🤑', '🤠'],
    gestures: ['👋', '🤚', '🖐️', '✋', '🖖', '👌', '🤌', '🤏', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👍', '👎', '✊', '👊', '🤛', '🤜', '👏', '🙌', '👐', '🤲', '🤝', '🙏', '✍️', '💪', '🦾', '🦿', '🦵', '🦶', '👂', '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀', '👁️', '👅', '👄', '💋', '🩸'],
    people: ['👶', '👧', '🧒', '👦', '👩', '🧑', '👨', '👩‍🦱', '🧑‍🦱', '👨‍🦱', '👩‍🦰', '🧑‍🦰', '👨‍🦰', '👱‍♀️', '👱', '👱‍♂️', '👩‍🦳', '🧑‍🦳', '👨‍🦳', '👩‍🦲', '🧑‍🦲', '👨‍🦲', '🧔‍♀️', '🧔', '🧔‍♂️', '👵', '🧓', '👴', '👮‍♀️', '👮', '👮‍♂️', '🕵️‍♀️', '🕵️', '🕵️‍♂️', '💂‍♀️', '💂', '💂‍♂️', '👷‍♀️', '👷', '👷‍♂️', '🫅', '🤴', '👸', '👳‍♀️', '👳', '👳‍♂️', '👲', '🧕‍♀️', '🧕', '🧕‍♂️', '🤵‍♀️', '🤵', '🤵‍♂️', '👰‍♀️', '👰', '👰‍♂️', '🤰‍♀️', '🤰', '🤰‍♂️', '🤱‍♀️', '🤱', '🤱‍♂️', '👼', '🎅', '🤶', '🦸‍♀️', '🦸', '🦸‍♂️', '🦹‍♀️', '🦹', '🦹‍♂️', '🧙‍♀️', '🧙', '🧙‍♂️', '🧚‍♀️', '🧚', '🧚‍♂️', '🧛‍♀️', '🧛', '🧛‍♂️', '🧜‍♀️', '🧜', '🧜‍♂️', '🧝‍♀️', '🧝', '🧝‍♂️', '🧞‍♀️', '🧞', '🧞‍♂️', '🧟‍♀️', '🧟', '🧟‍♂️', '🧌', '🙍‍♀️', '🙍', '🙍‍♂️', '🙎‍♀️', '🙎', '🙎‍♂️', '🙅‍♀️', '🙅', '🙅‍♂️', '🙆‍♀️', '🙆', '🙆‍♂️', '💁‍♀️', '💁', '💁‍♂️', '🙋‍♀️', '🙋', '🙋‍♂️', '🧏‍♀️', '🧏', '🧏‍♂️', '🙇‍♀️', '🙇', '🙇‍♂️', '🤦‍♀️', '🤦', '🤦‍♂️', '🤷‍♀️', '🤷', '🤷‍♂️', '👩‍⚕️', '🧑‍⚕️', '👨‍⚕️', '👩‍🎓', '🧑‍🎓', '👨‍🎓', '👩‍🏫', '🧑‍🏫', '👨‍🏫', '👩‍⚖️', '🧑‍⚖️', '👨‍⚖️', '👩‍🌾', '🧑‍🌾', '👨‍🌾', '👩‍🍳', '🧑‍🍳', '👨‍🍳', '👩‍🔧', '🧑‍🔧', '👨‍🔧', '👩‍🏭', '🧑‍🏭', '👨‍🏭', '👩‍💼', '🧑‍💼', '👨‍💼', '👩‍🔬', '🧑‍🔬', '👨‍🔬', '👩‍💻', '🧑‍💻', '👨‍💻', '👩‍🎤', '🧑‍🎤', '👨‍🎤', '👩‍🎨', '🧑‍🎨', '👨‍🎨', '👩‍✈️', '🧑‍✈️', '👨‍✈️', '👩‍🚀', '🧑‍🚀', '👨‍🚀', '👩‍🚒', '🧑‍🚒', '👨‍🚒', '👮‍♀️', '👮', '👮‍♂️', '🕵️‍♀️', '🕵️', '🕵️‍♂️', '💂‍♀️', '💂', '💂‍♂️', '🥷‍♀️', '🥷', '🥷‍♂️', '👷‍♀️', '👷', '👷‍♂️', '🫅', '🤴', '👸', '👳‍♀️', '👳', '👳‍♂️', '👲', '🧕‍♀️', '🧕', '🧕‍♂️', '🤵‍♀️', '🤵', '🤵‍♂️', '👰‍♀️', '👰', '👰‍♂️', '🤰‍♀️', '🤰', '🤰‍♂️', '🤱‍♀️', '🤱', '🤱‍♂️', '👼', '🎅', '🤶', '🦸‍♀️', '🦸', '🦸‍♂️', '🦹‍♀️', '🦹', '🦹‍♂️', '🧙‍♀️', '🧙', '🧙‍♂️', '🧚‍♀️', '🧚', '🧚‍♂️', '🧛‍♀️', '🧛', '🧛‍♂️', '🧜‍♀️', '🧜', '🧜‍♂️', '🧝‍♀️', '🧝', '🧝‍♂️', '🧞‍♀️', '🧞', '🧞‍♂️', '🧟‍♀️', '🧟', '🧟‍♂️', '🧌', '🙍‍♀️', '🙍', '🙍‍♂️', '🙎‍♀️', '🙎', '🙎‍♂️', '🙅‍♀️', '🙅', '🙅‍♂️', '🙆‍♀️', '🙆', '🙆‍♂️', '💁‍♀️', '💁', '💁‍♂️', '🙋‍♀️', '🙋', '🙋‍♂️', '🧏‍♀️', '🧏', '🧏‍♂️', '🙇‍♀️', '🙇', '🙇‍♂️', '🤦‍♀️', '🤦', '🤦‍♂️', '🤷‍♀️', '🤷', '🤷‍♂️'],
    symbols: ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓', '🆔', '⚛️', '🉑', '☢️', '☣️', '📴', '📳', '🈶', '🈚', '🈸', '🈺', '🈷️', '✴️', '🆚', '💮', '🉐', '㊙️', '㊗️', '🈴', '🈵', '🈹', '🈲', '🅰️', '🅱️', '🆎', '🆑', '🅾️', '🆘', '❌', '⭕', '🛑', '⛔', '📛', '🚫', '💯', '💢', '♨️', '🚷', '🚯', '🚳', '🚱', '🔞', '📵', '🚭', '❗', '❕', '❓', '❔', '‼️', '⁉️', '🔅', '🔆', '〽️', '⚠️', '🚸', '🔱', '⚜️', '🔰', '♻️', '✅', '🈯', '💹', '❇️', '✳️', '❎', '🌐', '💠', 'Ⓜ️', '🌀', '💤', '🏧', '🚾', '♿', '🅿️', '🛗', '🛂', '🛃', '🛄', '🛅', '🚹', '🚺', '🚼', '🚻', '🚮', '🎦', '📶', '🈁', '🔣', 'ℹ️', '🔤', '🔡', '🔠', '🆖', '🆗', '🆙', '🆒', '🆕', '🆓', '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '🔢', '#️⃣', '*️⃣', '⏏️', '▶️', '⏸️', '⏯️', '⏹️', '⏺️', '⏭️', '⏮️', '⏩', '⏪', '⏫', '⏬', '◀️', '🔼', '🔽', '➡️', '⬅️', '⬆️', '⬇️', '↗️', '↘️', '↙️', '↖️', '↕️', '↔️', '↪️', '↩️', '⤴️', '⤵️', '🔀', '🔁', '🔂', '🔄', '🔃', '🎵', '🎶', '➕', '➖', '➗', '✖️', '♾️', '💲', '💱', '™️', '©️', '®️', '👁️‍🗨️', '🔚', '🔙', '🔛', '🔝', '🔜', '〰️', '➰', '➿', '✔️', '☑️', '🔘', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '⚫', '⚪', '🟤', '🔺', '🔻', '🔸', '🔹', '🔶', '🔷', '🔳', '🔲', '▪️', '▫️', '◾', '◽', '◼️', '◻️', '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '⬛', '⬜', '🟫', '🔈', '🔇', '🔉', '🔊', '🔔', '🔕', '📣', '📢', '💬', '💭', '🗯️', '♠️', '♣️', '♥️', '♦️', '🃏', '🎴', '🀄', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛', '🕜', '🕝', '🕞', '🕟', '🕠', '🕡', '🕢', '🕣', '🕤', '🕥', '🕦', '🕧']
};

// 全局变量
let chatManager = null;
let roomId = null;
let typingTimer = null;
let isTyping = false;

// 初始化聊天功能
function initChat() {
    roomId = document.querySelector('[data-room-id]')?.dataset.roomId || 'test-room-' + Date.now();
    
    // 创建聊天管理器
    chatManager = new EnhancedChatManager(roomId, {
        onMessage: handleChatMessage,
        onStateChange: handleConnectionStateChange,
        onUserJoined: handleUserJoined,
        onUserLeft: handleUserLeft,
        onTyping: handleTyping,
        onReadStatus: handleReadStatus
    });
    
    initEmojiPanel();
    initToolButtons();
    loadParticipants();
    initFileUpload();
    initVoiceRecording();
    initVideoCall();
}

// 处理聊天消息
function handleChatMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;
    
    const messageElement = createMessageElement(message);
    messagesContainer.appendChild(messageElement);
    scrollToBottom();
}

// 处理连接状态变化
function handleConnectionStateChange(state) {
    const statusElement = document.getElementById('connectionStatus');
    if (!statusElement) return;
    
    const statusMap = {
        'connecting': { text: '连接中...', class: 'connecting' },
        'connected': { text: '已连接', class: 'connected' },
        'disconnected': { text: '连接已断开', class: 'disconnected' },
        'reconnecting': { text: '重连中...', class: 'reconnecting' },
        'error': { text: '连接错误', class: 'error' }
    };
    
    const status = statusMap[state] || { text: '未知状态', class: 'unknown' };
    statusElement.textContent = status.text;
    statusElement.className = `connection-status ${status.class}`;
    
    // 更新发送按钮状态
    const sendBtn = document.getElementById('sendBtn');
    if (sendBtn) {
        sendBtn.disabled = state !== 'connected';
    }
}

// 处理用户加入
function handleUserJoined(user) {
    addSystemMessage(`${user.username} 加入了聊天室`);
    updateParticipants();
}

// 处理用户离开
function handleUserLeft(user) {
    addSystemMessage(`${user.username} 离开了聊天室`);
    updateParticipants();
}

// 处理打字状态
function handleTyping(data) {
    const typingIndicator = document.getElementById('typingIndicator');
    if (!typingIndicator) return;
    
    if (data.typing) {
        typingIndicator.textContent = `${data.username} 正在输入...`;
        typingIndicator.style.display = 'block';
    } else {
        typingIndicator.style.display = 'none';
    }
}

// 处理已读状态
function handleReadStatus(data) {
    // 可以在这里更新消息的已读状态

}

// 创建消息元素
function createMessageElement(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const isOwnMessage = message.username === getCurrentUsername();
    messageDiv.classList.add(isOwnMessage ? 'own-message' : 'other-message');
    
    let content = '';
    
    switch (message.message_type) {
        case 'image':
            content = `<img src="${message.content}" alt="图片消息" class="message-image">`;
            break;
        case 'file':
            content = `<div class="file-message">
                <i class="fas fa-file"></i>
                <span>${message.content}</span>
                <button onclick="downloadFile('${message.content}')">下载</button>
            </div>`;
            break;
        case 'voice':
            content = `<div class="voice-message">
                <i class="fas fa-microphone"></i>
                <audio controls src="${message.content}"></audio>
            </div>`;
            break;
        case 'video':
            content = `<div class="video-message">
                <video controls src="${message.content}"></video>
            </div>`;
            break;
        default:
            content = `<span class="message-text">${escapeHtml(message.content)}</span>`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="username">${message.username}</span>
            <span class="timestamp">${formatTime(message.timestamp)}</span>
        </div>
        <div class="message-content">
            ${content}
        </div>
    `;
    
    return messageDiv;
}

// 发送消息
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    if (!messageInput || !chatManager) return;
    
    const content = messageInput.value.trim();
    if (!content) return;
    
    // 发送消息
    chatManager.sendChatMessage(content);
    
    // 清空输入框
    messageInput.value = '';
    
    // 停止打字状态
    stopTyping();
}

// 发送表情
function sendEmoji(emoji) {
    if (!chatManager) return;
    chatManager.sendChatMessage(emoji, 'emoji');
}

// 处理按键事件
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    } else {
        startTyping();
    }
}

// 开始打字
function startTyping() {
    if (isTyping) return;
    
    isTyping = true;
    if (chatManager) {
        chatManager.sendTypingStatus(true);
    }
    
    // 3秒后停止打字状态
    if (typingTimer) {
        clearTimeout(typingTimer);
    }
    typingTimer = setTimeout(stopTyping, 3000);
}

// 停止打字
function stopTyping() {
    if (!isTyping) return;
    
    isTyping = false;
    if (chatManager) {
        chatManager.sendTypingStatus(false);
    }
    
    if (typingTimer) {
        clearTimeout(typingTimer);
        typingTimer = null;
    }
}

// 初始化表情面板
function initEmojiPanel() {
    const emojiButton = document.getElementById('emojiButton');
    if (!emojiButton) return;
    
    emojiButton.addEventListener('click', () => {
        const emojiPanel = document.getElementById('emojiPanel');
        if (emojiPanel) {
            emojiPanel.style.display = emojiPanel.style.display === 'none' ? 'block' : 'none';
        }
    });
    
    // 创建表情面板
    createEmojiPanel();
}

// 创建表情面板
function createEmojiPanel() {
    let emojiPanel = document.getElementById('emojiPanel');
    if (!emojiPanel) {
        emojiPanel = document.createElement('div');
        emojiPanel.id = 'emojiPanel';
        emojiPanel.className = 'emoji-panel';
        document.body.appendChild(emojiPanel);
    }
    
    let emojiHtml = '';
    for (const [category, emojis] of Object.entries(emojiData)) {
        emojiHtml += `<div class="emoji-category">
            <h4>${category}</h4>
            <div class="emoji-list">`;
        
        emojis.forEach(emoji => {
            emojiHtml += `<span class="emoji" onclick="sendEmoji('${emoji}')">${emoji}</span>`;
        });
        
        emojiHtml += `</div></div>`;
    }
    
    emojiPanel.innerHTML = emojiHtml;
}

// 初始化工具按钮
function initToolButtons() {
    // 文件上传
    const fileButton = document.getElementById('fileButton');
    if (fileButton) {
        fileButton.addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
    }
    
    // 语音录制
    const voiceButton = document.getElementById('voiceButton');
    if (voiceButton) {
        voiceButton.addEventListener('click', toggleVoiceRecording);
    }
    
    // 视频通话
    const videoButton = document.getElementById('videoButton');
    if (videoButton) {
        videoButton.addEventListener('click', toggleVideoCall);
    }
}

// 初始化文件上传
function initFileUpload() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput) return;
    
    fileInput.addEventListener('change', handleFileUpload);
}

// 处理文件上传
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file || !chatManager) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const fileData = {
            name: file.name,
            size: file.size,
            type: file.type,
            data: e.target.result
        };
        
        chatManager.sendFileUpload(fileData);
    };
    reader.readAsDataURL(file);
}

// 初始化语音录制
function initVoiceRecording() {
    // 语音录制功能实现

}

// 切换语音录制
function toggleVoiceRecording() {

}

// 初始化视频通话
function initVideoCall() {
    // 视频通话功能实现

}

// 切换视频通话
function toggleVideoCall() {

}

// 加载参与者
function loadParticipants() {
    // 这里可以从服务器加载参与者列表

}

// 更新参与者
function updateParticipants() {
    // 更新参与者列表显示

}

// 添加系统消息
function addSystemMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'system-message';
    messageDiv.textContent = message;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// 滚动到底部
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// 获取当前用户名
function getCurrentUsername() {
    // 从页面或全局变量获取当前用户名
    return document.querySelector('[data-username]')?.dataset.username || 'Unknown';
}

// 格式化时间
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 下载文件
function downloadFile(fileUrl) {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initChat();
});

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (chatManager) {
        chatManager.disconnect();
    }
});
