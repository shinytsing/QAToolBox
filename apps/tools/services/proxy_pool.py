#!/usr/bin/env python3
"""
虚拟IP池管理系统 - 反爬虫解决方案
支持多种代理源和智能切换

主要功能：
- 多源代理自动采集
- 智能代理质量评估
- 代理池健康监控
- 自适应轮换策略
- 详细统计分析
"""

import hashlib
import json
import logging
import os
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

import requests

# 设置更详细的日志格式
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class ProxyProtocol(Enum):
    """代理协议枚举"""

    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyAnonymity(Enum):
    """代理匿名性枚举"""

    TRANSPARENT = "transparent"
    ANONYMOUS = "anonymous"
    HIGH_ANONYMOUS = "high_anonymous"
    UNKNOWN = "unknown"


@dataclass
class ProxyConfig:
    """代理池配置类"""

    max_pool_size: int = 100
    check_interval: int = 300  # 5分钟
    max_retries: int = 3
    timeout: int = 10
    min_success_rate: float = 0.3
    max_response_time: float = 30.0
    concurrent_checks: int = 10
    proxy_file: str = "proxy_pool.json"


@dataclass
class ProxyInfo:
    """代理信息数据类"""

    proxy: str
    protocol: str = ProxyProtocol.HTTP.value
    country: str = "unknown"
    anonymity: str = ProxyAnonymity.UNKNOWN.value
    last_checked: Optional[str] = None
    success_count: int = 0
    fail_count: int = 0
    response_time: float = 0.0
    source: str = "manual"
    score: float = 0.0  # 代理质量评分

    @property
    def success_rate(self) -> float:
        """计算成功率"""
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 1.0

    @property
    def total_requests(self) -> int:
        """总请求次数"""
        return self.success_count + self.fail_count


class ProxyPool:
    """增强版虚拟IP池管理系统"""

    def __init__(self, config: Optional[ProxyConfig] = None):
        self.config = config or ProxyConfig()
        self.proxies: List[ProxyInfo] = []  # 可用代理列表
        self.failed_proxies: set = set()  # 失败代理集合
        self.proxy_stats = {}  # 代理统计信息
        self.last_check_time = None
        self._lock = threading.RLock()  # 线程安全锁

        # 代理源配置 - 优化并分类代理源
        self.proxy_sources = {
            # API类型源 - 稳定可靠
            "proxyscrape_http": {
                "url": "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
                "type": "api",
                "format": "text",
                "priority": 1,
            },
            "geonode_api": {
                "url": "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc",
                "type": "api",
                "format": "json",
                "priority": 1,
            },
            # GitHub源 - 社区维护
            "github_monosans": {
                "url": "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
                "type": "github",
                "format": "text",
                "priority": 2,
            },
            "github_clarketm": {
                "url": "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
                "type": "github",
                "format": "text",
                "priority": 2,
            },
            # 备用源
            "proxyscrape_socks4": {
                "url": "https://api.proxyscrape.com/v2/?request=get&protocol=socks4&timeout=10000&country=all",
                "type": "api",
                "format": "text",
                "priority": 3,
            },
        }

        # 初始化代理池
        self._load_local_proxies()
        if not self.proxies:
            self._fetch_fresh_proxies()

    def _load_local_proxies(self):
        """加载本地保存的代理"""
        try:
            if os.path.exists(self.config.proxy_file):
                with open(self.config.proxy_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # 转换为ProxyInfo对象
                    proxy_list = data.get("proxies", [])
                    self.proxies = []
                    for proxy_data in proxy_list:
                        if isinstance(proxy_data, dict):
                            # 兼容旧格式
                            self.proxies.append(ProxyInfo(**proxy_data))
                        else:
                            # 字符串格式，创建基本ProxyInfo
                            self.proxies.append(ProxyInfo(proxy=proxy_data))

                    self.proxy_stats = data.get("stats", {})
                    last_update = data.get("updated_at")

                    logger.info(f"✅ 加载本地代理池: {len(self.proxies)}个代理")
                    if last_update:
                        logger.info(f"📅 上次更新时间: {last_update}")
        except Exception as e:
            logger.warning(f"⚠️ 加载本地代理失败: {e}")
            self.proxies = []

    def _save_proxies(self):
        """保存代理到本地"""
        try:
            with self._lock:
                data = {
                    "proxies": [asdict(proxy) for proxy in self.proxies],
                    "stats": self.proxy_stats,
                    "updated_at": datetime.now().isoformat(),
                    "config": asdict(self.config),
                }

                # 创建备份
                if os.path.exists(self.config.proxy_file):
                    backup_file = f"{self.config.proxy_file}.backup"
                    os.rename(self.config.proxy_file, backup_file)

                with open(self.config.proxy_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                logger.debug(f"✅ 代理池已保存到 {self.config.proxy_file}")
        except Exception as e:
            logger.error(f"❌ 保存代理失败: {e}")
            # 尝试恢复备份
            backup_file = f"{self.config.proxy_file}.backup"
            if os.path.exists(backup_file):
                os.rename(backup_file, self.config.proxy_file)
                logger.info("🔄 已恢复代理池备份文件")

    def _fetch_fresh_proxies(self):
        """获取新的代理列表"""
        logger.info("🔄 获取新的代理列表...")
        new_proxies = []

        # 添加一些高质量免费代理源（定期更新）
        free_proxies = [
            # 美国代理
            "162.223.94.164:80",
            "45.55.32.201:3128",
            "165.22.81.188:43993",
            "138.68.60.8:8080",
            "159.65.207.97:80",
            # 欧洲代理
            "185.162.231.106:80",
            "91.107.6.115:53281",
            "185.38.111.1:8080",
            "193.70.36.70:8080",
            "46.4.96.137:8080",
            # 亚洲代理
            "103.127.1.130:80",
            "103.76.12.42:80",
            "114.129.2.82:8080",
            "47.74.152.29:8888",
            "8.210.83.33:80",
            # 高匿代理
            "167.172.173.210:44207",
            "128.199.202.122:8080",
            "20.111.54.16:80",
        ]

        # 创建高质量种子代理
        for proxy in free_proxies:
            new_proxies.append(
                ProxyInfo(
                    proxy=proxy,
                    protocol=ProxyProtocol.HTTP.value,
                    country="unknown",
                    anonymity=ProxyAnonymity.UNKNOWN.value,
                    source="builtin",
                )
            )

        # 按优先级排序获取在线代理源
        sorted_sources = sorted(self.proxy_sources.items(), key=lambda x: x[1]["priority"])

        for source_name, source_config in sorted_sources:
            try:
                logger.info(f"🌐 尝试从 {source_name} 获取代理...")

                # 为不同类型的代理源使用不同的请求头
                headers = {
                    "User-Agent": self.get_random_user_agent(),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Cache-Control": "no-cache",
                }

                response = requests.get(source_config["url"], headers=headers, timeout=20, verify=True)  # 启用SSL验证

                if response.status_code == 200:
                    # 根据不同源解析代理列表
                    parsed_proxies = self._parse_proxy_response(response, source_name, source_config)
                    if parsed_proxies:
                        # 限制每个源的代理数量，优先级高的源获取更多
                        max_count = 50 if source_config["priority"] == 1 else 30
                        new_proxies.extend(parsed_proxies[:max_count])
                        logger.info(f"✅ 从 {source_name} 获取到 {len(parsed_proxies)} 个代理")
                    else:
                        logger.warning(f"⚠️ {source_name} 未解析到有效代理")
                else:
                    logger.warning(f"⚠️ {source_name} 返回状态码: {response.status_code}")

            except Exception as e:
                logger.warning(f"⚠️ 从 {source_name} 获取代理失败: {e}")

            # 添加延迟避免请求过快
            time.sleep(random.uniform(1, 3))

        # 添加到代理池并去重
        if new_proxies:
            with self._lock:
                # 去重：基于代理地址
                existing_proxies = {p.proxy for p in self.proxies}
                unique_new_proxies = [p for p in new_proxies if p.proxy not in existing_proxies]

                if unique_new_proxies:
                    self.proxies.extend(unique_new_proxies)
                    # 保持池大小限制
                    if len(self.proxies) > self.config.max_pool_size:
                        self.proxies = self.proxies[-self.config.max_pool_size :]

                    logger.info(f"✅ 代理池更新完成，新增 {len(unique_new_proxies)} 个代理，当前总计 {len(self.proxies)} 个")
                else:
                    logger.info("ℹ️ 未发现新的代理地址")

                self._save_proxies()
        else:
            logger.warning("⚠️ 未获取到新代理，使用现有代理池")

    def _is_valid_ip(self, ip: str) -> bool:
        """验证IP地址格式"""
        try:
            parts = ip.split(".")
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except:
            return False

    def _parse_proxy_response(self, response, source_name: str, source_config: Dict) -> List[ProxyInfo]:
        """解析不同来源的代理响应"""
        proxies = []

        try:
            if source_config["format"] == "json":
                # JSON格式解析
                data = response.json()

                if "geonode" in source_name:
                    for item in data.get("data", []):
                        ip = item.get("ip")
                        port = item.get("port")
                        if ip and port and self._is_valid_ip(ip):
                            proxy_info = ProxyInfo(
                                proxy=f"{ip}:{port}",
                                protocol=item.get("protocols", ["http"])[0].lower(),
                                country=item.get("country", "unknown"),
                                anonymity=item.get("anonymityLevel", "unknown").lower(),
                                source=source_name,
                            )
                            proxies.append(proxy_info)
                else:
                    # 其他JSON格式的处理
                    for item in data if isinstance(data, list) else [data]:
                        if isinstance(item, dict) and "ip" in item and "port" in item:
                            ip = item["ip"]
                            port = item["port"]
                            if self._is_valid_ip(ip):
                                proxy_info = ProxyInfo(
                                    proxy=f"{ip}:{port}",
                                    protocol=item.get("type", "http").lower(),
                                    country=item.get("country", "unknown"),
                                    anonymity=item.get("anonymity", "unknown").lower(),
                                    source=source_name,
                                )
                                proxies.append(proxy_info)

            elif source_config["format"] == "text":
                # 纯文本格式解析
                proxies_text = response.text.strip()
                lines = proxies_text.split("\n")

                for line in lines:
                    line = line.strip()

                    # 跳过注释和空行
                    if not line or line.startswith("#") or line.startswith("//"):
                        continue

                    # 使用正则提取IP:端口
                    ip_port_pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})"
                    match = re.search(ip_port_pattern, line)

                    if match:
                        ip, port = match.groups()
                        if self._is_valid_ip(ip) and 1 <= int(port) <= 65535:
                            proxy_info = ProxyInfo(
                                proxy=f"{ip}:{port}",
                                protocol=self._detect_protocol_from_source(source_name),
                                country="unknown",
                                anonymity=ProxyAnonymity.UNKNOWN.value,
                                source=source_name,
                            )
                            proxies.append(proxy_info)

        except Exception as e:
            logger.warning(f"解析代理响应失败 {source_name}: {e}")

        return proxies

    def _detect_protocol_from_source(self, source_name: str) -> str:
        """从源名称检测协议类型"""
        source_lower = source_name.lower()
        if "socks5" in source_lower:
            return ProxyProtocol.SOCKS5.value
        elif "socks4" in source_lower:
            return ProxyProtocol.SOCKS4.value
        elif "https" in source_lower:
            return ProxyProtocol.HTTPS.value
        else:
            return ProxyProtocol.HTTP.value

    def _test_proxy(self, proxy_info: ProxyInfo) -> bool:
        """测试单个代理的可用性"""
        proxy = proxy_info.proxy
        try:
            # 使用多个测试URL提高准确性和成功率
            test_urls = [
                "http://httpbin.org/ip",
                "https://api.ipify.org?format=json",
                "http://ip-api.com/json",
                "https://httpbin.org/user-agent",
                "https://icanhazip.com",
                "http://jsonip.com",
            ]

            # 根据协议类型构建代理字典
            if proxy_info.protocol in [ProxyProtocol.SOCKS4.value, ProxyProtocol.SOCKS5.value]:
                proxy_dict = {"http": f"{proxy_info.protocol}://{proxy}", "https": f"{proxy_info.protocol}://{proxy}"}
            else:
                proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

            start_time = time.time()
            test_url = random.choice(test_urls)

            response = requests.get(
                test_url,
                proxies=proxy_dict,
                timeout=self.config.timeout,
                headers={"User-Agent": self.get_random_user_agent()},
                verify=True,
            )

            response_time = time.time() - start_time

            if response.status_code == 200 and response_time <= self.config.max_response_time:
                # 更新代理信息
                proxy_info.last_checked = datetime.now().isoformat()
                proxy_info.success_count += 1
                proxy_info.response_time = response_time

                # 计算代理质量评分 (0-100)
                proxy_info.score = self._calculate_proxy_score(proxy_info)

                # 更新统计信息
                if proxy not in self.proxy_stats:
                    self.proxy_stats[proxy] = {
                        "total_requests": 0,
                        "successful_requests": 0,
                        "avg_response_time": 0,
                        "last_success": None,
                    }

                stats = self.proxy_stats[proxy]
                stats["successful_requests"] += 1
                stats["total_requests"] += 1
                stats["avg_response_time"] = (stats["avg_response_time"] + response_time) / 2
                stats["last_success"] = datetime.now().isoformat()

                logger.debug(f"✅ 代理 {proxy} 测试成功 ({response_time:.2f}s, 评分: {proxy_info.score:.1f})")
                return True

        except Exception as e:
            proxy_info.fail_count += 1
            logger.debug(f"❌ 代理 {proxy} 测试失败: {e}")

            # 更新失败统计
            if proxy not in self.proxy_stats:
                self.proxy_stats[proxy] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "avg_response_time": 0,
                    "last_success": None,
                }

            self.proxy_stats[proxy]["total_requests"] += 1

        return False

    def _calculate_proxy_score(self, proxy_info: ProxyInfo) -> float:
        """计算代理质量评分"""
        score = 0.0

        # 成功率权重 (50%)
        if proxy_info.total_requests > 0:
            success_rate_score = proxy_info.success_rate * 50
            score += success_rate_score
        else:
            score += 25  # 新代理给予中等分数

        # 响应时间权重 (30%)
        if proxy_info.response_time > 0:
            # 响应时间越短分数越高，10秒以内满分
            time_score = max(0, (10 - proxy_info.response_time) / 10 * 30)
            score += time_score
        else:
            score += 15  # 未测试给予中等分数

        # 稳定性权重 (20%) - 基于连续成功次数
        stability_score = min(proxy_info.success_count / 10 * 20, 20)
        score += stability_score

        return min(score, 100.0)

    def get_working_proxy(self) -> Optional[ProxyInfo]:
        """获取一个可用的代理"""
        with self._lock:
            if not self.proxies:
                logger.warning("⚠️ 代理池为空，尝试获取新代理...")
                self._fetch_fresh_proxies()

            # 检查是否需要更新代理池
            if self.last_check_time is None or datetime.now() - self.last_check_time > timedelta(
                seconds=self.config.check_interval
            ):
                self._check_proxy_health()

            # 过滤可用代理
            available_proxies = []
            for proxy_info in self.proxies:
                if (
                    proxy_info.proxy not in self.failed_proxies
                    and proxy_info.fail_count < self.config.max_retries
                    and proxy_info.success_rate >= self.config.min_success_rate
                ):
                    available_proxies.append(proxy_info)

            if not available_proxies:
                logger.warning("⚠️ 没有可用代理，重新获取...")
                self._fetch_fresh_proxies()
                # 给新代理一个机会
                available_proxies = [p for p in self.proxies if p.fail_count < self.config.max_retries]

            if available_proxies:
                # 智能排序：综合考虑评分、成功率、响应时间
                available_proxies.sort(
                    key=lambda x: (
                        -x.score,  # 评分高优先
                        -x.success_rate,  # 成功率高优先
                        x.fail_count,  # 失败次数少优先
                        x.response_time,  # 响应时间短优先
                    )
                )

                # 从前5个最佳代理中随机选择，平衡负载
                best_proxies = available_proxies[:5]
                proxy_info = random.choice(best_proxies)

                logger.debug(
                    f"🎯 选择代理: {proxy_info.proxy} "
                    f"(评分: {proxy_info.score:.1f}, "
                    f"成功率: {proxy_info.success_rate:.2f}, "
                    f"响应时间: {proxy_info.response_time:.2f}s)"
                )

                return proxy_info

            return None

    def _check_proxy_health(self):
        """批量检查代理健康状态"""
        logger.info("🔍 检查代理池健康状态...")
        self.last_check_time = datetime.now()

        # 优先检查评分较低或长时间未检查的代理
        proxies_to_check = sorted(self.proxies, key=lambda x: (x.score, x.last_checked or ""))[:30]

        # 使用线程池并发测试
        with ThreadPoolExecutor(max_workers=self.config.concurrent_checks) as executor:
            future_to_proxy = {executor.submit(self._test_proxy, proxy): proxy for proxy in proxies_to_check}

            failed_count = 0
            success_count = 0

            for future in as_completed(future_to_proxy, timeout=60):
                proxy = future_to_proxy[future]
                try:
                    result = future.result()
                    if result:
                        success_count += 1
                    else:
                        failed_count += 1
                        # 标记连续失败多次的代理
                        if proxy.fail_count >= self.config.max_retries:
                            self.failed_proxies.add(proxy.proxy)
                except Exception as e:
                    logger.debug(f"代理 {proxy.proxy} 测试异常: {e}")
                    failed_count += 1
                    self.failed_proxies.add(proxy.proxy)

        # 清理失败代理
        original_count = len(self.proxies)
        self.proxies = [p for p in self.proxies if p.proxy not in self.failed_proxies]
        removed_count = original_count - len(self.proxies)

        # 保存更新后的代理池
        self._save_proxies()

        logger.info(
            f"✅ 代理池检查完成: 成功 {success_count}, 失败 {failed_count}, "
            f"移除 {removed_count}, 当前可用: {len(self.proxies)}个"
        )

    def mark_proxy_failed(self, proxy: str):
        """标记代理失败"""
        with self._lock:
            self.failed_proxies.add(proxy)
            # 更新对应代理的失败计数
            for proxy_info in self.proxies:
                if proxy_info.proxy == proxy:
                    proxy_info.fail_count += 1
                    break

            # 移除失败次数过多的代理
            self.proxies = [p for p in self.proxies if p.proxy != proxy or p.fail_count < self.config.max_retries * 2]

    def get_proxy_for_requests(self) -> Optional[Dict]:
        """获取用于requests的代理字典"""
        proxy_info = self.get_working_proxy()
        if proxy_info:
            proxy = proxy_info.proxy

            # 根据协议类型构建代理字典
            if proxy_info.protocol in [ProxyProtocol.SOCKS4.value, ProxyProtocol.SOCKS5.value]:
                proxy_dict = {
                    "http": f"{proxy_info.protocol}://{proxy}",
                    "https": f"{proxy_info.protocol}://{proxy}",
                    "info": proxy_info,
                }
            else:
                proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}", "info": proxy_info}

            return proxy_dict
        return None

    def add_custom_proxy(self, proxy: str, protocol: str = "http", country: str = "unknown", anonymity: str = "unknown"):
        """添加自定义代理"""
        with self._lock:
            # 检查是否已存在
            existing_proxies = {p.proxy for p in self.proxies}
            if proxy not in existing_proxies:
                proxy_info = ProxyInfo(proxy=proxy, protocol=protocol, country=country, anonymity=anonymity, source="manual")
                self.proxies.append(proxy_info)
                logger.info(f"✅ 已添加自定义代理: {proxy}")
                self._save_proxies()
                return True
            else:
                logger.warning(f"⚠️ 代理 {proxy} 已存在")
                return False

    def remove_proxy(self, proxy: str) -> bool:
        """移除指定代理"""
        with self._lock:
            original_count = len(self.proxies)
            self.proxies = [p for p in self.proxies if p.proxy != proxy]

            if len(self.proxies) < original_count:
                self.failed_proxies.discard(proxy)
                if proxy in self.proxy_stats:
                    del self.proxy_stats[proxy]
                self._save_proxies()
                logger.info(f"✅ 已移除代理: {proxy}")
                return True
            else:
                logger.warning(f"⚠️ 代理 {proxy} 不存在")
                return False

    def get_random_user_agent(self) -> str:
        """获取随机User-Agent - 大幅扩展库以提高反爬虫能力"""
        user_agents = [
            # Chrome - Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            # Chrome - macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            # Chrome - Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            # Firefox - Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            # Firefox - macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.6; rv:121.0) Gecko/20100101 Firefox/121.0",
            # Safari - macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            # Edge - Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/119.0.0.0",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0",
            # Mobile User Agents
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 13; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
            "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
            # Opera
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/106.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/106.0.0.0",
            # Different OS versions
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        ]
        return random.choice(user_agents)

    def get_stats(self) -> Dict:
        """获取代理池详细统计信息"""
        with self._lock:
            total_proxies = len(self.proxies)
            failed_proxies_count = len(self.failed_proxies)

            # 计算可用代理数量
            working_proxies = sum(
                1
                for p in self.proxies
                if p.proxy not in self.failed_proxies and p.success_rate >= self.config.min_success_rate
            )

            # 计算平均响应时间和评分
            response_times = [p.response_time for p in self.proxies if p.response_time > 0]
            scores = [p.score for p in self.proxies if p.score > 0]

            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            avg_score = sum(scores) / len(scores) if scores else 0

            # 按协议分类统计
            protocol_stats = {}
            for p in self.proxies:
                protocol = p.protocol
                if protocol not in protocol_stats:
                    protocol_stats[protocol] = 0
                protocol_stats[protocol] += 1

            # 按来源分类统计
            source_stats = {}
            for p in self.proxies:
                source = p.source
                if source not in source_stats:
                    source_stats[source] = 0
                source_stats[source] += 1

            # 按国家分类统计
            country_stats = {}
            for p in self.proxies:
                country = p.country
                if country not in country_stats:
                    country_stats[country] = 0
                country_stats[country] += 1

            # 高质量代理统计（评分>70）
            high_quality_proxies = sum(1 for p in self.proxies if p.score > 70)

            return {
                "total_proxies": total_proxies,
                "working_proxies": working_proxies,
                "failed_proxies": failed_proxies_count,
                "high_quality_proxies": high_quality_proxies,
                "success_rate": (working_proxies / max(total_proxies, 1)) * 100,
                "avg_response_time": round(avg_response_time, 2),
                "avg_score": round(avg_score, 1),
                "protocol_distribution": protocol_stats,
                "source_distribution": source_stats,
                "country_distribution": country_stats,
                "config": asdict(self.config),
                "last_health_check": self.last_check_time.isoformat() if self.last_check_time else None,
                "pool_quality": (
                    "excellent" if avg_score > 80 else "good" if avg_score > 60 else "fair" if avg_score > 40 else "poor"
                ),
            }

    def get_top_proxies(self, limit: int = 10) -> List[Dict]:
        """获取评分最高的代理列表"""
        with self._lock:
            top_proxies = sorted(self.proxies, key=lambda x: x.score, reverse=True)[:limit]
            return [
                {
                    "proxy": p.proxy,
                    "score": p.score,
                    "success_rate": p.success_rate,
                    "response_time": p.response_time,
                    "protocol": p.protocol,
                    "country": p.country,
                    "source": p.source,
                    "last_checked": p.last_checked,
                }
                for p in top_proxies
            ]

    def reset_failed_proxies(self):
        """重置失败代理列表，给代理第二次机会"""
        with self._lock:
            old_count = len(self.failed_proxies)
            self.failed_proxies.clear()

            # 重置所有代理的失败计数
            for proxy in self.proxies:
                proxy.fail_count = 0

            logger.info(f"🔄 已重置 {old_count} 个失败代理，给予第二次机会")
            self._save_proxies()

    def force_refresh(self):
        """强制刷新代理池"""
        logger.info("🔄 强制刷新代理池...")
        self._fetch_fresh_proxies()
        self._check_proxy_health()
        logger.info("✅ 代理池强制刷新完成")


# 全局代理池实例
proxy_pool = ProxyPool()

# 使用示例和管理工具
if __name__ == "__main__":
    import sys

    def print_stats():
        """打印代理池统计信息"""
        stats = proxy_pool.get_stats()
        print("\n" + "=" * 50)
        print("🔍 代理池统计信息")
        print("=" * 50)
        print(f"📊 总代理数: {stats['total_proxies']}")
        print(f"✅ 可用代理: {stats['working_proxies']}")
        print(f"❌ 失败代理: {stats['failed_proxies']}")
        print(f"⭐ 高质量代理: {stats['high_quality_proxies']}")
        print(f"📈 成功率: {stats['success_rate']:.1f}%")
        print(f"⏱️ 平均响应时间: {stats['avg_response_time']}s")
        print(f"🎯 平均评分: {stats['avg_score']}")
        print(f"🏆 池质量: {stats['pool_quality']}")

        print(f"\n📡 协议分布:")
        for protocol, count in stats["protocol_distribution"].items():
            print(f"  {protocol}: {count}")

        print(f"\n🌐 来源分布:")
        for source, count in stats["source_distribution"].items():
            print(f"  {source}: {count}")

    def print_top_proxies():
        """打印最佳代理"""
        top_proxies = proxy_pool.get_top_proxies(5)
        print("\n🏆 最佳代理 TOP 5:")
        print("-" * 80)
        print(f"{'代理地址':<20} {'评分':<6} {'成功率':<8} {'响应时间':<10} {'协议':<8} {'来源':<12}")
        print("-" * 80)
        for p in top_proxies:
            print(
                f"{p['proxy']:<20} {p['score']:<6.1f} {p['success_rate']:<8.2f} "
                f"{p['response_time']:<10.2f} {p['protocol']:<8} {p['source']:<12}"
            )

    def test_proxy_functionality():
        """测试代理功能"""
        print("\n🧪 测试代理功能...")

        # 获取代理进行测试
        proxy_dict = proxy_pool.get_proxy_for_requests()
        if proxy_dict:
            print(f"✅ 获取到代理: {proxy_dict['info'].proxy}")

            # 测试请求
            try:
                response = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=10)
                if response.status_code == 200:
                    ip_data = response.json()
                    print(f"🌐 代理IP: {ip_data.get('origin', 'Unknown')}")
                else:
                    print(f"⚠️ 请求失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"❌ 代理测试失败: {e}")
        else:
            print("❌ 无可用代理")

    # 命令行工具
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "stats":
            print_stats()
        elif command == "top":
            print_top_proxies()
        elif command == "test":
            test_proxy_functionality()
        elif command == "refresh":
            proxy_pool.force_refresh()
            print("✅ 代理池已刷新")
        elif command == "reset":
            proxy_pool.reset_failed_proxies()
            print("✅ 失败代理已重置")
        elif command == "add" and len(sys.argv) > 2:
            proxy = sys.argv[2]
            protocol = sys.argv[3] if len(sys.argv) > 3 else "http"
            if proxy_pool.add_custom_proxy(proxy, protocol):
                print(f"✅ 代理 {proxy} 添加成功")
            else:
                print(f"❌ 代理 {proxy} 添加失败")
        elif command == "remove" and len(sys.argv) > 2:
            proxy = sys.argv[2]
            if proxy_pool.remove_proxy(proxy):
                print(f"✅ 代理 {proxy} 移除成功")
            else:
                print(f"❌ 代理 {proxy} 移除失败")
        else:
            print("🔧 代理池管理工具")
            print("\n可用命令:")
            print("  python proxy_pool.py stats       - 显示统计信息")
            print("  python proxy_pool.py top         - 显示最佳代理")
            print("  python proxy_pool.py test        - 测试代理功能")
            print("  python proxy_pool.py refresh     - 刷新代理池")
            print("  python proxy_pool.py reset       - 重置失败代理")
            print("  python proxy_pool.py add <proxy> [protocol] - 添加代理")
            print("  python proxy_pool.py remove <proxy> - 移除代理")
    else:
        print("🚀 代理池服务已启动")
        print_stats()
        print_top_proxies()
