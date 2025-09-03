import yaml
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ClashConfigManager:
    """Clash配置管理器"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
            else:
                self.config = self.get_default_config()
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            self.config = self.get_default_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'port': 7890,
            'socks-port': 7891,
            'allow-lan': False,
            'mode': 'rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            'secret': '',
            'dns': {
                'enable': True,
                'ipv6': False,
                'nameserver': ['223.5.5.5', '8.8.8.8'],
                'fallback': ['8.8.8.8', '1.1.1.1']
            },
            'proxies': [],
            'proxy-groups': [
                {
                    'name': 'PROXY',
                    'type': 'select',
                    'proxies': ['DIRECT']
                }
            ],
            'rules': [
                'DOMAIN-SUFFIX,cn,DIRECT',
                'GEOIP,CN,DIRECT',
                'MATCH,PROXY'
            ]
        }
    
    def add_proxy(self, proxy_config: Dict):
        """添加代理节点"""
        if 'proxies' not in self.config:
            self.config['proxies'] = []
        
        self.config['proxies'].append(proxy_config)
        self.update_proxy_groups()
    
    def remove_proxy(self, proxy_name: str):
        """移除代理节点"""
        if 'proxies' in self.config:
            self.config['proxies'] = [p for p in self.config['proxies'] if p.get('name') != proxy_name]
            self.update_proxy_groups()
    
    def update_proxy_groups(self):
        """更新代理组"""
        if 'proxies' not in self.config:
            return
        
        proxy_names = [p['name'] for p in self.config['proxies']]
        
        # 更新选择组
        if 'proxy-groups' in self.config:
            for group in self.config['proxy-groups']:
                if group.get('type') == 'select':
                    group['proxies'] = ['Auto'] + proxy_names
                elif group.get('type') == 'url-test':
                    group['proxies'] = proxy_names
    
    def set_rule_mode(self):
        """设置为规则模式"""
        self.config['mode'] = 'rule'
    
    def set_global_mode(self):
        """设置为全局模式"""
        self.config['mode'] = 'global'
    
    def set_direct_mode(self):
        """设置为直连模式"""
        self.config['mode'] = 'direct'
    
    def add_rule(self, rule: str):
        """添加规则"""
        if 'rules' not in self.config:
            self.config['rules'] = []
        
        if rule not in self.config['rules']:
            self.config['rules'].insert(-1, rule)  # 插入到MATCH规则之前
    
    def remove_rule(self, rule: str):
        """移除规则"""
        if 'rules' in self.config:
            self.config['rules'] = [r for r in self.config['rules'] if r != rule]
    
    def get_proxy_list(self) -> List[Dict]:
        """获取代理列表"""
        return self.config.get('proxies', [])
    
    def get_proxy_groups(self) -> List[Dict]:
        """获取代理组列表"""
        return self.config.get('proxy-groups', [])
    
    def get_rules(self) -> List[str]:
        """获取规则列表"""
        return self.config.get('rules', [])
    
    def export_config(self) -> str:
        """导出配置为YAML字符串"""
        return yaml.dump(self.config, default_flow_style=False, allow_unicode=True)
    
    def import_config(self, config_data: str):
        """导入配置"""
        try:
            self.config = yaml.safe_load(config_data)
            return True
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False
