#!/usr/bin/env python3
"""
监控仪表板脚本
实时监控系统性能和状态
"""

import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from monitoring.health_check import HealthChecker
import psutil


class MonitoringDashboard:
    """监控仪表板"""
    
    def __init__(self, refresh_interval=10):
        self.refresh_interval = refresh_interval
        self.running = True
        self.metrics_history = []
        self.max_history = 100  # 保留最近100条记录
        
    def start(self):
        """启动监控"""
        print("🚀 QAToolBox 监控仪表板启动")
        print("按 Ctrl+C 停止监控")
        print("=" * 80)
        
        try:
            while self.running:
                self.collect_and_display_metrics()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\n👋 监控已停止")
            self.running = False
    
    def collect_and_display_metrics(self):
        """收集并显示指标"""
        timestamp = datetime.now()
        
        # 收集系统指标
        metrics = self.collect_system_metrics()
        
        # 执行健康检查
        health_results = self.collect_health_metrics()
        
        # 组合数据
        combined_data = {
            'timestamp': timestamp.isoformat(),
            'system_metrics': metrics,
            'health_check': health_results
        }
        
        # 保存到历史记录
        self.metrics_history.append(combined_data)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
        
        # 显示仪表板
        self.display_dashboard(combined_data)
    
    def collect_system_metrics(self):
        """收集系统指标"""
        # CPU指标
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 内存指标
        memory = psutil.virtual_memory()
        
        # 磁盘指标
        disk = psutil.disk_usage('/')
        
        # 网络指标
        network = psutil.net_io_counters()
        
        # 进程指标
        processes = len(psutil.pids())
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'load_avg': list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'processes': processes
        }
    
    def collect_health_metrics(self):
        """收集健康检查指标"""
        try:
            checker = HealthChecker()
            results = checker.check_all()
            summary = checker.get_summary()
            
            return {
                'summary': summary,
                'component_status': {
                    result.component: result.status 
                    for result in results
                }
            }
        except Exception as e:
            return {
                'summary': {'overall_status': 'error'},
                'error': str(e)
            }
    
    def display_dashboard(self, data):
        """显示仪表板"""
        # 清屏
        print("\033[2J\033[H", end="")
        
        timestamp = datetime.fromisoformat(data['timestamp'])
        metrics = data['system_metrics']
        health = data['health_check']
        
        # 标题
        print("🖥️  QAToolBox 系统监控仪表板")
        print(f"📅 更新时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 健康状态概览
        self.display_health_overview(health)
        
        print()
        
        # 系统指标
        self.display_system_metrics(metrics)
        
        print()
        
        # 历史趋势
        self.display_trends()
        
        print("=" * 80)
        print(f"🔄 下次更新: {self.refresh_interval}秒后 | 按 Ctrl+C 停止监控")
    
    def display_health_overview(self, health):
        """显示健康状态概览"""
        print("🏥 系统健康状态")
        print("-" * 40)
        
        if 'summary' in health and 'overall_status' in health['summary']:
            status = health['summary']['overall_status']
            status_icons = {
                'healthy': '🟢',
                'warning': '🟡', 
                'critical': '🔴',
                'error': '⚫'
            }
            
            print(f"总体状态: {status_icons.get(status, '❓')} {status.upper()}")
            
            if 'component_status' in health:
                print("\n组件状态:")
                for component, status in health['component_status'].items():
                    icon = status_icons.get(status, '❓')
                    print(f"  {icon} {component}: {status}")
        else:
            print("❌ 健康检查失败")
    
    def display_system_metrics(self, metrics):
        """显示系统指标"""
        print("📊 系统性能指标")
        print("-" * 40)
        
        # CPU
        cpu = metrics['cpu']
        cpu_bar = self.create_progress_bar(cpu['percent'], 100)
        print(f"🔧 CPU使用率: {cpu_bar} {cpu['percent']:5.1f}%")
        print(f"   核心数: {cpu['count']} | 负载: {cpu['load_avg'][0]:.2f}")
        
        # 内存
        memory = metrics['memory']
        memory_bar = self.create_progress_bar(memory['percent'], 100)
        print(f"🧠 内存使用: {memory_bar} {memory['percent']:5.1f}%")
        print(f"   已用: {self.bytes_to_human(memory['used'])} / {self.bytes_to_human(memory['total'])}")
        
        # 磁盘
        disk = metrics['disk']
        disk_bar = self.create_progress_bar(disk['percent'], 100)
        print(f"💾 磁盘使用: {disk_bar} {disk['percent']:5.1f}%")
        print(f"   已用: {self.bytes_to_human(disk['used'])} / {self.bytes_to_human(disk['total'])}")
        
        # 网络
        network = metrics['network']
        print(f"🌐 网络流量: ↑{self.bytes_to_human(network['bytes_sent'])} ↓{self.bytes_to_human(network['bytes_recv'])}")
        
        # 进程
        print(f"⚙️  活跃进程: {metrics['processes']}")
    
    def display_trends(self):
        """显示趋势信息"""
        if len(self.metrics_history) < 2:
            return
        
        print("📈 性能趋势 (最近10分钟)")
        print("-" * 40)
        
        # 计算趋势
        recent_data = self.metrics_history[-min(60, len(self.metrics_history)):]  # 最近60个数据点
        
        cpu_values = [d['system_metrics']['cpu']['percent'] for d in recent_data]
        memory_values = [d['system_metrics']['memory']['percent'] for d in recent_data]
        
        if len(cpu_values) > 1:
            cpu_trend = "📈" if cpu_values[-1] > cpu_values[-2] else "📉" if cpu_values[-1] < cpu_values[-2] else "➡️"
            memory_trend = "📈" if memory_values[-1] > memory_values[-2] else "📉" if memory_values[-1] < memory_values[-2] else "➡️"
            
            print(f"CPU趋势: {cpu_trend} 平均: {sum(cpu_values)/len(cpu_values):.1f}% 峰值: {max(cpu_values):.1f}%")
            print(f"内存趋势: {memory_trend} 平均: {sum(memory_values)/len(memory_values):.1f}% 峰值: {max(memory_values):.1f}%")
        
        # 显示简单的ASCII图表
        self.display_ascii_chart("CPU%", cpu_values[-20:])  # 最近20个点
    
    def display_ascii_chart(self, title, values):
        """显示ASCII图表"""
        if not values:
            return
        
        print(f"\n{title} 趋势图:")
        
        # 归一化值到0-10范围
        max_val = max(values) if max(values) > 0 else 1
        normalized = [int((v / max_val) * 10) for v in values]
        
        # 绘制图表
        for row in range(10, -1, -1):
            line = f"{row * 10:3.0f}% |"
            for val in normalized:
                if val >= row:
                    line += "█"
                else:
                    line += " "
            print(line)
        
        # 底部刻度
        print("     " + "+" + "-" * len(values))
        print(f"     最新:{values[-1]:.1f}% 最高:{max(values):.1f}% 最低:{min(values):.1f}%")
    
    def create_progress_bar(self, value, max_value, width=20):
        """创建进度条"""
        percentage = value / max_value
        filled = int(width * percentage)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def bytes_to_human(self, bytes_value):
        """字节转换为人类可读格式"""
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}P"
    
    def save_metrics_to_file(self, filename=None):
        """保存指标到文件"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"metrics_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.metrics_history, f, indent=2, ensure_ascii=False)
        
        return filename


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.thresholds = {
            'cpu_critical': 90,
            'cpu_warning': 80,
            'memory_critical': 95,
            'memory_warning': 85,
            'disk_critical': 95,
            'disk_warning': 85
        }
        
        self.alert_history = []
        self.alert_cooldown = 300  # 5分钟冷却期
    
    def check_alerts(self, metrics):
        """检查告警条件"""
        alerts = []
        current_time = datetime.now()
        
        # CPU告警
        cpu_percent = metrics['system_metrics']['cpu']['percent']
        if cpu_percent >= self.thresholds['cpu_critical']:
            alerts.append({
                'level': 'critical',
                'component': 'cpu',
                'message': f'CPU使用率过高: {cpu_percent:.1f}%',
                'value': cpu_percent,
                'threshold': self.thresholds['cpu_critical']
            })
        elif cpu_percent >= self.thresholds['cpu_warning']:
            alerts.append({
                'level': 'warning', 
                'component': 'cpu',
                'message': f'CPU使用率较高: {cpu_percent:.1f}%',
                'value': cpu_percent,
                'threshold': self.thresholds['cpu_warning']
            })
        
        # 内存告警
        memory_percent = metrics['system_metrics']['memory']['percent']
        if memory_percent >= self.thresholds['memory_critical']:
            alerts.append({
                'level': 'critical',
                'component': 'memory',
                'message': f'内存使用率过高: {memory_percent:.1f}%',
                'value': memory_percent,
                'threshold': self.thresholds['memory_critical']
            })
        elif memory_percent >= self.thresholds['memory_warning']:
            alerts.append({
                'level': 'warning',
                'component': 'memory', 
                'message': f'内存使用率较高: {memory_percent:.1f}%',
                'value': memory_percent,
                'threshold': self.thresholds['memory_warning']
            })
        
        # 磁盘告警
        disk_percent = metrics['system_metrics']['disk']['percent']
        if disk_percent >= self.thresholds['disk_critical']:
            alerts.append({
                'level': 'critical',
                'component': 'disk',
                'message': f'磁盘使用率过高: {disk_percent:.1f}%',
                'value': disk_percent,
                'threshold': self.thresholds['disk_critical']
            })
        elif disk_percent >= self.thresholds['disk_warning']:
            alerts.append({
                'level': 'warning',
                'component': 'disk',
                'message': f'磁盘使用率较高: {disk_percent:.1f}%',
                'value': disk_percent,
                'threshold': self.thresholds['disk_warning']
            })
        
        # 处理告警
        for alert in alerts:
            if self.should_send_alert(alert):
                self.send_alert(alert)
                self.alert_history.append({
                    **alert,
                    'timestamp': current_time.isoformat()
                })
        
        return alerts
    
    def should_send_alert(self, alert):
        """判断是否应该发送告警"""
        # 检查冷却期
        recent_alerts = [
            a for a in self.alert_history 
            if a['component'] == alert['component'] 
            and a['level'] == alert['level']
            and datetime.fromisoformat(a['timestamp']) > 
                datetime.now() - timedelta(seconds=self.alert_cooldown)
        ]
        
        return len(recent_alerts) == 0
    
    def send_alert(self, alert):
        """发送告警"""
        print(f"\n🚨 告警: {alert['message']}")
        # 这里可以集成邮件、短信、钉钉等告警渠道
        
        # 写入日志文件
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': alert['level'],
            'component': alert['component'],
            'message': alert['message'],
            'value': alert['value'],
            'threshold': alert['threshold']
        }
        
        try:
            with open('alerts.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"写入告警日志失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QAToolBox 监控仪表板')
    parser.add_argument('--interval', '-i', type=int, default=10, 
                       help='刷新间隔(秒)，默认10秒')
    parser.add_argument('--alerts', '-a', action='store_true',
                       help='启用告警监控')
    parser.add_argument('--save', '-s', help='保存指标到文件')
    
    args = parser.parse_args()
    
    # 创建监控仪表板
    dashboard = MonitoringDashboard(refresh_interval=args.interval)
    
    # 创建告警管理器
    alert_manager = AlertManager() if args.alerts else None
    
    # 如果启用告警，在后台运行告警检查
    if alert_manager:
        def alert_worker():
            while dashboard.running:
                if dashboard.metrics_history:
                    latest_metrics = dashboard.metrics_history[-1]
                    alert_manager.check_alerts(latest_metrics)
                time.sleep(30)  # 每30秒检查一次告警
        
        alert_thread = threading.Thread(target=alert_worker, daemon=True)
        alert_thread.start()
    
    try:
        # 启动监控
        dashboard.start()
    finally:
        # 保存指标
        if args.save:
            filename = dashboard.save_metrics_to_file(args.save)
            print(f"指标已保存到: {filename}")


if __name__ == '__main__':
    main()
