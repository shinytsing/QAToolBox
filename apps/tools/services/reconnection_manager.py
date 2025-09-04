import asyncio
import json
import logging
import time
import zlib
import gzip
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import weakref

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """连接状态枚举"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class Message:
    """消息数据结构"""

    id: str
    type: str
    content: Any
    timestamp: float
    retry_count: int = 0
    max_retries: int = 3
    acknowledged: bool = False


@dataclass
class ConnectionConfig:
    """连接配置"""

    url: str
    heartbeat_interval: int = 30
    reconnect_delay: float = 1.0
    max_reconnect_delay: float = 60.0
    max_reconnect_attempts: int = 10
    message_timeout: float = 10.0
    enable_compression: bool = True
    compression_threshold: int = 1024  # 1KB以上才压缩


class NetworkMonitor:
    """网络状态监控器"""

    def __init__(self):
        self.is_online = True
        self.last_check = time.time()
        self.check_interval = 5.0
        self._callbacks = []

    def add_callback(self, callback: Callable[[bool], None]):
        """添加网络状态变化回调"""
        self._callbacks.append(callback)

    def check_network_status(self) -> bool:
        """检查网络状态"""
        try:
            import socket

            socket.create_connection(("8.8.8.8", 53), timeout=3)
            current_status = True
        except OSError:
            current_status = False

        if current_status != self.is_online:
            self.is_online = current_status
            self._notify_callbacks(current_status)

        self.last_check = time.time()
        return current_status

    def _notify_callbacks(self, is_online: bool):
        """通知回调函数"""
        for callback in self._callbacks:
            try:
                callback(is_online)
            except Exception as e:
                logger.error(f"网络状态回调执行失败: {e}")


class MessageCompressor:
    """消息压缩器"""

    @staticmethod
    def compress(data: str) -> bytes:
        """压缩消息"""
        try:
            return gzip.compress(data.encode("utf-8"))
        except Exception as e:
            logger.error(f"消息压缩失败: {e}")
            return data.encode("utf-8")

    @staticmethod
    def decompress(data: bytes) -> str:
        """解压消息"""
        try:
            return gzip.decompress(data).decode("utf-8")
        except Exception as e:
            logger.error(f"消息解压失败: {e}")
            return data.decode("utf-8", errors="ignore")


class MessageQueue:
    """消息队列管理器"""

    def __init__(self, max_size: int = 1000):
        self.pending_messages: deque = deque(maxlen=max_size)
        self.sent_messages: Dict[str, Message] = {}
        self.received_messages: set = set()
        self._message_id_counter = 0

    def add_message(self, message_type: str, content: Any, max_retries: int = 3) -> str:
        """添加消息到队列"""
        message_id = f"msg_{int(time.time() * 1000)}_{self._message_id_counter}"
        self._message_id_counter += 1

        message = Message(id=message_id, type=message_type, content=content, timestamp=time.time(), max_retries=max_retries)

        self.pending_messages.append(message)
        return message_id

    def get_pending_messages(self) -> List[Message]:
        """获取待发送消息"""
        return list(self.pending_messages)

    def mark_sent(self, message_id: str):
        """标记消息已发送"""
        for i, msg in enumerate(self.pending_messages):
            if msg.id == message_id:
                msg.acknowledged = True
                self.sent_messages[message_id] = msg
                self.pending_messages.remove(msg)
                break

    def mark_received(self, message_id: str):
        """标记消息已接收"""
        self.received_messages.add(message_id)
        if message_id in self.sent_messages:
            del self.sent_messages[message_id]

    def get_unacknowledged_messages(self) -> List[Message]:
        """获取未确认的消息"""
        return [msg for msg in self.sent_messages.values() if not msg.acknowledged]

    def retry_failed_messages(self):
        """重试失败的消息"""
        current_time = time.time()
        for msg in list(self.sent_messages.values()):
            if not msg.acknowledged and msg.retry_count < msg.max_retries and current_time - msg.timestamp > 5.0:  # 5秒后重试
                msg.retry_count += 1
                msg.timestamp = current_time
                self.pending_messages.append(msg)
                del self.sent_messages[msg.id]


class ReconnectionManager:
    """重连管理器"""

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.state = ConnectionState.DISCONNECTED
        self.websocket = None
        self.reconnect_attempts = 0
        self.last_reconnect_time = 0
        self.heartbeat_task = None
        self.network_monitor = NetworkMonitor()
        self.message_queue = MessageQueue()
        self.message_handlers: Dict[str, Callable] = {}
        self.state_callbacks: List[Callable[[ConnectionState], None]] = []

        # 注册网络状态回调
        self.network_monitor.add_callback(self._on_network_status_change)

    def add_message_handler(self, message_type: str, handler: Callable):
        """添加消息处理器"""
        self.message_handlers[message_type] = handler

    def add_state_callback(self, callback: Callable[[ConnectionState], None]):
        """添加状态变化回调"""
        self.state_callbacks.append(callback)

    def _update_state(self, new_state: ConnectionState):
        """更新连接状态"""
        if self.state != new_state:
            self.state = new_state
            for callback in self.state_callbacks:
                try:
                    callback(new_state)
                except Exception as e:
                    logger.error(f"状态回调执行失败: {e}")

    def _on_network_status_change(self, is_online: bool):
        """网络状态变化处理"""
        if is_online and self.state == ConnectionState.DISCONNECTED:
            logger.info("网络恢复，尝试重连")
            asyncio.create_task(self.reconnect())
        elif not is_online:
            logger.warning("网络断开")
            self._update_state(ConnectionState.ERROR)

    async def connect(self, websocket_factory: Callable):
        """建立连接"""
        if self.state in [ConnectionState.CONNECTING, ConnectionState.CONNECTED]:
            return

        self._update_state(ConnectionState.CONNECTING)

        try:
            self.websocket = await websocket_factory()
            self._update_state(ConnectionState.CONNECTED)
            self.reconnect_attempts = 0

            # 启动心跳任务
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            # 发送未确认的消息
            await self._send_pending_messages()

            logger.info("WebSocket连接成功")

        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            self._update_state(ConnectionState.ERROR)
            await self._schedule_reconnect()

    async def disconnect(self):
        """断开连接"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None

        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"关闭WebSocket失败: {e}")
            finally:
                self.websocket = None

        self._update_state(ConnectionState.DISCONNECTED)

    async def reconnect(self):
        """重连"""
        if self.state == ConnectionState.RECONNECTING:
            return

        self._update_state(ConnectionState.RECONNECTING)

        # 指数退避策略
        delay = min(self.config.reconnect_delay * (2**self.reconnect_attempts), self.config.max_reconnect_delay)

        if time.time() - self.last_reconnect_time < delay:
            await asyncio.sleep(delay)

        self.last_reconnect_time = time.time()
        self.reconnect_attempts += 1

        if self.reconnect_attempts > self.config.max_reconnect_attempts:
            logger.error("重连次数已达上限")
            self._update_state(ConnectionState.ERROR)
            return

        logger.info(f"尝试重连 ({self.reconnect_attempts}/{self.config.max_reconnect_attempts})")

        try:
            await self.disconnect()
            await asyncio.sleep(delay)
            await self.connect(self._create_websocket)
        except Exception as e:
            logger.error(f"重连失败: {e}")
            await self._schedule_reconnect()

    async def _schedule_reconnect(self):
        """安排重连"""
        if self.state != ConnectionState.ERROR:
            return

        asyncio.create_task(self.reconnect())

    async def _create_websocket(self):
        """创建WebSocket连接"""
        import websockets

        return await websockets.connect(self.config.url)

    async def send_message(self, message_type: str, content: Any, max_retries: int = 3) -> str:
        """发送消息"""
        message_id = self.message_queue.add_message(message_type, content, max_retries)

        if self.state == ConnectionState.CONNECTED:
            await self._send_message_immediate(message_id)
        else:
            logger.info(f"连接未建立，消息已加入队列: {message_id}")

        return message_id

    async def _send_message_immediate(self, message_id: str):
        """立即发送消息"""
        if not self.websocket:
            return

        try:
            # 查找消息
            message = None
            for msg in self.message_queue.pending_messages:
                if msg.id == message_id:
                    message = msg
                    break

            if not message:
                return

            # 准备消息数据
            message_data = {"id": message.id, "type": message.type, "content": message.content, "timestamp": message.timestamp}

            data_str = json.dumps(message_data, ensure_ascii=False)

            # 压缩消息
            if self.config.enable_compression and len(data_str) > self.config.compression_threshold:
                compressed_data = MessageCompressor.compress(data_str)
                await self.websocket.send(compressed_data)
            else:
                await self.websocket.send(data_str)

            # 标记为已发送
            self.message_queue.mark_sent(message_id)
            logger.debug(f"消息发送成功: {message_id}")

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            # 消息发送失败，会在下次重连时重试

    async def _send_pending_messages(self):
        """发送待发送消息"""
        pending_messages = self.message_queue.get_pending_messages()
        for message in pending_messages:
            await self._send_message_immediate(message.id)

    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.state == ConnectionState.CONNECTED:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)

                if self.state != ConnectionState.CONNECTED:
                    break

                # 发送心跳消息
                await self.send_message("heartbeat", {"timestamp": time.time()})

                # 重试失败的消息
                self.message_queue.retry_failed_messages()

                # 检查网络状态
                self.network_monitor.check_network_status()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳任务异常: {e}")

    async def handle_message(self, data: str):
        """处理接收到的消息"""
        try:
            # 尝试解压消息
            if data.startswith(b"\x1f\x8b"):  # gzip magic number
                data = MessageCompressor.decompress(data)
            elif isinstance(data, bytes):
                data = data.decode("utf-8")

            message_data = json.loads(data)
            message_id = message_data.get("id")
            message_type = message_data.get("type")
            content = message_data.get("content")

            # 标记消息已接收
            if message_id:
                self.message_queue.mark_received(message_id)

            # 处理心跳消息
            if message_type == "heartbeat":
                await self.send_message("heartbeat_ack", {"timestamp": time.time()})
                return

            # 处理心跳确认
            if message_type == "heartbeat_ack":
                return

            # 调用消息处理器
            if message_type in self.message_handlers:
                try:
                    await self.message_handlers[message_type](content)
                except Exception as e:
                    logger.error(f"消息处理器异常: {e}")
            else:
                logger.warning(f"未知消息类型: {message_type}")

        except Exception as e:
            logger.error(f"处理消息失败: {e}")

    async def start_listening(self):
        """开始监听消息"""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except Exception as e:
            logger.error(f"消息监听异常: {e}")
            await self._schedule_reconnect()


# 全局重连管理器实例
_reconnection_managers: Dict[str, ReconnectionManager] = {}


def get_reconnection_manager(room_id: str, config: ConnectionConfig) -> ReconnectionManager:
    """获取重连管理器实例"""
    if room_id not in _reconnection_managers:
        _reconnection_managers[room_id] = ReconnectionManager(config)

    return _reconnection_managers[room_id]


def remove_reconnection_manager(room_id: str):
    """移除重连管理器实例"""
    if room_id in _reconnection_managers:
        manager = _reconnection_managers[room_id]
        asyncio.create_task(manager.disconnect())
        del _reconnection_managers[room_id]
