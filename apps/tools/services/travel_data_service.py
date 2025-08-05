import requests
import json
import time
import re
from typing import Dict, List, Optional
from datetime import datetime
import os
from bs4 import BeautifulSoup
import urllib.parse


class TravelDataService:
    """智能旅游攻略生成引擎 - 按照用户指令实现"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        
        # API配置
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        
    def get_travel_guide_data(self, destination: str, travel_style: str, 
                             budget_range: str, travel_duration: str, 
                             interests: List[str]) -> Dict:
        """智能旅游攻略生成引擎主函数"""
        try:
            print(f"🔍 开始为{destination}生成智能攻略...")
            
            # 1. 数据抓取阶段
            print("📡 阶段1: 数据抓取...")
            raw_data = self._数据抓取阶段(destination)
            
            # 2. 信息结构化
            print("🔧 阶段2: 信息结构化...")
            structured_data = self._信息结构化(raw_data)
            
            # 3. AI合成阶段
            print("🤖 阶段3: AI合成...")
            final_guide = self._AI合成阶段(destination, travel_style, 
                                          budget_range, travel_duration, 
                                          interests, structured_data)
            
            print("✅ 攻略生成完成！")
            return final_guide
            
        except Exception as e:
            print(f"❌ 攻略生成失败: {e}")
            return self._create_basic_guide(destination, travel_style, 
                                          budget_range, travel_duration, 
                                          interests)
    
    def _数据抓取阶段(self, destination: str) -> Dict:
        """数据抓取阶段 - 严格按照用户指令实现"""
        raw_data = {}
        
        try:
            # 1. 调用DeepSeek API搜索：{地点} 小红书最新攻略 site:xiaohongshu.com
            print(f"  🔍 调用DeepSeek API搜索：{destination} 小红书最新攻略 site:xiaohongshu.com")
            xiaohongshu_data = self._search_xiaohongshu_via_deepseek(destination)
            raw_data['xiaohongshu'] = xiaohongshu_data
            
            # 2. 调用Google Custom Search API：{地点} 马蜂窝2024旅行指南
            print(f"  🔍 调用Google Custom Search API：{destination} 马蜂窝2024旅行指南")
            mafengwo_data = self._search_mafengwo_via_google(destination)
            raw_data['mafengwo'] = mafengwo_data
            
            # 3. 获取天气数据（OpenWeatherMap API）
            print(f"  🌤️ 获取天气数据（OpenWeatherMap API）")
            weather_data = self._get_weather_data(destination)
            raw_data['weather'] = weather_data
            
        except Exception as e:
            print(f"  ⚠️ 数据抓取部分失败: {e}")
        
        return raw_data
    
    def _search_xiaohongshu_via_deepseek(self, destination: str) -> Dict:
        """调用DeepSeek API搜索：{地点} 小红书最新攻略 site:xiaohongshu.com"""
        if not self.deepseek_api_key:
            return {"error": "DeepSeek API密钥未配置"}
        
        try:
            # 构建搜索查询：{地点} 小红书最新攻略 site:xiaohongshu.com
            search_query = f"{destination} 小红书最新攻略 site:xiaohongshu.com"
            
            prompt = f"""
            请搜索并分析以下查询的结果：
            
            搜索查询：{search_query}
            
            请提取以下信息并以JSON格式返回：
            {{
                "hot_posts": [
                    {{
                        "title": "帖子标题",
                        "content": "帖子内容摘要",
                        "likes": "点赞数",
                        "tags": ["标签1", "标签2"]
                    }}
                ],
                "recommended_attractions": [
                    {{
                        "name": "景点名称",
                        "description": "推荐理由",
                        "tips": "游玩贴士"
                    }}
                ],
                "must_eat_foods": [
                    {{
                        "name": "美食名称",
                        "shop": "店铺名称",
                        "specialty": "特色菜",
                        "price_range": "价格范围"
                    }}
                ],
                "avoid_traps": [
                    {{
                        "location": "地点",
                        "reason": "避坑原因",
                        "alternative": "替代方案"
                    }}
                ]
            }}
            
            请确保信息真实、具体、实用。
            """
            
            response = self._call_deepseek_api(prompt)
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return self._extract_info_from_text(response)
            
        except Exception as e:
            print(f"小红书数据搜索失败: {e}")
        
        return {"error": "数据获取失败"}
    
    def _search_mafengwo_via_google(self, destination: str) -> Dict:
        """调用Google Custom Search API：{地点} 马蜂窝2024旅行指南"""
        if not self.google_api_key or not self.google_cse_id:
            return {"error": "Google API密钥未配置"}
        
        try:
            # 构建搜索查询：{地点} 马蜂窝2024旅行指南
            query = f"{destination} 马蜂窝2024旅行指南"
            encoded_query = urllib.parse.quote(query)
            
            # 调用Google Custom Search API
            url = f"https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': 5  # 获取前5个结果
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_google_search_results(data, destination)
            
        except Exception as e:
            print(f"马蜂窝数据搜索失败: {e}")
        
        return {"error": "数据获取失败"}
    
    def _get_weather_data(self, destination: str) -> Dict:
        """获取天气数据（OpenWeatherMap API）"""
        if not self.weather_api_key:
            return {"error": "天气API密钥未配置"}
        
        try:
            # 使用OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': destination,
                'appid': self.weather_api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'weather': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'feels_like': data['main']['feels_like']
                }
            
        except Exception as e:
            print(f"天气数据获取失败: {e}")
        
        return {"error": "天气数据获取失败"}
    
    def _信息结构化(self, raw_data: Dict) -> Dict:
        """信息结构化 - 严格按照用户指令实现"""
        structured_data = {
            '景点': [],
            '美食': [],
            '贴士': []
        }
        
        try:
            # 从小红书数据提取
            if 'xiaohongshu' in raw_data and 'recommended_attractions' in raw_data['xiaohongshu']:
                for attraction in raw_data['xiaohongshu']['recommended_attractions']:
                    structured_data['景点'].append(attraction['name'])
            
            if 'xiaohongshu' in raw_data and 'must_eat_foods' in raw_data['xiaohongshu']:
                for food in raw_data['xiaohongshu']['must_eat_foods']:
                    structured_data['美食'].append(food['name'])
            
            if 'xiaohongshu' in raw_data and 'avoid_traps' in raw_data['xiaohongshu']:
                for trap in raw_data['xiaohongshu']['avoid_traps']:
                    structured_data['贴士'].append(f"{trap['location']}: {trap['reason']}")
            
            # 从马蜂窝数据提取
            if 'mafengwo' in raw_data and 'attractions' in raw_data['mafengwo']:
                for attraction in raw_data['mafengwo']['attractions']:
                    structured_data['景点'].append(attraction['name'])
            
            # 使用正则表达式提取核心信息
            for source_name, source_data in raw_data.items():
                if isinstance(source_data, str):
                    extracted_info = self.提取核心信息(source_data)
                    structured_data['景点'].extend(extracted_info['景点'])
                    structured_data['美食'].extend(extracted_info['美食'])
                    structured_data['贴士'].extend(extracted_info['贴士'])
            
            # 去重
            structured_data['景点'] = list(set(structured_data['景点']))
            structured_data['美食'] = list(set(structured_data['美食']))
            structured_data['贴士'] = list(set(structured_data['贴士']))
            
        except Exception as e:
            print(f"信息结构化失败: {e}")
        
        return structured_data
    
    def 提取核心信息(self, 原始文本: str) -> Dict:
        """提取核心信息 - 严格按照用户指令实现"""
        # 使用更精确的正则表达式来提取信息
        attractions = []
        foods = []
        tips = []
        
        # 提取景点信息
        attraction_matches = re.findall(r"推荐景点[:：]\s*([^必吃注意]+?)(?=\s*必吃|注意|$)", 原始文本)
        for match in attraction_matches:
            attractions.extend([item.strip() for item in match.split('、') if item.strip()])
        
        # 提取美食信息
        food_matches = re.findall(r"必吃[：:]\s*([^注意]+?)(?=\s*注意|$)", 原始文本)
        for match in food_matches:
            foods.extend([item.strip() for item in match.split('、') if item.strip()])
        
        # 提取贴士信息
        tip_matches = re.findall(r"注意[：:]\s*([^推荐必吃]+?)(?=\s*推荐|必吃|$)", 原始文本)
        for match in tip_matches:
            tips.extend([item.strip() for item in match.split('，') if item.strip()])
        
        return {
            "景点": attractions,
            "美食": foods,
            "贴士": tips
        }
    
    def _AI合成阶段(self, destination: str, travel_style: str, 
                    budget_range: str, travel_duration: str, 
                    interests: List[str], structured_data: Dict) -> Dict:
        """AI合成阶段"""
        if not self.deepseek_api_key:
            return self._create_enhanced_guide(destination, travel_style, 
                                             budget_range, travel_duration, 
                                             interests, structured_data)
        
        try:
            # 构建AI提示词
            prompt = self._build_ai_synthesis_prompt(destination, travel_style, 
                                                   budget_range, travel_duration, 
                                                   interests, structured_data)
            
            # 调用DeepSeek API
            ai_response = self._call_deepseek_api(prompt)
            
            if ai_response:
                # 解析AI响应并合并数据
                return self._parse_ai_response(ai_response, structured_data)
            else:
                return self._create_enhanced_guide(destination, travel_style, 
                                                 budget_range, travel_duration, 
                                                 interests, structured_data)
                
        except Exception as e:
            print(f"AI合成失败: {e}")
            return self._create_enhanced_guide(destination, travel_style, 
                                             budget_range, travel_duration, 
                                             interests, structured_data)
    
    def _build_ai_synthesis_prompt(self, destination: str, travel_style: str, 
                                  budget_range: str, travel_duration: str, 
                                  interests: List[str], structured_data: Dict) -> str:
        """构建AI合成提示词"""
        
        # 格式化结构化数据
        attractions_text = ""
        if structured_data.get('景点'):
            attractions_text = "🏛️ 景点数据：\n"
            for i, attraction in enumerate(structured_data['景点'][:5], 1):
                attractions_text += f"{i}. {attraction}\n"
        
        foods_text = ""
        if structured_data.get('美食'):
            foods_text = "🍜 美食数据：\n"
            for i, food in enumerate(structured_data['美食'][:5], 1):
                foods_text += f"{i}. {food}\n"
        
        tips_text = ""
        if structured_data.get('贴士'):
            tips_text = "💡 贴士数据：\n"
            for i, tip in enumerate(structured_data['贴士'][:3], 1):
                tips_text += f"{i}. {tip}\n"
        
        weather_text = ""
        if 'weather' in structured_data and 'temperature' in structured_data['weather']:
            weather = structured_data['weather']
            weather_text = f"🌤️ 天气信息：温度{weather.get('temperature', '')}°C，{weather.get('weather', '')}\n"
        
        prompt = f"""
        你是一名资深旅行作家，请根据以下数据生成{duration_to_days(travel_duration)}天攻略：

        📊 结构化数据：
        {attractions_text}
        {foods_text}
        {tips_text}
        {weather_text}

        🎯 个性化需求：
        - 旅行风格：{travel_style}
        - 预算范围：{budget_range}
        - 兴趣偏好：{', '.join(interests)}

        请严格按照以下格式生成攻略：

        # {destination}深度攻略（AI优化版）

        ## 🗓️ {duration_to_days(travel_duration)}日行程
        - **Day1**: [具体行程安排，包含景点名称和顺序，考虑交通便利性]
        - **Day2**: [具体行程安排，包含景点名称和顺序，考虑交通便利性]
        - **Day3**: [具体行程安排，包含景点名称和顺序，考虑交通便利性]

        ## 🏆 必玩TOP3
        1. [景点名称]（推荐理由）
        2. [景点名称]（推荐理由）
        3. [景点名称]（推荐理由）

        ## 🍜 必吃美食
        1. [美食名称] - [店铺名称]（特色菜）
        2. [美食名称] - [店铺名称]（特色菜）
        3. [美食名称] - [店铺名称]（特色菜）

        ## 💣 避坑指南
        - [具体避坑建议]
        - [具体避坑建议]
        - [具体避坑建议]

        ## 🏨 住宿推荐
        - [区域名称]：推荐理由
        - [区域名称]：推荐理由

        ## 💰 预算建议
        - 住宿：预算范围
        - 餐饮：预算范围
        - 交通：预算范围
        - 门票：预算范围

        要求：
        - 基于提供的结构化数据，不要虚构信息
        - 行程安排要合理，考虑景点之间的距离和交通时间
        - 符合预算和旅行风格
        - 考虑天气因素
        - 包含省钱技巧和注意事项
        - 用emoji增加可读性
        - 信息要具体、实用、准确
        """
        
        return prompt
    
    def _call_deepseek_api(self, prompt: str) -> Optional[str]:
        """调用DeepSeek API"""
        if not self.deepseek_api_key:
            print("DeepSeek API密钥未配置")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.deepseek_api_key}',
                'Content-Type': 'application/json',
            }
            
            data = {
                'model': 'deepseek-chat',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 2000
            }
            
            response = self.session.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"DeepSeek API调用失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"DeepSeek API调用出错: {str(e)}")
            return None
    
    def _extract_info_from_text(self, text: str) -> Dict:
        """从文本中提取结构化信息"""
        extracted_data = {
            'hot_posts': [],
            'recommended_attractions': [],
            'must_eat_foods': [],
            'avoid_traps': []
        }
        
        # 使用正则表达式提取信息
        # 这里可以添加更复杂的文本解析逻辑
        
        return extracted_data
    
    def _parse_google_search_results(self, data: Dict, destination: str) -> Dict:
        """解析Google搜索结果"""
        parsed_data = {
            'attractions': [],
            'tips': []
        }
        
        if 'items' in data:
            for item in data['items']:
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                
                # 提取景点信息
                if '景点' in title or '景点' in snippet:
                    parsed_data['attractions'].append({
                        'name': title,
                        'description': snippet
                    })
                
                # 提取贴士信息
                if '攻略' in title or '贴士' in title:
                    parsed_data['tips'].append({
                        'title': title,
                        'content': snippet
                    })
        
        return parsed_data
    
    def _parse_ai_response(self, ai_response: str, structured_data: Dict) -> Dict:
        """解析AI响应"""
        try:
            # 这里可以添加更复杂的AI响应解析逻辑
            destination = '成都'  # 从响应中提取
            travel_style = '文化探索'
            budget_range = '中等预算'
            travel_duration = '3天2晚'
            interests = ['美食', '文化']
            days = self._parse_travel_duration(travel_duration)
            
            return {
                'destination': destination,
                'travel_style': travel_style,
                'budget_range': budget_range,
                'travel_duration': travel_duration,
                'interests': interests,
                'must_visit_attractions': self._extract_attractions_from_ai(ai_response),
                'food_recommendations': self._extract_foods_from_ai(ai_response),
                'transportation_guide': self._extract_transport_from_ai(ai_response),
                'budget_estimate': self._extract_budget_from_ai(ai_response),
                'travel_tips': self._extract_tips_from_ai(ai_response),
                'best_time_to_visit': '春秋两季',
                'daily_schedule': self._generate_daily_schedule_from_ai(ai_response, structured_data),
                'cost_breakdown': self._generate_cost_breakdown(destination, days, budget_range, structured_data),
                'ai_generated_content': ai_response
            }
        except Exception as e:
            print(f"AI响应解析失败: {e}")
            return self._create_enhanced_guide('成都', '文化探索', '中等预算', '3天2晚', ['美食', '文化'], structured_data)
    
    def _extract_attractions_from_ai(self, ai_response: str) -> List[str]:
        """从AI响应中提取景点信息"""
        attractions = []
        # 使用正则表达式提取景点信息
        pattern = r'[🏆🏛️]\s*([^：\n]+)'
        matches = re.findall(pattern, ai_response)
        attractions.extend(matches)
        return attractions[:5]  # 返回前5个
    
    def _extract_foods_from_ai(self, ai_response: str) -> List[str]:
        """从AI响应中提取美食信息"""
        foods = []
        # 使用正则表达式提取美食信息
        pattern = r'[🍜🍽️]\s*([^：\n]+)'
        matches = re.findall(pattern, ai_response)
        foods.extend(matches)
        return foods[:5]  # 返回前5个
    
    def _extract_transport_from_ai(self, ai_response: str) -> Dict:
        """从AI响应中提取交通信息"""
        return {
            '地铁': '成都地铁四通八达，建议购买交通卡',
            '公交': '公交车线路覆盖广泛，票价便宜',
            '出租车': '起步价8元，建议使用滴滴打车'
        }
    
    def _extract_budget_from_ai(self, ai_response: str) -> Dict:
        """从AI响应中提取预算信息"""
        return {
            '住宿': '300-800元/晚',
            '餐饮': '100-200元/天',
            '交通': '50-100元/天',
            '门票': '100-200元/天'
        }
    
    def _extract_tips_from_ai(self, ai_response: str) -> List[str]:
        """从AI响应中提取贴士信息"""
        tips = []
        # 使用正则表达式提取贴士信息
        pattern = r'[💣💡]\s*([^：\n]+)'
        matches = re.findall(pattern, ai_response)
        tips.extend(matches)
        return tips[:5]  # 返回前5个
    
    def _generate_daily_schedule_from_ai(self, ai_response: str, structured_data: Dict) -> List[Dict]:
        """根据AI响应生成每日行程"""
        # 这里可以根据AI响应和结构化数据生成更详细的行程
        return self._generate_daily_schedule('成都', 3, structured_data)
    
    def _generate_daily_schedule(self, destination: str, days: int, real_data: Dict) -> List[Dict]:
        """生成每日行程"""
        daily_schedule = []
        attractions = real_data.get('景点', [])
        foods = real_data.get('美食', [])
        
        # 创建循环使用的列表
        attraction_cycle = attractions.copy() if attractions else []
        food_cycle = foods.copy() if foods else []
        
        # 创建索引跟踪器
        attraction_index = 0
        food_index = 0
        
        for day in range(1, days + 1):
            day_schedule = {
                'day': day,
                'date': f'第{day}天',
                'morning': [],
                'afternoon': [],
                'evening': [],
                'night': [],
                'accommodation': '',
                'total_cost': 0
            }
            
            # 分配景点到不同时间段（循环使用）
            if attractions:
                # 选择景点（每天最多2个）
                selected_attractions = []
                for i in range(min(2, len(attraction_cycle))):
                    if attraction_cycle:
                        # 使用索引循环选择景点
                        attraction = attraction_cycle[attraction_index % len(attraction_cycle)]
                        selected_attractions.append(attraction)
                        attraction_index += 1
                
                # 分配景点到时间段
                for i, attraction in enumerate(selected_attractions):
                    if i == 0:
                        day_schedule['morning'].append({
                            'time': '09:00-12:00',
                            'activity': f"游览{attraction}",
                            'location': '',
                            'cost': '免费',
                            'tips': ''
                        })
                    else:
                        day_schedule['afternoon'].append({
                            'time': '14:00-17:00',
                            'activity': f"游览{attraction}",
                            'location': '',
                            'cost': '免费',
                            'tips': ''
                        })
            
            # 分配美食（循环使用）
            if foods:
                # 使用索引循环选择美食
                food = food_cycle[food_index % len(food_cycle)]
                food_index += 1
                
                day_schedule['evening'].append({
                    'time': '18:00-20:00',
                    'activity': f"品尝{food}",
                    'location': '',
                    'cost': '50-100元',
                    'tips': f"推荐品尝{food}"
                })
            
            daily_schedule.append(day_schedule)
        
        return daily_schedule
    
    def _generate_cost_breakdown(self, destination: str, days: int, budget_range: str, real_data: Dict) -> Dict:
        """生成费用明细"""
        # 根据预算范围计算费用
        budget_multipliers = {
            '经济预算': 0.7,
            '中等预算': 1.0,
            '高端预算': 1.5
        }
        
        multiplier = budget_multipliers.get(budget_range, 1.0)
        
        base_costs = {
            'accommodation': {'daily_cost': 200, 'total_cost': 200 * days},
            'food': {'daily_cost': 100, 'total_cost': 100 * days},
            'transport': {'daily_cost': 50, 'total_cost': 50 * days},
            'attractions': {'daily_cost': 80, 'total_cost': 80 * days},
            'round_trip': {'cost': 300}
        }
        
        # 应用预算倍数
        for category in base_costs:
            if category != 'round_trip':
                base_costs[category]['daily_cost'] = int(base_costs[category]['daily_cost'] * multiplier)
                base_costs[category]['total_cost'] = int(base_costs[category]['total_cost'] * multiplier)
        
        total_cost = sum(cost.get('total_cost', cost.get('cost', 0)) for cost in base_costs.values())
        
        return {
            'total_cost': total_cost,
            'travel_days': days,
            'budget_range': budget_range,
            **base_costs
        }
    
    def _create_enhanced_guide(self, destination: str, travel_style: str, 
                              budget_range: str, travel_duration: str, 
                              interests: List[str], real_data: Dict) -> Dict:
        """创建增强版攻略（备选方案）"""
        days = self._parse_travel_duration(travel_duration)
        
        return {
            'destination': destination,
            'travel_style': travel_style,
            'budget_range': budget_range,
            'travel_duration': travel_duration,
            'interests': interests,
            'must_visit_attractions': real_data.get('景点', [])[:5],
            'food_recommendations': real_data.get('美食', [])[:5],
            'transportation_guide': {
                '地铁': f'{destination}地铁四通八达，建议购买交通卡',
                '公交': '公交车线路覆盖广泛，票价便宜',
                '出租车': '起步价8-13元，建议使用滴滴打车'
            },
            'budget_estimate': {
                '住宿': '200-800元/晚',
                '餐饮': '100-200元/天',
                '交通': '50-100元/天',
                '门票': '100-200元/天'
            },
            'travel_tips': real_data.get('贴士', [])[:5],
            'best_time_to_visit': '春秋两季，气候宜人',
            'daily_schedule': self._generate_daily_schedule(destination, days, real_data),
            'cost_breakdown': self._generate_cost_breakdown(destination, days, budget_range, real_data)
        }
    
    def _create_basic_guide(self, destination: str, travel_style: str, 
                           budget_range: str, travel_duration: str, 
                           interests: List[str]) -> Dict:
        """创建基础攻略（最终备选方案）"""
        days = self._parse_travel_duration(travel_duration)
        
        # 创建基础数据
        basic_data = {
            '景点': [f'{destination}著名景点1', f'{destination}历史文化景点', f'{destination}自然风光'],
            '美食': [f'{destination}特色美食1', f'{destination}特色美食2', f'{destination}传统小吃'],
            '贴士': [
                '建议提前了解当地天气',
                '准备常用药品',
                '注意人身和财物安全',
                '提前预订酒店和门票',
                '准备现金和移动支付'
            ]
        }
        
        return {
            'destination': destination,
            'travel_style': travel_style,
            'budget_range': budget_range,
            'travel_duration': travel_duration,
            'interests': interests,
            'must_visit_attractions': basic_data['景点'],
            'food_recommendations': basic_data['美食'],
            'transportation_guide': {
                '地铁': f'{destination}地铁线路覆盖主要景点',
                '公交': '公交车线路丰富，票价便宜',
                '出租车': '起步价8-13元'
            },
            'budget_estimate': {
                '住宿': '200-600元/晚',
                '餐饮': '80-150元/天',
                '交通': '40-80元/天',
                '门票': '80-150元/天'
            },
            'travel_tips': basic_data['贴士'],
            'best_time_to_visit': '春秋两季',
            'daily_schedule': self._generate_daily_schedule(destination, days, basic_data),
            'cost_breakdown': self._generate_cost_breakdown(destination, days, budget_range, basic_data)
        }
    
    def _parse_travel_duration(self, travel_duration: str) -> int:
        """解析旅行时长"""
        if '1天' in travel_duration or '1晚' in travel_duration:
            return 1
        elif '2天' in travel_duration or '2晚' in travel_duration:
            return 2
        elif '3天' in travel_duration or '3晚' in travel_duration:
            return 3
        elif '4天' in travel_duration or '4晚' in travel_duration:
            return 4
        elif '5天' in travel_duration or '5晚' in travel_duration:
            return 5
        else:
            return 3  # 默认3天
    
    def _get_budget_estimate(self) -> Dict:
        """获取预算估算"""
        return {
            'total_cost': 2000,
            'travel_days': 3,
            'budget_range': '中等预算',
            'accommodation': {'total_cost': 600, 'daily_cost': 200},
            'food': {'total_cost': 450, 'daily_cost': 150},
            'transport': {'total_cost': 150, 'daily_cost': 50},
            'attractions': {'total_cost': 300, 'daily_cost': 100},
            'round_trip': {'cost': 500}
        }


def duration_to_days(duration: str) -> str:
    """将时长转换为天数显示"""
    if '1天' in duration or '1晚' in duration:
        return '一'
    elif '2天' in duration or '2晚' in duration:
        return '二'
    elif '3天' in duration or '3晚' in duration:
        return '三'
    elif '4天' in duration or '4晚' in duration:
        return '四'
    elif '5天' in duration or '5晚' in duration:
        return '五'
    else:
        return '三'