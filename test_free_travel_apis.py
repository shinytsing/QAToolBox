#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试免费旅游API连接和功能
"""

import requests
import json
import time
from typing import Dict, List

def test_duckduckgo_api():
    """测试DuckDuckGo API"""
    print("🔍 测试DuckDuckGo API...")
    
    try:
        # 测试搜索旅游信息
        query = "北京旅游攻略 景点 美食"
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ DuckDuckGo API连接成功")
            
            # 检查返回的数据
            if 'AbstractText' in data and data['AbstractText']:
                print(f"📝 获取到摘要: {data['AbstractText'][:100]}...")
            else:
                print("⚠️ 未获取到摘要信息")
            
            if 'RelatedTopics' in data and data['RelatedTopics']:
                print(f"📚 获取到{len(data['RelatedTopics'])}个相关主题")
            else:
                print("⚠️ 未获取到相关主题")
                
            return True
        else:
            print(f"❌ DuckDuckGo API连接失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ DuckDuckGo API测试失败: {str(e)}")
        return False

def test_wttr_api():
    """测试wttr.in API"""
    print("\n🌤️ 测试wttr.in API...")
    
    try:
        # 测试获取天气信息
        destination = "北京"
        url = f"https://wttr.in/{destination}?format=j1"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ wttr.in API连接成功")
            
            # 检查天气数据
            if 'current_condition' in data and data['current_condition']:
                current = data['current_condition'][0]
                temp = current.get('temp_C', 'N/A')
                weather = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
                humidity = current.get('humidity', 'N/A')
                
                print(f"🌡️ 当前温度: {temp}°C")
                print(f"☁️ 天气状况: {weather}")
                print(f"💧 湿度: {humidity}%")
                
                return True
            else:
                print("⚠️ 未获取到天气数据")
                return False
        else:
            print(f"❌ wttr.in API连接失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ wttr.in API测试失败: {str(e)}")
        return False

def test_wikipedia_api():
    """测试维基百科API"""
    print("\n📚 测试维基百科API...")
    
    try:
        # 测试获取目的地信息
        destination = "北京"
        url = f"https://zh.wikipedia.org/api/rest_v1/page/summary/{destination}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 维基百科API连接成功")
            
            # 检查返回的数据
            title = data.get('title', 'N/A')
            extract = data.get('extract', 'N/A')
            content_url = data.get('content_urls', {}).get('desktop', {}).get('page', 'N/A')
            
            print(f"📖 标题: {title}")
            print(f"📝 摘要: {extract[:100]}...")
            print(f"🔗 链接: {content_url}")
            
            return True
        else:
            print(f"❌ 维基百科API连接失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ 维基百科API测试失败: {str(e)}")
        return False

def test_travel_data_service():
    """测试旅游数据服务"""
    print("\n🤖 测试旅游数据服务...")
    
    try:
        # 导入旅游数据服务
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'apps', 'tools', 'services'))
        
        from travel_data_service import TravelDataService
        
        # 创建服务实例
        service = TravelDataService()
        
        # 测试数据抓取
        print("📡 测试数据抓取...")
        raw_data = service._数据抓取阶段("北京")
        
        if raw_data:
            print("✅ 数据抓取成功")
            
            # 检查各个数据源
            for source, data in raw_data.items():
                if data and 'error' not in data:
                    print(f"✅ {source}: 数据获取成功")
                else:
                    print(f"⚠️ {source}: 数据获取失败")
        else:
            print("❌ 数据抓取失败")
            return False
        
        # 测试信息结构化
        print("\n🔧 测试信息结构化...")
        structured_data = service._信息结构化(raw_data, "北京")
        
        if structured_data:
            print("✅ 信息结构化成功")
            print(f"🏛️ 景点数量: {len(structured_data.get('景点', []))}")
            print(f"🍜 美食数量: {len(structured_data.get('美食', []))}")
            print(f"💡 贴士数量: {len(structured_data.get('贴士', []))}")
        else:
            print("❌ 信息结构化失败")
            return False
        
        # 测试智能合成
        print("\n🤖 测试智能合成...")
        guide_data = service._智能合成阶段(
            "北京", "cultural", "medium", "3天2晚", 
            ["美食", "文化"], structured_data
        )
        
        if guide_data:
            print("✅ 智能合成成功")
            print(f"📋 攻略标题: {guide_data.get('destination', 'N/A')}")
            print(f"🏛️ 必去景点: {len(guide_data.get('must_visit_attractions', []))}")
            print(f"🍜 美食推荐: {len(guide_data.get('food_recommendations', []))}")
            print(f"💡 旅行贴士: {len(guide_data.get('travel_tips', []))}")
        else:
            print("❌ 智能合成失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 旅游数据服务测试失败: {str(e)}")
        return False

def test_opentripmap_api():
    """测试OpenTripMap API"""
    print("\n🗺️ 测试OpenTripMap API...")
    
    try:
        # 测试获取景点信息
        destination = "北京"
        geocode_url = f"https://api.opentripmap.com/0.1/zh/places/geocode"
        params = {
            'name': destination,
            'limit': 1,
            'format': 'json'
        }
        
        response = requests.get(geocode_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                print("✅ OpenTripMap API连接成功")
                location = data[0]
                print(f"📍 坐标: {location.get('lat')}, {location.get('lon')}")
                
                # 测试获取景点
                lat = location.get('lat')
                lon = location.get('lon')
                places_url = f"https://api.opentripmap.com/0.1/zh/places/radius"
                places_params = {
                    'radius': 5000,
                    'lon': lon,
                    'lat': lat,
                    'kinds': 'cultural,historic,architecture',
                    'limit': 5,
                    'format': 'json'
                }
                
                places_response = requests.get(places_url, params=places_params, timeout=10)
                if places_response.status_code == 200:
                    places_data = places_response.json()
                    features = places_data.get('features', [])
                    print(f"🏛️ 获取到{len(features)}个景点")
                    
                    for i, feature in enumerate(features[:3], 1):
                        props = feature.get('properties', {})
                        name = props.get('name', '未知景点')
                        print(f"  {i}. {name}")
                    
                    return True
                else:
                    print(f"❌ 获取景点失败 (状态码: {places_response.status_code})")
                    return False
            else:
                print("⚠️ 未获取到地理坐标")
                return False
        else:
            print(f"❌ OpenTripMap API连接失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ OpenTripMap API测试失败: {str(e)}")
        return False

def test_restcountries_api():
    """测试RestCountries API"""
    print("\n🌍 测试RestCountries API...")
    
    try:
        # 测试获取国家信息
        destination = "China"
        url = f"https://restcountries.com/v3.1/name/{destination}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                print("✅ RestCountries API连接成功")
                country = data[0]
                
                name = country.get('name', {}).get('common', 'Unknown')
                capital = country.get('capital', [''])[0] if country.get('capital') else 'N/A'
                population = country.get('population', 0)
                currencies = list(country.get('currencies', {}).keys())
                
                print(f"🏛️ 国家: {name}")
                print(f"🏛️ 首都: {capital}")
                print(f"👥 人口: {population:,}")
                print(f"💰 货币: {', '.join(currencies)}")
                
                return True
            else:
                print("⚠️ 未获取到国家信息")
                return False
        else:
            print(f"❌ RestCountries API连接失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ RestCountries API测试失败: {str(e)}")
        return False

def test_currency_api():
    """测试Currency API"""
    print("\n💱 测试Currency API...")
    
    try:
        # 测试获取汇率信息
        url = "https://api.exchangerate-api.com/v4/latest/CNY"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Currency API连接成功")
            
            base_currency = data.get('base', 'CNY')
            rates = data.get('rates', {})
            
            print(f"💰 基础货币: {base_currency}")
            print(f"📊 汇率信息:")
            
            major_currencies = ['USD', 'EUR', 'JPY', 'GBP']
            for currency in major_currencies:
                if currency in rates:
                    rate = rates[currency]
                    print(f"  {currency}: {rate:.4f}")
            
            return True
        else:
            print(f"❌ Currency API连接失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Currency API测试失败: {str(e)}")
        return False

def test_timezone_api():
    """测试Timezone API"""
    print("\n🕐 测试Timezone API...")
    
    try:
        # 测试获取时区信息
        url = "http://worldtimeapi.org/api/timezone/Asia/Shanghai"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Timezone API连接成功")
            
            timezone = data.get('timezone', 'Unknown')
            datetime_str = data.get('datetime', '')
            utc_offset = data.get('utc_offset', '')
            
            print(f"🌍 时区: {timezone}")
            print(f"🕐 当前时间: {datetime_str[:19]}")
            print(f"⏰ UTC偏移: {utc_offset}")
            
            return True
        else:
            print(f"❌ Timezone API连接失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Timezone API测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🧪 免费旅游API测试工具")
    print("=" * 50)
    
    # 测试各个API
    results = {}
    
    results['duckduckgo'] = test_duckduckgo_api()
    results['wttr'] = test_wttr_api()
    results['wikipedia'] = test_wikipedia_api()
    results['service'] = test_travel_data_service()
    results['opentripmap'] = test_opentripmap_api()
    results['restcountries'] = test_restcountries_api()
    results['currency'] = test_currency_api()
    results['timezone'] = test_timezone_api()
    
    # 总结测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    api_names = {
        'duckduckgo': 'DuckDuckGo API',
        'wttr': 'wttr.in API',
        'wikipedia': '维基百科API',
        'service': '旅游数据服务',
        'opentripmap': 'OpenTripMap API',
        'restcountries': 'RestCountries API',
        'currency': 'Currency API',
        'timezone': 'Timezone API'
    }
    
    success_count = 0
    for api, result in results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{api_names[api]}: {status}")
        if result:
            success_count += 1
    
    print(f"\n🎯 总体结果: {success_count}/{len(results)} 个API测试成功")
    
    if success_count == len(results):
        print("🎉 所有API测试通过！免费旅游功能可以正常使用。")
    elif success_count > 0:
        print("⚠️ 部分API测试失败，但基本功能仍可使用。")
    else:
        print("❌ 所有API测试失败，请检查网络连接。")

if __name__ == "__main__":
    main() 