import json

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.tools.models.legacy_models import TrainingPlan


class Command(BaseCommand):
    help = "为训练模式创建默认动作设置"

    def handle(self, *args, **options):
        self.stdout.write("开始创建默认训练模式动作设置...")

        # 创建各种训练模式的默认设置
        self.create_five_day_split()
        self.create_three_day_split()
        self.create_push_pull_legs()
        self.create_cardio_program()
        self.create_functional_training()

        self.stdout.write(self.style.SUCCESS("默认训练模式创建完成！"))

    def create_five_day_split(self):
        """创建五分化训练模式"""
        plan_data = {
            "name": "经典五分化力量训练",
            "description": "适合中高级训练者的经典五分化训练计划，每天专注一个身体部位",
            "plan_type": "hypertrophy",
            "duration_weeks": 8,
            "difficulty": "intermediate",
            "primary_goals": ["增肌", "力量提升"],
            "visibility": "template",
            "week_schedule": [
                {
                    "weekday": "周一",
                    "body_parts": ["胸部"],
                    "focus": "胸部专项训练",
                    "modules": {
                        "warmup": [
                            {"name": "动态拉伸", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "轻重量杠铃卧推", "sets": 2, "reps": 15, "weight": "空杆", "rest": "60秒"},
                            {"name": "俯卧撑", "sets": 2, "reps": 10, "weight": "自重", "rest": "30秒"},
                        ],
                        "main": [
                            {"name": "杠铃卧推", "sets": 4, "reps": "6-8", "weight": "体重×1.2倍", "rest": "3分钟"},
                            {"name": "哑铃卧推", "sets": 3, "reps": "8-10", "weight": "30kg", "rest": "90秒"},
                            {"name": "上斜哑铃推举", "sets": 3, "reps": "10-12", "weight": "25kg", "rest": "90秒"},
                            {"name": "双杠臂屈伸", "sets": 3, "reps": "8-12", "weight": "自重+10kg", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "哑铃飞鸟", "sets": 3, "reps": "12-15", "weight": "15kg", "rest": "60秒"},
                            {"name": "绳索夹胸", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "俯卧撑（钻石式）", "sets": 2, "reps": "至力竭", "weight": "自重", "rest": "60秒"},
                        ],
                        "cooldown": [
                            {"name": "胸部拉伸", "sets": 1, "reps": "3分钟", "weight": "", "rest": ""},
                            {"name": "肩部放松", "sets": 1, "reps": "2分钟", "weight": "", "rest": ""},
                        ],
                    },
                },
                {
                    "weekday": "周二",
                    "body_parts": ["背部"],
                    "focus": "背部专项训练",
                    "modules": {
                        "warmup": [
                            {"name": "肩胛激活", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "轻重量高位下拉", "sets": 2, "reps": 15, "weight": "轻重量", "rest": "60秒"},
                            {"name": "反向飞鸟", "sets": 2, "reps": 12, "weight": "5kg", "rest": "30秒"},
                        ],
                        "main": [
                            {"name": "引体向上", "sets": 4, "reps": "6-10", "weight": "自重", "rest": "3分钟"},
                            {"name": "杠铃划船", "sets": 4, "reps": "8-10", "weight": "60kg", "rest": "2分钟"},
                            {"name": "高位下拉", "sets": 3, "reps": "10-12", "weight": "适中", "rest": "90秒"},
                            {"name": "坐姿绳索划船", "sets": 3, "reps": "10-12", "weight": "适中", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "单臂哑铃划船", "sets": 3, "reps": "12-15", "weight": "25kg", "rest": "60秒"},
                            {"name": "面拉", "sets": 3, "reps": "15-20", "weight": "轻重量", "rest": "60秒"},
                            {"name": "直臂下拉", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                        ],
                        "cooldown": [
                            {"name": "背部拉伸", "sets": 1, "reps": "3分钟", "weight": "", "rest": ""},
                            {"name": "肩胛放松", "sets": 1, "reps": "2分钟", "weight": "", "rest": ""},
                        ],
                    },
                },
                {
                    "weekday": "周三",
                    "body_parts": ["休息"],
                    "focus": "主动恢复或轻度有氧",
                    "modules": {
                        "main": [
                            {"name": "轻松散步", "sets": 1, "reps": "20-30分钟", "weight": "", "rest": ""},
                            {"name": "全身拉伸", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""},
                            {"name": "泡沫轴放松", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""},
                        ]
                    },
                },
                {
                    "weekday": "周四",
                    "body_parts": ["肩部"],
                    "focus": "肩部专项训练",
                    "modules": {
                        "warmup": [
                            {"name": "肩部环绕", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "轻重量侧平举", "sets": 2, "reps": 15, "weight": "5kg", "rest": "30秒"},
                            {"name": "弹力带外旋", "sets": 2, "reps": 15, "weight": "轻阻力", "rest": "30秒"},
                        ],
                        "main": [
                            {"name": "坐姿哑铃推举", "sets": 4, "reps": "8-10", "weight": "25kg", "rest": "2分钟"},
                            {"name": "杠铃推举", "sets": 3, "reps": "8-10", "weight": "40kg", "rest": "2分钟"},
                            {"name": "哑铃侧平举", "sets": 4, "reps": "12-15", "weight": "12kg", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "哑铃前平举", "sets": 3, "reps": "12-15", "weight": "10kg", "rest": "60秒"},
                            {"name": "哑铃后束飞鸟", "sets": 4, "reps": "15-20", "weight": "8kg", "rest": "60秒"},
                            {"name": "耸肩", "sets": 3, "reps": "15-20", "weight": "30kg", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "肩部拉伸", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周五",
                    "body_parts": ["腿部"],
                    "focus": "腿部专项训练",
                    "modules": {
                        "warmup": [
                            {"name": "腿部动态热身", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""},
                            {"name": "高脚杯深蹲", "sets": 2, "reps": 15, "weight": "15kg", "rest": "60秒"},
                            {"name": "腿部摆动", "sets": 2, "reps": "15次/腿", "weight": "", "rest": "30秒"},
                        ],
                        "main": [
                            {"name": "杠铃深蹲", "sets": 4, "reps": "6-8", "weight": "体重×1.5倍", "rest": "3分钟"},
                            {"name": "罗马尼亚硬拉", "sets": 3, "reps": "8-10", "weight": "体重×1.2倍", "rest": "2分钟"},
                            {"name": "腿举", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "90秒"},
                            {"name": "保加利亚分腿蹲", "sets": 3, "reps": "12次/腿", "weight": "20kg", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "腿弯举", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "腿伸展", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "小腿提踵", "sets": 4, "reps": "15-20", "weight": "适中", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "腿部拉伸", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周六",
                    "body_parts": ["手臂"],
                    "focus": "手臂专项训练",
                    "modules": {
                        "warmup": [
                            {"name": "手臂环绕", "sets": 1, "reps": "3分钟", "weight": "", "rest": ""},
                            {"name": "轻重量弯举", "sets": 2, "reps": 15, "weight": "5kg", "rest": "30秒"},
                            {"name": "绳索下拉热身", "sets": 2, "reps": 15, "weight": "轻重量", "rest": "30秒"},
                        ],
                        "main": [
                            {"name": "杠铃弯举", "sets": 4, "reps": "8-12", "weight": "30kg", "rest": "90秒"},
                            {"name": "三头肌下拉", "sets": 4, "reps": "8-12", "weight": "适中", "rest": "90秒"},
                            {"name": "哑铃弯举", "sets": 3, "reps": "10-12", "weight": "15kg", "rest": "75秒"},
                            {"name": "仰卧臂屈伸", "sets": 3, "reps": "10-12", "weight": "20kg", "rest": "75秒"},
                        ],
                        "accessory": [
                            {"name": "锤式弯举", "sets": 3, "reps": "12-15", "weight": "12kg", "rest": "60秒"},
                            {"name": "绳索过顶臂屈伸", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "集中弯举", "sets": 3, "reps": "12-15", "weight": "10kg", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "手臂拉伸", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周日",
                    "body_parts": ["休息"],
                    "focus": "完全休息或轻度活动",
                    "modules": {
                        "main": [
                            {"name": "瑜伽或冥想", "sets": 1, "reps": "30分钟", "weight": "", "rest": ""},
                            {"name": "营养补充", "sets": 1, "reps": "全天", "weight": "", "rest": ""},
                            {"name": "充足睡眠", "sets": 1, "reps": "8小时+", "weight": "", "rest": ""},
                        ]
                    },
                },
            ],
        }

        self.create_template_plan(plan_data)
        self.stdout.write("✓ 五分化训练模式创建完成")

    def create_three_day_split(self):
        """创建三分化训练模式"""
        plan_data = {
            "name": "高效三分化训练",
            "description": "适合初中级训练者的三分化训练计划，每次训练多个身体部位",
            "plan_type": "general_fitness",
            "duration_weeks": 6,
            "difficulty": "beginner",
            "primary_goals": ["增肌", "塑形"],
            "visibility": "template",
            "week_schedule": [
                {
                    "weekday": "周一",
                    "body_parts": ["胸部", "肩部", "三头肌"],
                    "focus": "推举肌群训练",
                    "modules": {
                        "warmup": [
                            {"name": "上肢动态热身", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "轻重量推举", "sets": 2, "reps": 12, "weight": "轻重量", "rest": "60秒"},
                        ],
                        "main": [
                            {"name": "杠铃卧推", "sets": 3, "reps": "8-10", "weight": "适中", "rest": "2分钟"},
                            {"name": "哑铃推举", "sets": 3, "reps": "10-12", "weight": "20kg", "rest": "90秒"},
                            {"name": "双杠臂屈伸", "sets": 3, "reps": "8-12", "weight": "自重", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "哑铃侧平举", "sets": 3, "reps": "12-15", "weight": "10kg", "rest": "60秒"},
                            {"name": "三头肌下拉", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "俯卧撑", "sets": 2, "reps": "至力竭", "weight": "自重", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "上肢拉伸", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周二",
                    "body_parts": ["休息"],
                    "focus": "休息恢复",
                    "modules": {
                        "main": [
                            {"name": "轻度有氧", "sets": 1, "reps": "20分钟", "weight": "", "rest": ""},
                            {"name": "全身拉伸", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""},
                        ]
                    },
                },
                {
                    "weekday": "周三",
                    "body_parts": ["背部", "二头肌"],
                    "focus": "拉力肌群训练",
                    "modules": {
                        "warmup": [
                            {"name": "肩胛激活", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "轻重量划船", "sets": 2, "reps": 12, "weight": "轻重量", "rest": "60秒"},
                        ],
                        "main": [
                            {"name": "引体向上/助力引体", "sets": 3, "reps": "6-10", "weight": "自重", "rest": "2分钟"},
                            {"name": "坐姿绳索划船", "sets": 3, "reps": "10-12", "weight": "适中", "rest": "90秒"},
                            {"name": "杠铃弯举", "sets": 3, "reps": "10-12", "weight": "25kg", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "高位下拉", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "哑铃弯举", "sets": 3, "reps": "12-15", "weight": "12kg", "rest": "60秒"},
                            {"name": "面拉", "sets": 3, "reps": "15-20", "weight": "轻重量", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "背部手臂拉伸", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周四",
                    "body_parts": ["休息"],
                    "focus": "休息恢复",
                    "modules": {
                        "main": [
                            {"name": "主动恢复", "sets": 1, "reps": "20分钟", "weight": "", "rest": ""},
                            {"name": "泡沫轴放松", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""},
                        ]
                    },
                },
                {
                    "weekday": "周五",
                    "body_parts": ["腿部"],
                    "focus": "下肢训练",
                    "modules": {
                        "warmup": [
                            {"name": "下肢动态热身", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""},
                            {"name": "空蹲练习", "sets": 2, "reps": 15, "weight": "自重", "rest": "60秒"},
                        ],
                        "main": [
                            {"name": "杠铃深蹲", "sets": 4, "reps": "8-12", "weight": "体重×1.2倍", "rest": "2分钟"},
                            {"name": "罗马尼亚硬拉", "sets": 3, "reps": "10-12", "weight": "体重", "rest": "90秒"},
                            {"name": "箭步蹲", "sets": 3, "reps": "12次/腿", "weight": "15kg", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "腿弯举", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "小腿提踵", "sets": 3, "reps": "15-20", "weight": "适中", "rest": "60秒"},
                            {"name": "臀桥", "sets": 3, "reps": "15-20", "weight": "自重", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "下肢拉伸", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周六",
                    "body_parts": ["休息"],
                    "focus": "休息或轻度活动",
                    "modules": {
                        "main": [
                            {"name": "瑜伽", "sets": 1, "reps": "30分钟", "weight": "", "rest": ""},
                            {"name": "营养规划", "sets": 1, "reps": "全天", "weight": "", "rest": ""},
                        ]
                    },
                },
                {
                    "weekday": "周日",
                    "body_parts": ["休息"],
                    "focus": "完全休息",
                    "modules": {
                        "main": [
                            {"name": "完全休息", "sets": 1, "reps": "全天", "weight": "", "rest": ""},
                            {"name": "充足睡眠", "sets": 1, "reps": "8小时+", "weight": "", "rest": ""},
                        ]
                    },
                },
            ],
        }

        self.create_template_plan(plan_data)
        self.stdout.write("✓ 三分化训练模式创建完成")

    def create_push_pull_legs(self):
        """创建推拉腿训练模式"""
        plan_data = {
            "name": "经典推拉腿训练",
            "description": "按运动模式划分的高效训练计划，适合各个水平的训练者",
            "plan_type": "strength",
            "duration_weeks": 8,
            "difficulty": "intermediate",
            "primary_goals": ["增肌", "力量", "塑形"],
            "visibility": "template",
            "week_schedule": [
                {
                    "weekday": "周一",
                    "body_parts": ["推"],
                    "focus": "推举肌群 - 胸肩三头",
                    "modules": {
                        "warmup": [
                            {"name": "上肢动态热身", "sets": 1, "reps": "6分钟", "weight": "", "rest": ""},
                            {"name": "空杆推举", "sets": 2, "reps": 12, "weight": "空杆", "rest": "60秒"},
                        ],
                        "main": [
                            {"name": "杠铃卧推", "sets": 4, "reps": "6-8", "weight": "体重×1.2倍", "rest": "3分钟"},
                            {"name": "上斜哑铃推举", "sets": 3, "reps": "8-10", "weight": "25kg", "rest": "2分钟"},
                            {"name": "哑铃推举", "sets": 3, "reps": "10-12", "weight": "20kg", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "哑铃侧平举", "sets": 3, "reps": "12-15", "weight": "10kg", "rest": "60秒"},
                            {"name": "双杠臂屈伸", "sets": 3, "reps": "10-12", "weight": "自重", "rest": "75秒"},
                            {"name": "三头肌下拉", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "推举肌群拉伸", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周二",
                    "body_parts": ["拉"],
                    "focus": "拉力肌群 - 背部二头",
                    "modules": {
                        "warmup": [
                            {"name": "肩胛激活", "sets": 1, "reps": "6分钟", "weight": "", "rest": ""},
                            {"name": "弹力带划船", "sets": 2, "reps": 15, "weight": "轻阻力", "rest": "60秒"},
                        ],
                        "main": [
                            {"name": "引体向上", "sets": 4, "reps": "6-10", "weight": "自重", "rest": "3分钟"},
                            {"name": "杠铃划船", "sets": 3, "reps": "8-10", "weight": "60kg", "rest": "2分钟"},
                            {"name": "高位下拉", "sets": 3, "reps": "10-12", "weight": "适中", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "坐姿绳索划船", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "杠铃弯举", "sets": 3, "reps": "10-12", "weight": "25kg", "rest": "75秒"},
                            {"name": "面拉", "sets": 3, "reps": "15-20", "weight": "轻重量", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "拉力肌群拉伸", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周三",
                    "body_parts": ["腿"],
                    "focus": "下肢训练 - 腿臀核心",
                    "modules": {
                        "warmup": [
                            {"name": "下肢动态热身", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""},
                            {"name": "空蹲练习", "sets": 2, "reps": 15, "weight": "自重", "rest": "60秒"},
                        ],
                        "main": [
                            {"name": "杠铃深蹲", "sets": 4, "reps": "6-8", "weight": "体重×1.5倍", "rest": "3分钟"},
                            {"name": "罗马尼亚硬拉", "sets": 3, "reps": "8-10", "weight": "体重×1.2倍", "rest": "2分钟"},
                            {"name": "保加利亚分腿蹲", "sets": 3, "reps": "10次/腿", "weight": "20kg", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "腿弯举", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "腿伸展", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "小腿提踵", "sets": 4, "reps": "15-20", "weight": "适中", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "下肢拉伸", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周四",
                    "body_parts": ["推"],
                    "focus": "推举肌群 - 力量变化",
                    "modules": {
                        "warmup": [
                            {"name": "肩关节热身", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "轻重量推举", "sets": 2, "reps": 10, "weight": "轻重量", "rest": "60秒"},
                        ],
                        "main": [
                            {"name": "哑铃卧推", "sets": 4, "reps": "8-10", "weight": "30kg", "rest": "2分钟"},
                            {"name": "上斜杠铃推举", "sets": 3, "reps": "8-10", "weight": "50kg", "rest": "2分钟"},
                            {"name": "军用推举", "sets": 3, "reps": "8-10", "weight": "35kg", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "哑铃前平举", "sets": 3, "reps": "12-15", "weight": "8kg", "rest": "60秒"},
                            {"name": "窄距卧推", "sets": 3, "reps": "10-12", "weight": "适中", "rest": "75秒"},
                            {"name": "绳索过顶臂屈伸", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "推举肌群放松", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周五",
                    "body_parts": ["拉"],
                    "focus": "拉力肌群 - 细节雕刻",
                    "modules": {
                        "warmup": [
                            {"name": "背部激活", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "轻重量反向飞鸟", "sets": 2, "reps": 12, "weight": "5kg", "rest": "60秒"},
                        ],
                        "main": [
                            {"name": "宽握引体向上", "sets": 3, "reps": "8-12", "weight": "自重", "rest": "2分钟"},
                            {"name": "T杠划船", "sets": 3, "reps": "10-12", "weight": "40kg", "rest": "90秒"},
                            {"name": "单臂哑铃划船", "sets": 3, "reps": "10次/臂", "weight": "25kg", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "直臂下拉", "sets": 3, "reps": "12-15", "weight": "适中", "rest": "60秒"},
                            {"name": "锤式弯举", "sets": 3, "reps": "12-15", "weight": "12kg", "rest": "60秒"},
                            {"name": "集中弯举", "sets": 3, "reps": "12-15", "weight": "10kg", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "拉力肌群放松", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周六",
                    "body_parts": ["腿"],
                    "focus": "下肢强化训练",
                    "modules": {
                        "warmup": [
                            {"name": "髋关节激活", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""},
                            {"name": "臀桥激活", "sets": 2, "reps": 15, "weight": "自重", "rest": "60秒"},
                        ],
                        "main": [
                            {"name": "前蹲", "sets": 3, "reps": "8-10", "weight": "体重", "rest": "2分钟"},
                            {"name": "直腿硬拉", "sets": 3, "reps": "10-12", "weight": "体重", "rest": "90秒"},
                            {"name": "腿举", "sets": 3, "reps": "15-20", "weight": "适中", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "箭步蹲行走", "sets": 3, "reps": "20步", "weight": "15kg", "rest": "60秒"},
                            {"name": "单腿臀桥", "sets": 3, "reps": "12次/腿", "weight": "自重", "rest": "60秒"},
                            {"name": "坐姿小腿提踵", "sets": 3, "reps": "20-25", "weight": "适中", "rest": "60秒"},
                        ],
                        "cooldown": [{"name": "下肢深度拉伸", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周日",
                    "body_parts": ["休息"],
                    "focus": "积极恢复",
                    "modules": {
                        "main": [
                            {"name": "瑜伽流动", "sets": 1, "reps": "30分钟", "weight": "", "rest": ""},
                            {"name": "冥想放松", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""},
                            {"name": "营养补充", "sets": 1, "reps": "全天", "weight": "", "rest": ""},
                        ]
                    },
                },
            ],
        }

        self.create_template_plan(plan_data)
        self.stdout.write("✓ 推拉腿训练模式创建完成")

    def create_cardio_program(self):
        """创建有氧运动训练模式"""
        plan_data = {
            "name": "全面有氧训练计划",
            "description": "专注心肺功能提升和脂肪燃烧的有氧训练计划",
            "plan_type": "endurance",
            "duration_weeks": 6,
            "difficulty": "beginner",
            "primary_goals": ["减脂", "心肺", "耐力"],
            "visibility": "template",
            "week_schedule": [
                {
                    "weekday": "周一",
                    "body_parts": ["心肺系统"],
                    "focus": "HIIT高强度间歇训练",
                    "modules": {
                        "warmup": [
                            {"name": "轻松慢跑", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "动态拉伸", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                        ],
                        "main": [
                            {"name": "冲刺跑", "sets": 8, "reps": "30秒", "weight": "最大强度", "rest": "90秒"},
                            {"name": "跳绳", "sets": 5, "reps": "1分钟", "weight": "中等强度", "rest": "1分钟"},
                            {"name": "波比跳", "sets": 4, "reps": "30秒", "weight": "自重", "rest": "1分钟"},
                        ],
                        "cooldown": [
                            {"name": "慢走恢复", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "全身拉伸", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""},
                        ],
                    },
                },
                {
                    "weekday": "周二",
                    "body_parts": ["心肺系统"],
                    "focus": "中等强度持续有氧",
                    "modules": {
                        "warmup": [{"name": "关节活动", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                        "main": [
                            {"name": "椭圆机", "sets": 1, "reps": "30分钟", "weight": "中等强度", "rest": ""},
                            {"name": "爬楼梯", "sets": 1, "reps": "15分钟", "weight": "稳定配速", "rest": ""},
                        ],
                        "cooldown": [{"name": "放松拉伸", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周三",
                    "body_parts": ["全身"],
                    "focus": "功能性有氧训练",
                    "modules": {
                        "warmup": [{"name": "全身激活", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                        "main": [
                            {"name": "开合跳", "sets": 6, "reps": "45秒", "weight": "自重", "rest": "15秒"},
                            {"name": "高抬腿", "sets": 6, "reps": "45秒", "weight": "自重", "rest": "15秒"},
                            {"name": "登山者", "sets": 6, "reps": "45秒", "weight": "自重", "rest": "15秒"},
                            {"name": "俯卧撑跳", "sets": 4, "reps": "30秒", "weight": "自重", "rest": "30秒"},
                        ],
                        "cooldown": [{"name": "瑜伽拉伸", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周四",
                    "body_parts": ["心肺系统"],
                    "focus": "游泳或水中运动",
                    "modules": {
                        "warmup": [{"name": "水中热身", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""}],
                        "main": [
                            {"name": "自由泳", "sets": 8, "reps": "50米", "weight": "中等强度", "rest": "1分钟"},
                            {"name": "蛙泳", "sets": 6, "reps": "50米", "weight": "轻松配速", "rest": "1分钟"},
                            {"name": "踩水", "sets": 3, "reps": "2分钟", "weight": "持续", "rest": "1分钟"},
                        ],
                        "cooldown": [{"name": "水中放松", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周五",
                    "body_parts": ["心肺系统"],
                    "focus": "长距离慢跑",
                    "modules": {
                        "warmup": [
                            {"name": "走路热身", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                            {"name": "跑前拉伸", "sets": 1, "reps": "5分钟", "weight": "", "rest": ""},
                        ],
                        "main": [
                            {"name": "慢跑", "sets": 1, "reps": "45分钟", "weight": "会话配速", "rest": ""},
                            {"name": "间歇恢复", "sets": 3, "reps": "2分钟走+3分钟跑", "weight": "轻松", "rest": ""},
                        ],
                        "cooldown": [
                            {"name": "步行恢复", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""},
                            {"name": "跑后拉伸", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""},
                        ],
                    },
                },
                {
                    "weekday": "周六",
                    "body_parts": ["全身"],
                    "focus": "户外活动有氧",
                    "modules": {
                        "warmup": [{"name": "动态热身", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""}],
                        "main": [
                            {"name": "骑行", "sets": 1, "reps": "60分钟", "weight": "中等强度", "rest": ""},
                            {"name": "爬山", "sets": 1, "reps": "45分钟", "weight": "变化强度", "rest": ""},
                            {"name": "户外健走", "sets": 1, "reps": "30分钟", "weight": "快速配速", "rest": ""},
                        ],
                        "cooldown": [{"name": "户外拉伸", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周日",
                    "body_parts": ["恢复"],
                    "focus": "主动恢复",
                    "modules": {
                        "main": [
                            {"name": "瑜伽", "sets": 1, "reps": "30分钟", "weight": "轻松", "rest": ""},
                            {"name": "冥想", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""},
                            {"name": "按摩放松", "sets": 1, "reps": "20分钟", "weight": "", "rest": ""},
                        ]
                    },
                },
            ],
        }

        self.create_template_plan(plan_data)
        self.stdout.write("✓ 有氧运动训练模式创建完成")

    def create_functional_training(self):
        """创建功能性训练模式"""
        plan_data = {
            "name": "全身功能性训练",
            "description": "提升运动表现和日常功能的综合训练计划",
            "plan_type": "functional",
            "duration_weeks": 8,
            "difficulty": "intermediate",
            "primary_goals": ["功能性", "平衡", "协调", "核心"],
            "visibility": "template",
            "week_schedule": [
                {
                    "weekday": "周一",
                    "body_parts": ["全身", "核心"],
                    "focus": "核心稳定与平衡",
                    "modules": {
                        "warmup": [
                            {"name": "关节活动", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""},
                            {"name": "平板支撑激活", "sets": 2, "reps": "30秒", "weight": "自重", "rest": "30秒"},
                        ],
                        "main": [
                            {"name": "土耳其起立", "sets": 3, "reps": "5次/侧", "weight": "8kg", "rest": "90秒"},
                            {"name": "农夫行走", "sets": 4, "reps": "20米", "weight": "20kg/手", "rest": "90秒"},
                            {"name": "单腿硬拉", "sets": 3, "reps": "8次/腿", "weight": "15kg", "rest": "75秒"},
                            {"name": "鸟狗式", "sets": 3, "reps": "10次/侧", "weight": "自重", "rest": "60秒"},
                        ],
                        "accessory": [
                            {"name": "单臂推举", "sets": 3, "reps": "8次/臂", "weight": "12kg", "rest": "60秒"},
                            {"name": "侧平板", "sets": 3, "reps": "30秒/侧", "weight": "自重", "rest": "60秒"},
                            {"name": "死虫式", "sets": 3, "reps": "10次/侧", "weight": "自重", "rest": "45秒"},
                        ],
                        "cooldown": [{"name": "功能性拉伸", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周二",
                    "body_parts": ["全身"],
                    "focus": "动态力量与爆发力",
                    "modules": {
                        "warmup": [{"name": "动态热身", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""}],
                        "main": [
                            {"name": "壶铃摆动", "sets": 4, "reps": "20次", "weight": "16kg", "rest": "90秒"},
                            {"name": "跳箱", "sets": 4, "reps": "10次", "weight": "自重", "rest": "2分钟"},
                            {"name": "药球投掷", "sets": 3, "reps": "15次", "weight": "6kg", "rest": "90秒"},
                            {"name": "熊爬", "sets": 3, "reps": "20步", "weight": "自重", "rest": "75秒"},
                        ],
                        "accessory": [
                            {"name": "蟹步行走", "sets": 3, "reps": "15步/方向", "weight": "自重", "rest": "60秒"},
                            {"name": "单臂划船", "sets": 3, "reps": "12次/臂", "weight": "20kg", "rest": "60秒"},
                            {"name": "手枪蹲（辅助）", "sets": 3, "reps": "5次/腿", "weight": "辅助", "rest": "90秒"},
                        ],
                        "cooldown": [{"name": "动态恢复", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周三",
                    "body_parts": ["休息"],
                    "focus": "主动恢复",
                    "modules": {
                        "main": [
                            {"name": "轻松步行", "sets": 1, "reps": "30分钟", "weight": "", "rest": ""},
                            {"name": "泡沫轴放松", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""},
                            {"name": "冥想", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""},
                        ]
                    },
                },
                {
                    "weekday": "周四",
                    "body_parts": ["全身"],
                    "focus": "复合动作训练",
                    "modules": {
                        "warmup": [{"name": "全身激活", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""}],
                        "main": [
                            {"name": "臀桥到推举", "sets": 3, "reps": "12次", "weight": "15kg", "rest": "90秒"},
                            {"name": "深蹲到推举", "sets": 3, "reps": "12次", "weight": "20kg", "rest": "90秒"},
                            {"name": "弓步蹲旋转", "sets": 3, "reps": "10次/侧", "weight": "8kg", "rest": "75秒"},
                            {"name": "伐木者", "sets": 3, "reps": "12次/侧", "weight": "12kg", "rest": "75秒"},
                        ],
                        "accessory": [
                            {"name": "山羊挺身", "sets": 3, "reps": "15次", "weight": "自重", "rest": "60秒"},
                            {"name": "俄罗斯转体", "sets": 3, "reps": "20次", "weight": "10kg", "rest": "60秒"},
                            {"name": "超人式", "sets": 3, "reps": "15次", "weight": "自重", "rest": "45秒"},
                        ],
                        "cooldown": [{"name": "功能性恢复", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周五",
                    "body_parts": ["全身"],
                    "focus": "协调性与敏捷训练",
                    "modules": {
                        "warmup": [{"name": "敏捷热身", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""}],
                        "main": [
                            {"name": "梯子训练", "sets": 4, "reps": "30秒", "weight": "自重", "rest": "90秒"},
                            {"name": "反应球训练", "sets": 3, "reps": "2分钟", "weight": "反应球", "rest": "90秒"},
                            {"name": "平衡板深蹲", "sets": 3, "reps": "12次", "weight": "自重", "rest": "75秒"},
                            {"name": "单脚站立", "sets": 3, "reps": "45秒/脚", "weight": "自重", "rest": "60秒"},
                        ],
                        "accessory": [
                            {"name": "闭眼平衡", "sets": 3, "reps": "30秒/脚", "weight": "自重", "rest": "60秒"},
                            {"name": "侧向移动", "sets": 3, "reps": "15步/方向", "weight": "自重", "rest": "60秒"},
                            {"name": "跳跃降落", "sets": 3, "reps": "10次", "weight": "自重", "rest": "75秒"},
                        ],
                        "cooldown": [{"name": "平衡恢复", "sets": 1, "reps": "8分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周六",
                    "body_parts": ["全身"],
                    "focus": "运动技能训练",
                    "modules": {
                        "warmup": [{"name": "运动准备", "sets": 1, "reps": "10分钟", "weight": "", "rest": ""}],
                        "main": [
                            {"name": "翻滚练习", "sets": 3, "reps": "8次/方向", "weight": "自重", "rest": "90秒"},
                            {"name": "手倒立练习", "sets": 3, "reps": "30秒", "weight": "自重", "rest": "2分钟"},
                            {"name": "爬行变式", "sets": 3, "reps": "30秒", "weight": "自重", "rest": "90秒"},
                            {"name": "跳跃组合", "sets": 3, "reps": "10组合", "weight": "自重", "rest": "90秒"},
                        ],
                        "accessory": [
                            {"name": "柔韧性练习", "sets": 3, "reps": "各1分钟", "weight": "自重", "rest": "30秒"},
                            {"name": "呼吸训练", "sets": 3, "reps": "2分钟", "weight": "", "rest": "30秒"},
                            {"name": "身体感知", "sets": 3, "reps": "1分钟", "weight": "自重", "rest": "30秒"},
                        ],
                        "cooldown": [{"name": "整合性拉伸", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""}],
                    },
                },
                {
                    "weekday": "周日",
                    "body_parts": ["恢复"],
                    "focus": "休息与恢复",
                    "modules": {
                        "main": [
                            {"name": "瑜伽流动", "sets": 1, "reps": "45分钟", "weight": "", "rest": ""},
                            {"name": "深度拉伸", "sets": 1, "reps": "20分钟", "weight": "", "rest": ""},
                            {"name": "放松冥想", "sets": 1, "reps": "15分钟", "weight": "", "rest": ""},
                        ]
                    },
                },
            ],
        }

        self.create_template_plan(plan_data)
        self.stdout.write("✓ 功能性训练模式创建完成")

    def create_template_plan(self, plan_data):
        """创建训练计划模板"""
        try:
            # 创建系统管理员用户（如果不存在）
            admin_user, created = User.objects.get_or_create(
                username="system_admin", defaults={"email": "admin@system.local", "is_staff": True, "is_superuser": True}
            )

            # 使用TrainingPlan模型
            existing_plan = TrainingPlan.objects.filter(name=plan_data["name"]).first()

            if existing_plan:
                # 更新现有模板
                existing_plan.mode = plan_data.get("plan_type", "general_fitness")
                existing_plan.cycle_weeks = plan_data.get("duration_weeks", 8)
                existing_plan.week_schedule = plan_data["week_schedule"]
                existing_plan.visibility = "public"  # 作为模板公开
                existing_plan.save()
                self.stdout.write(f'更新模板: {plan_data["name"]}')
            else:
                # 创建新模板
                plan = TrainingPlan.objects.create(
                    name=plan_data["name"],
                    mode=plan_data.get("plan_type", "general_fitness"),
                    cycle_weeks=plan_data.get("duration_weeks", 8),
                    week_schedule=plan_data["week_schedule"],
                    visibility="public",  # 作为模板公开
                    user=admin_user,
                )
                self.stdout.write(f"创建模板: {plan.name}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建模板 {plan_data["name"]} 时出错: {str(e)}'))
