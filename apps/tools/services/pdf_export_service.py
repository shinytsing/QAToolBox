#!/usr/bin/env python3
"""
PDF导出服务 - 生成旅游攻略PDF文档
"""

import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from typing import Dict, List, Any


class PDFExportService:
    """PDF导出服务"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # 副标题样式
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        
        # 章节标题样式
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.darkgreen
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        ))
        
        # 列表样式
        self.styles.add(ParagraphStyle(
            name='CustomList',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=5,
            leftIndent=20
        ))
        
        # 费用样式
        self.styles.add(ParagraphStyle(
            name='CostStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=5,
            textColor=colors.darkred
        ))
    
    def export_travel_guide_to_pdf(self, guide_data: Dict[str, Any], filename: str = None) -> bytes:
        """导出旅游攻略为PDF"""
        if not filename:
            destination = guide_data.get('destination', '旅游攻略')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{destination}旅游攻略_{timestamp}.pdf"
        
        # 创建PDF文档
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # 构建PDF内容
        story = []
        
        # 添加标题页
        story.extend(self._create_title_page(guide_data))
        story.append(PageBreak())
        
        # 添加基本信息
        story.extend(self._create_basic_info(guide_data))
        story.append(PageBreak())
        
        # 添加每日行程
        if guide_data.get('daily_schedule'):
            story.extend(self._create_daily_schedule(guide_data['daily_schedule']))
            story.append(PageBreak())
        
        # 添加费用明细
        if guide_data.get('cost_breakdown'):
            story.extend(self._create_cost_breakdown(guide_data['cost_breakdown']))
            story.append(PageBreak())
        
        # 添加景点推荐
        if guide_data.get('must_visit_attractions'):
            story.extend(self._create_attractions(guide_data['must_visit_attractions']))
            story.append(PageBreak())
        
        # 添加美食推荐
        if guide_data.get('food_recommendations'):
            story.extend(self._create_food_recommendations(guide_data['food_recommendations']))
            story.append(PageBreak())
        
        # 添加交通指南
        if guide_data.get('transportation_guide'):
            story.extend(self._create_transportation_guide(guide_data['transportation_guide']))
            story.append(PageBreak())
        
        # 添加旅行贴士
        if guide_data.get('travel_tips'):
            story.extend(self._create_travel_tips(guide_data['travel_tips']))
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_title_page(self, guide_data: Dict[str, Any]) -> List:
        """创建标题页"""
        story = []
        
        # 主标题
        destination = guide_data.get('destination', '旅游攻略')
        title = Paragraph(f"{destination} 旅游攻略", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 50))
        
        # 生成信息
        generation_info = [
            f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            f"目的地：{destination}",
            f"旅行风格：{guide_data.get('travel_style', '通用型')}",
            f"预算范围：{guide_data.get('budget_range', '舒适型')}",
            f"旅行时长：{guide_data.get('travel_duration', '3-5天')}",
        ]
        
        for info in generation_info:
            story.append(Paragraph(info, self.styles['CustomBody']))
            story.append(Spacer(1, 10))
        
        # 兴趣偏好
        interests = guide_data.get('interests', [])
        if interests:
            story.append(Spacer(1, 20))
            story.append(Paragraph("兴趣偏好：", self.styles['CustomSubtitle']))
            for interest in interests:
                story.append(Paragraph(f"• {interest}", self.styles['CustomList']))
        
        return story
    
    def _create_basic_info(self, guide_data: Dict[str, Any]) -> List:
        """创建基本信息"""
        story = []
        
        story.append(Paragraph("📋 攻略概览", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        # 最佳旅行时间
        best_time = guide_data.get('best_time_to_visit', '春秋季节')
        story.append(Paragraph(f"<b>最佳旅行时间：</b>{best_time}", self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # 天气信息
        weather_info = guide_data.get('weather_info', {})
        if weather_info:
            story.append(Paragraph("<b>天气信息：</b>", self.styles['CustomBody']))
            for season, desc in weather_info.items():
                story.append(Paragraph(f"• {season}：{desc}", self.styles['CustomList']))
            story.append(Spacer(1, 15))
        
        # 预算估算
        budget_estimate = guide_data.get('budget_estimate', {})
        if budget_estimate:
            story.append(Paragraph("<b>预算估算：</b>", self.styles['CustomBody']))
            for budget_type, amount in budget_estimate.items():
                story.append(Paragraph(f"• {budget_type}：{amount}", self.styles['CustomList']))
        
        return story
    
    def _create_daily_schedule(self, daily_schedule: List[Dict]) -> List:
        """创建每日行程"""
        story = []
        
        story.append(Paragraph("🗓️ 每日行程安排", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        for day in daily_schedule:
            # 日期标题
            day_title = f"第{day['day']}天 ({day['date']})"
            story.append(Paragraph(day_title, self.styles['SectionTitle']))
            
            # 时间段安排
            time_slots = [
                ('🌅 上午', day.get('morning', [])),
                ('☀️ 下午', day.get('afternoon', [])),
                ('🌆 傍晚', day.get('evening', [])),
                ('🌙 夜晚', day.get('night', []))
            ]
            
            for time_slot_name, activities in time_slots:
                if activities:
                    story.append(Paragraph(time_slot_name, self.styles['CustomBody']))
                    for activity in activities:
                        activity_text = f"• {activity['time']} - {activity['activity']}"
                        if activity.get('location'):
                            activity_text += f" (📍{activity['location']})"
                        if activity.get('cost'):
                            activity_text += f" (💰{activity['cost']})"
                        story.append(Paragraph(activity_text, self.styles['CustomList']))
                        
                        if activity.get('tips'):
                            story.append(Paragraph(f"   💡{activity['tips']}", self.styles['CustomList']))
            
            # 住宿信息
            if day.get('accommodation'):
                story.append(Paragraph(f"🏨 住宿：{day['accommodation']}", self.styles['CustomBody']))
            
            story.append(Spacer(1, 15))
        
        return story
    
    def _create_cost_breakdown(self, cost_breakdown: Dict) -> List:
        """创建费用明细"""
        story = []
        
        story.append(Paragraph("💰 费用明细", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        # 总费用
        total_cost = cost_breakdown.get('total_cost', 0)
        travel_days = cost_breakdown.get('travel_days', 0)
        budget_range = cost_breakdown.get('budget_range', '舒适型')
        
        story.append(Paragraph(f"<b>总费用：¥{total_cost}</b>", self.styles['CostStyle']))
        story.append(Paragraph(f"行程天数：{travel_days}天", self.styles['CustomBody']))
        story.append(Paragraph(f"预算类型：{budget_range}", self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # 费用明细表格
        cost_items = []
        cost_items.append(['费用项目', '每日费用', '总费用', '说明'])
        
        cost_categories = [
            ('accommodation', '🏨 住宿费用'),
            ('food', '🍽️ 餐饮费用'),
            ('transport', '🚗 市内交通'),
            ('attractions', '🎫 景点门票'),
            ('round_trip', '✈️ 往返交通')
        ]
        
        for category, label in cost_categories:
            if category in cost_breakdown:
                item = cost_breakdown[category]
                if category == 'round_trip':
                    cost_items.append([
                        label,
                        '-',
                        f"¥{item.get('cost', 0)}",
                        item.get('description', '')
                    ])
                else:
                    cost_items.append([
                        label,
                        f"¥{item.get('daily_cost', 0)}",
                        f"¥{item.get('total_cost', 0)}",
                        item.get('description', '')
                    ])
        
        if len(cost_items) > 1:
            table = Table(cost_items, colWidths=[2*inch, 1*inch, 1*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        return story
    
    def _create_attractions(self, attractions: List[str]) -> List:
        """创建景点推荐"""
        story = []
        
        story.append(Paragraph("🏛️ 必去景点", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        for i, attraction in enumerate(attractions, 1):
            story.append(Paragraph(f"{i}. {attraction}", self.styles['CustomBody']))
            story.append(Spacer(1, 8))
        
        return story
    
    def _create_food_recommendations(self, food_recommendations: List[str]) -> List:
        """创建美食推荐"""
        story = []
        
        story.append(Paragraph("🍜 美食推荐", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        for i, food in enumerate(food_recommendations, 1):
            story.append(Paragraph(f"{i}. {food}", self.styles['CustomBody']))
            story.append(Spacer(1, 8))
        
        return story
    
    def _create_transportation_guide(self, transportation_guide: Dict) -> List:
        """创建交通指南"""
        story = []
        
        story.append(Paragraph("🚗 交通指南", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        for transport_type, description in transportation_guide.items():
            story.append(Paragraph(f"<b>{transport_type}：</b>{description}", self.styles['CustomBody']))
            story.append(Spacer(1, 8))
        
        return story
    
    def _create_travel_tips(self, travel_tips: List[str]) -> List:
        """创建旅行贴士"""
        story = []
        
        story.append(Paragraph("💡 旅行贴士", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 20))
        
        for i, tip in enumerate(travel_tips, 1):
            story.append(Paragraph(f"{i}. {tip}", self.styles['CustomBody']))
            story.append(Spacer(1, 8))
        
        return story 