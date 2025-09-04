import json
import logging
import socket
import subprocess
import time
from typing import Dict, List, Optional

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import requests

logger = logging.getLogger(__name__)


class IPDefenseSystem:
    """IP攻击防御系统"""

    def __init__(self):
        self.attack_log = []
        self.blocked_ips = set()
        self.whitelist_ips = set()

    def analyze_ip(self, ip: str) -> Dict:
        """分析IP地址信息"""
        try:
            # 获取IP地理位置信息
            geo_info = self._get_ip_geo_info(ip)

            # 检查是否为已知恶意IP
            threat_info = self._check_threat_intelligence(ip)

            # 检查IP类型
            ip_type = self._classify_ip(ip)

            return {
                "ip": ip,
                "geo_info": geo_info,
                "threat_info": threat_info,
                "ip_type": ip_type,
                "risk_level": self._calculate_risk_level(geo_info, threat_info, ip_type),
                "timestamp": time.time(),
            }
        except Exception as e:
            logger.error(f"IP分析失败: {ip}, 错误: {str(e)}")
            return {"ip": ip, "error": str(e), "timestamp": time.time()}

    def _get_ip_geo_info(self, ip: str) -> Dict:
        """获取IP地理位置信息"""
        try:
            # 使用免费IP地理位置API
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "country": data.get("country", ""),
                    "region": data.get("regionName", ""),
                    "city": data.get("city", ""),
                    "isp": data.get("isp", ""),
                    "org": data.get("org", ""),
                    "timezone": data.get("timezone", ""),
                    "lat": data.get("lat", ""),
                    "lon": data.get("lon", ""),
                }
        except:
            pass

        return {}

    def _check_threat_intelligence(self, ip: str) -> Dict:
        """检查威胁情报"""
        # 这里可以集成多个威胁情报源
        # 目前使用简单的检查逻辑

        # 检查是否为私有IP
        if self._is_private_ip(ip):
            return {"is_private": True, "risk": "low"}

        # 检查是否为已知攻击IP
        blacklisted_ips = getattr(settings, "BLACKLISTED_IPS", [])
        if ip in blacklisted_ips:
            return {"is_blacklisted": True, "risk": "high"}

        return {"risk": "unknown"}

    def _is_private_ip(self, ip: str) -> bool:
        """检查是否为私有IP"""
        private_ranges = [
            ("10.0.0.0", "10.255.255.255"),
            ("172.16.0.0", "172.31.255.255"),
            ("192.168.0.0", "192.168.255.255"),
            ("127.0.0.0", "127.255.255.255"),
        ]

        try:
            ip_int = self._ip_to_int(ip)
            for start_ip, end_ip in private_ranges:
                start_int = self._ip_to_int(start_ip)
                end_int = self._ip_to_int(end_ip)
                if start_int <= ip_int <= end_int:
                    return True
        except:
            pass

        return False

    def _ip_to_int(self, ip: str) -> int:
        """将IP地址转换为整数"""
        parts = ip.split(".")
        return int(parts[0]) << 24 | int(parts[1]) << 16 | int(parts[2]) << 8 | int(parts[3])

    def _classify_ip(self, ip: str) -> str:
        """分类IP类型"""
        if self._is_private_ip(ip):
            return "private"
        elif ip == "127.0.0.1" or ip == "::1":
            return "localhost"
        else:
            return "public"

    def _calculate_risk_level(self, geo_info: Dict, threat_info: Dict, ip_type: str) -> str:
        """计算风险等级"""
        risk_score = 0

        # 基于地理位置的风险评估
        if geo_info.get("country") in ["CN", "RU", "KP"]:  # 高风险国家
            risk_score += 3
        elif geo_info.get("country") in ["US", "GB", "DE"]:  # 中等风险国家
            risk_score += 1

        # 基于威胁情报的风险评估
        if threat_info.get("is_blacklisted"):
            risk_score += 5
        elif threat_info.get("is_private"):
            risk_score -= 2

        # 基于IP类型的风险评估
        if ip_type == "private":
            risk_score -= 3
        elif ip_type == "localhost":
            risk_score -= 5

        # 确定风险等级
        if risk_score >= 5:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"

    def block_ip(self, ip: str, reason: str = "") -> bool:
        """封禁IP地址"""
        try:
            # 添加到黑名单
            self.blocked_ips.add(ip)

            # 记录封禁日志
            self.attack_log.append({"ip": ip, "action": "blocked", "reason": reason, "timestamp": time.time()})

            # 尝试系统级封禁（需要root权限）
            self._system_block_ip(ip)

            logger.warning(f"IP已封禁: {ip}, 原因: {reason}")
            return True

        except Exception as e:
            logger.error(f"IP封禁失败: {ip}, 错误: {str(e)}")
            return False

    def _system_block_ip(self, ip: str):
        """系统级IP封禁"""
        try:
            # 使用iptables封禁IP（Linux系统）
            subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True, capture_output=True)
            logger.info(f"系统级封禁IP: {ip}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 如果iptables不可用，尝试使用ufw
            try:
                subprocess.run(["ufw", "deny", "from", ip], check=True, capture_output=True)
                logger.info(f"UFW封禁IP: {ip}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning(f"无法进行系统级封禁: {ip}")

    def unblock_ip(self, ip: str) -> bool:
        """解封IP地址"""
        try:
            # 从黑名单移除
            self.blocked_ips.discard(ip)

            # 记录解封日志
            self.attack_log.append({"ip": ip, "action": "unblocked", "timestamp": time.time()})

            # 尝试系统级解封
            self._system_unblock_ip(ip)

            logger.info(f"IP已解封: {ip}")
            return True

        except Exception as e:
            logger.error(f"IP解封失败: {ip}, 错误: {str(e)}")
            return False

    def _system_unblock_ip(self, ip: str):
        """系统级IP解封"""
        try:
            # 使用iptables解封IP
            subprocess.run(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], check=True, capture_output=True)
            logger.info(f"系统级解封IP: {ip}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(["ufw", "allow", "from", ip], check=True, capture_output=True)
                logger.info(f"UFW解封IP: {ip}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning(f"无法进行系统级解封: {ip}")

    def get_attack_log(self, limit: int = 100) -> List[Dict]:
        """获取攻击日志"""
        return sorted(self.attack_log, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_blocked_ips(self) -> List[str]:
        """获取被封禁的IP列表"""
        return list(self.blocked_ips)

    def add_to_whitelist(self, ip: str) -> bool:
        """添加IP到白名单"""
        try:
            self.whitelist_ips.add(ip)
            logger.info(f"IP已添加到白名单: {ip}")
            return True
        except Exception as e:
            logger.error(f"添加白名单失败: {ip}, 错误: {str(e)}")
            return False

    def remove_from_whitelist(self, ip: str) -> bool:
        """从白名单移除IP"""
        try:
            self.whitelist_ips.discard(ip)
            logger.info(f"IP已从白名单移除: {ip}")
            return True
        except Exception as e:
            logger.error(f"移除白名单失败: {ip}, 错误: {str(e)}")
            return False

    def get_whitelist_ips(self) -> List[str]:
        """获取白名单IP列表"""
        return list(self.whitelist_ips)


# 全局防御系统实例
ip_defense = IPDefenseSystem()


@login_required
def ip_defense_dashboard(request):
    """IP防御系统仪表板"""
    context = {
        "blocked_ips": ip_defense.get_blocked_ips(),
        "whitelist_ips": ip_defense.get_whitelist_ips(),
        "attack_log": ip_defense.get_attack_log(50),
    }
    return render(request, "tools/ip_defense_dashboard.html", context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def analyze_ip_api(request):
    """分析IP地址API"""
    try:
        data = json.loads(request.body)
        ip = data.get("ip", "")

        if not ip:
            return JsonResponse({"success": False, "error": "请提供要分析的IP地址"})

        # 分析IP
        analysis = ip_defense.analyze_ip(ip)

        return JsonResponse({"success": True, "data": analysis})

    except Exception as e:
        logger.error(f"IP分析API错误: {str(e)}")
        return JsonResponse({"success": False, "error": f"IP分析失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def block_ip_api(request):
    """封禁IP地址API"""
    try:
        data = json.loads(request.body)
        ip = data.get("ip", "")
        reason = data.get("reason", "")

        if not ip:
            return JsonResponse({"success": False, "error": "请提供要封禁的IP地址"})

        # 封禁IP
        success = ip_defense.block_ip(ip, reason)

        return JsonResponse({"success": success, "message": "IP封禁成功" if success else "IP封禁失败"})

    except Exception as e:
        logger.error(f"IP封禁API错误: {str(e)}")
        return JsonResponse({"success": False, "error": f"IP封禁失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def unblock_ip_api(request):
    """解封IP地址API"""
    try:
        data = json.loads(request.body)
        ip = data.get("ip", "")

        if not ip:
            return JsonResponse({"success": False, "error": "请提供要解封的IP地址"})

        # 解封IP
        success = ip_defense.unblock_ip(ip)

        return JsonResponse({"success": success, "message": "IP解封成功" if success else "IP解封失败"})

    except Exception as e:
        logger.error(f"IP解封API错误: {str(e)}")
        return JsonResponse({"success": False, "error": f"IP解封失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_attack_log_api(request):
    """获取攻击日志API"""
    try:
        limit = int(request.GET.get("limit", 100))
        attack_log = ip_defense.get_attack_log(limit)

        return JsonResponse({"success": True, "data": {"attack_log": attack_log, "total_count": len(attack_log)}})

    except Exception as e:
        logger.error(f"获取攻击日志API错误: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取攻击日志失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_ip_lists_api(request):
    """获取IP列表API"""
    try:
        return JsonResponse(
            {
                "success": True,
                "data": {
                    "blocked_ips": ip_defense.get_blocked_ips(),
                    "whitelist_ips": ip_defense.get_whitelist_ips(),
                    "blacklisted_ips": getattr(settings, "BLACKLISTED_IPS", []),
                },
            }
        )

    except Exception as e:
        logger.error(f"获取IP列表API错误: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取IP列表失败: {str(e)}"})
