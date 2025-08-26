"""
健身训练计划模板数据
包含各种训练模式的详细模板数据
"""

# 五分化训练模板
FIVE_DAY_SPLIT_TEMPLATE = {
    'id': 'template_5day_split',
    'name': '五分化力量训练',
    'description': '经典五分化训练，适合中高级训练者',
    'mode': '五分化',
    'cycle_weeks': 8,
    'difficulty': 'intermediate',
    'target_goals': ['增肌', '力量提升'],
    'week_schedule': [
        {
            'weekday': '周一',
            'body_parts': ['胸部'],
            'modules': {
                'warmup': [
                    {'name': '动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量卧推', 'sets': 2, 'reps': 15, 'weight': '空杆', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '杠铃卧推', 'sets': 4, 'reps': '8-10', 'weight': '75kg', 'rest': '3分钟'},
                    {'name': '哑铃卧推', 'sets': 3, 'reps': '10-12', 'weight': '30kg', 'rest': '90秒'},
                    {'name': '上斜哑铃推举', 'sets': 3, 'reps': '10-12', 'weight': '25kg', 'rest': '90秒'},
                    {'name': '双杠臂屈伸', 'sets': 3, 'reps': '10-12', 'weight': '自重', 'rest': '90秒'}
                ],
                'accessory': [
                    {'name': '哑铃飞鸟', 'sets': 3, 'reps': '12-15', 'weight': '15kg', 'rest': '60秒'},
                    {'name': '绳索夹胸', 'sets': 3, 'reps': '12-15', 'weight': '20kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '胸部拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周二',
            'body_parts': ['背部'],
            'modules': {
                'warmup': [
                    {'name': '动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量划船', 'sets': 2, 'reps': 15, 'weight': '20kg', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '硬拉', 'sets': 4, 'reps': '6-8', 'weight': '100kg', 'rest': '3分钟'},
                    {'name': '引体向上', 'sets': 4, 'reps': '8-12', 'weight': '自重', 'rest': '2分钟'},
                    {'name': '杠铃划船', 'sets': 3, 'reps': '8-10', 'weight': '60kg', 'rest': '90秒'},
                    {'name': '坐姿划船', 'sets': 3, 'reps': '10-12', 'weight': '50kg', 'rest': '90秒'}
                ],
                'accessory': [
                    {'name': '哑铃单臂划船', 'sets': 3, 'reps': '12-15', 'weight': '25kg', 'rest': '60秒'},
                    {'name': '高位下拉', 'sets': 3, 'reps': '12-15', 'weight': '40kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '背部拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周三',
            'body_parts': ['腿部'],
            'modules': {
                'warmup': [
                    {'name': '动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量深蹲', 'sets': 2, 'reps': 15, 'weight': '空杆', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '深蹲', 'sets': 4, 'reps': '8-10', 'weight': '80kg', 'rest': '3分钟'},
                    {'name': '罗马尼亚硬拉', 'sets': 3, 'reps': '10-12', 'weight': '60kg', 'rest': '2分钟'},
                    {'name': '保加利亚分腿蹲', 'sets': 3, 'reps': '12-15', 'weight': '20kg', 'rest': '90秒'},
                    {'name': '腿举', 'sets': 3, 'reps': '15-20', 'weight': '100kg', 'rest': '90秒'}
                ],
                'accessory': [
                    {'name': '腿弯举', 'sets': 3, 'reps': '12-15', 'weight': '30kg', 'rest': '60秒'},
                    {'name': '腿屈伸', 'sets': 3, 'reps': '12-15', 'weight': '40kg', 'rest': '60秒'},
                    {'name': '提踵', 'sets': 4, 'reps': '15-20', 'weight': '60kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '腿部拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周四',
            'body_parts': ['肩部'],
            'modules': {
                'warmup': [
                    {'name': '肩部环绕', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量推举', 'sets': 2, 'reps': 15, 'weight': '10kg', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '杠铃推举', 'sets': 4, 'reps': '8-10', 'weight': '50kg', 'rest': '2分钟'},
                    {'name': '哑铃肩上推举', 'sets': 3, 'reps': '10-12', 'weight': '20kg', 'rest': '90秒'},
                    {'name': '哑铃侧平举', 'sets': 3, 'reps': '12-15', 'weight': '12kg', 'rest': '60秒'},
                    {'name': '哑铃后束飞鸟', 'sets': 3, 'reps': '12-15', 'weight': '10kg', 'rest': '60秒'}
                ],
                'accessory': [
                    {'name': '哑铃前平举', 'sets': 3, 'reps': '12-15', 'weight': '10kg', 'rest': '60秒'},
                    {'name': '绳索面拉', 'sets': 3, 'reps': '15-20', 'weight': '15kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '肩部拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周五',
            'body_parts': ['手臂'],
            'modules': {
                'warmup': [
                    {'name': '手臂环绕', 'sets': 1, 'reps': '3分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量弯举', 'sets': 2, 'reps': 15, 'weight': '10kg', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '杠铃弯举', 'sets': 4, 'reps': '8-12', 'weight': '30kg', 'rest': '90秒'},
                    {'name': '窄距卧推', 'sets': 4, 'reps': '8-12', 'weight': '50kg', 'rest': '90秒'},
                    {'name': '哑铃弯举', 'sets': 3, 'reps': '10-12', 'weight': '15kg', 'rest': '75秒'},
                    {'name': '三头肌臂屈伸', 'sets': 3, 'reps': '10-12', 'weight': '自重', 'rest': '75秒'}
                ],
                'accessory': [
                    {'name': '锤式弯举', 'sets': 3, 'reps': '12-15', 'weight': '12kg', 'rest': '60秒'},
                    {'name': '绳索下压', 'sets': 3, 'reps': '12-15', 'weight': '25kg', 'rest': '60秒'},
                    {'name': '绳索弯举', 'sets': 3, 'reps': '12-15', 'weight': '20kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '手臂拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周六',
            'body_parts': ['休息'],
            'modules': {
                'warmup': [],
                'main': [],
                'accessory': [
                    {'name': '轻度有氧运动', 'sets': 1, 'reps': '30分钟', 'weight': '', 'rest': ''},
                    {'name': '全身拉伸', 'sets': 1, 'reps': '15分钟', 'weight': '', 'rest': ''}
                ],
                'cooldown': []
            }
        },
        {
            'weekday': '周日',
            'body_parts': ['休息'],
            'modules': {
                'warmup': [],
                'main': [],
                'accessory': [],
                'cooldown': [
                    {'name': '完全休息', 'sets': 1, 'reps': '全天', 'weight': '', 'rest': ''}
                ]
            }
        }
    ]
}

# 三分化训练模板
THREE_DAY_SPLIT_TEMPLATE = {
    'id': 'template_3day_split',
    'name': '三分化力量训练',
    'description': '经典三分化训练，适合初中级训练者',
    'mode': '三分化',
    'cycle_weeks': 6,
    'difficulty': 'beginner',
    'target_goals': ['增肌', '力量提升'],
    'week_schedule': [
        {
            'weekday': '周一',
            'body_parts': ['胸部', '三头肌'],
            'modules': {
                'warmup': [
                    {'name': '动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量卧推', 'sets': 2, 'reps': 15, 'weight': '空杆', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '杠铃卧推', 'sets': 4, 'reps': '8-10', 'weight': '70kg', 'rest': '3分钟'},
                    {'name': '哑铃卧推', 'sets': 3, 'reps': '10-12', 'weight': '25kg', 'rest': '90秒'},
                    {'name': '双杠臂屈伸', 'sets': 3, 'reps': '8-12', 'weight': '自重', 'rest': '90秒'},
                    {'name': '绳索下压', 'sets': 3, 'reps': '12-15', 'weight': '25kg', 'rest': '75秒'}
                ],
                'accessory': [
                    {'name': '哑铃飞鸟', 'sets': 3, 'reps': '12-15', 'weight': '15kg', 'rest': '60秒'},
                    {'name': '哑铃臂屈伸', 'sets': 3, 'reps': '12-15', 'weight': '15kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '胸部三头拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周三',
            'body_parts': ['背部', '二头肌'],
            'modules': {
                'warmup': [
                    {'name': '动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量划船', 'sets': 2, 'reps': 15, 'weight': '20kg', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '硬拉', 'sets': 4, 'reps': '6-8', 'weight': '90kg', 'rest': '3分钟'},
                    {'name': '引体向上', 'sets': 4, 'reps': '6-10', 'weight': '自重', 'rest': '2分钟'},
                    {'name': '杠铃划船', 'sets': 3, 'reps': '8-10', 'weight': '55kg', 'rest': '90秒'},
                    {'name': '杠铃弯举', 'sets': 3, 'reps': '10-12', 'weight': '25kg', 'rest': '75秒'}
                ],
                'accessory': [
                    {'name': '坐姿划船', 'sets': 3, 'reps': '12-15', 'weight': '45kg', 'rest': '60秒'},
                    {'name': '哑铃弯举', 'sets': 3, 'reps': '12-15', 'weight': '12kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '背部二头拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周五',
            'body_parts': ['腿部', '肩部'],
            'modules': {
                'warmup': [
                    {'name': '动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量深蹲', 'sets': 2, 'reps': 15, 'weight': '空杆', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '深蹲', 'sets': 4, 'reps': '8-10', 'weight': '75kg', 'rest': '3分钟'},
                    {'name': '罗马尼亚硬拉', 'sets': 3, 'reps': '10-12', 'weight': '55kg', 'rest': '2分钟'},
                    {'name': '杠铃推举', 'sets': 4, 'reps': '8-10', 'weight': '45kg', 'rest': '2分钟'},
                    {'name': '哑铃侧平举', 'sets': 3, 'reps': '12-15', 'weight': '10kg', 'rest': '75秒'}
                ],
                'accessory': [
                    {'name': '腿举', 'sets': 3, 'reps': '15-20', 'weight': '80kg', 'rest': '60秒'},
                    {'name': '哑铃后束飞鸟', 'sets': 3, 'reps': '12-15', 'weight': '8kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '腿部肩部拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        }
    ]
}

# 推拉腿训练模板
PUSH_PULL_LEGS_TEMPLATE = {
    'id': 'template_push_pull_legs',
    'name': '推拉腿训练',
    'description': '经典推拉腿分化，平衡发展全身肌群',
    'mode': '推拉腿',
    'cycle_weeks': 8,
    'difficulty': 'intermediate',
    'target_goals': ['增肌', '力量平衡'],
    'week_schedule': [
        {
            'weekday': '周一',
            'body_parts': ['胸部', '肩部', '三头肌'],
            'modules': {
                'warmup': [
                    {'name': '上肢动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量推举', 'sets': 2, 'reps': 15, 'weight': '空杆', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '杠铃卧推', 'sets': 4, 'reps': '6-8', 'weight': '80kg', 'rest': '3分钟'},
                    {'name': '哑铃肩上推举', 'sets': 4, 'reps': '8-10', 'weight': '22kg', 'rest': '2分钟'},
                    {'name': '上斜哑铃卧推', 'sets': 3, 'reps': '10-12', 'weight': '25kg', 'rest': '90秒'},
                    {'name': '双杠臂屈伸', 'sets': 3, 'reps': '10-12', 'weight': '自重', 'rest': '90秒'}
                ],
                'accessory': [
                    {'name': '哑铃侧平举', 'sets': 3, 'reps': '12-15', 'weight': '12kg', 'rest': '60秒'},
                    {'name': '绳索下压', 'sets': 3, 'reps': '12-15', 'weight': '25kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '推肌群拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周三',
            'body_parts': ['背部', '二头肌'],
            'modules': {
                'warmup': [
                    {'name': '背部动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '轻重量划船', 'sets': 2, 'reps': 15, 'weight': '20kg', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '硬拉', 'sets': 4, 'reps': '5-6', 'weight': '110kg', 'rest': '3分钟'},
                    {'name': '引体向上', 'sets': 4, 'reps': '8-12', 'weight': '自重', 'rest': '2分钟'},
                    {'name': '杠铃划船', 'sets': 4, 'reps': '8-10', 'weight': '65kg', 'rest': '2分钟'},
                    {'name': '杠铃弯举', 'sets': 3, 'reps': '10-12', 'weight': '30kg', 'rest': '90秒'}
                ],
                'accessory': [
                    {'name': '坐姿划船', 'sets': 3, 'reps': '12-15', 'weight': '50kg', 'rest': '60秒'},
                    {'name': '锤式弯举', 'sets': 3, 'reps': '12-15', 'weight': '15kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '拉肌群拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周五',
            'body_parts': ['腿部'],
            'modules': {
                'warmup': [
                    {'name': '下肢动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                    {'name': '徒手深蹲', 'sets': 2, 'reps': 20, 'weight': '自重', 'rest': '60秒'}
                ],
                'main': [
                    {'name': '深蹲', 'sets': 4, 'reps': '6-8', 'weight': '90kg', 'rest': '3分钟'},
                    {'name': '罗马尼亚硬拉', 'sets': 4, 'reps': '8-10', 'weight': '70kg', 'rest': '2分钟'},
                    {'name': '保加利亚分腿蹲', 'sets': 3, 'reps': '12-15', 'weight': '20kg', 'rest': '90秒'},
                    {'name': '腿举', 'sets': 3, 'reps': '15-20', 'weight': '120kg', 'rest': '90秒'}
                ],
                'accessory': [
                    {'name': '腿弯举', 'sets': 3, 'reps': '12-15', 'weight': '35kg', 'rest': '60秒'},
                    {'name': '提踵', 'sets': 4, 'reps': '15-20', 'weight': '70kg', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '腿部拉伸', 'sets': 1, 'reps': '8分钟', 'weight': '', 'rest': ''}
                ]
            }
        }
    ]
}

# 有氧运动模板
CARDIO_TEMPLATE = {
    'id': 'template_cardio',
    'name': '有氧运动训练',
    'description': '全面的有氧训练计划，提升心肺功能',
    'mode': '有氧运动',
    'cycle_weeks': 4,
    'difficulty': 'beginner',
    'target_goals': ['减脂', '心肺功能'],
    'week_schedule': [
        {
            'weekday': '周一',
            'body_parts': ['有氧训练'],
            'modules': {
                'warmup': [
                    {'name': '动态热身', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ],
                'main': [
                    {'name': '跑步机慢跑', 'sets': 1, 'reps': '30分钟', 'weight': '中等强度', 'rest': ''},
                    {'name': '椭圆机', 'sets': 1, 'reps': '15分钟', 'weight': '中等强度', 'rest': '2分钟'}
                ],
                'accessory': [
                    {'name': '核心训练', 'sets': 3, 'reps': '1分钟', 'weight': '自重', 'rest': '30秒'}
                ],
                'cooldown': [
                    {'name': '全身拉伸', 'sets': 1, 'reps': '10分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周三',
            'body_parts': ['有氧训练'],
            'modules': {
                'warmup': [
                    {'name': '动态热身', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ],
                'main': [
                    {'name': '单车', 'sets': 1, 'reps': '35分钟', 'weight': '中等强度', 'rest': ''},
                    {'name': '划船机', 'sets': 1, 'reps': '15分钟', 'weight': '中等强度', 'rest': ''}
                ],
                'accessory': [
                    {'name': '功能性训练', 'sets': 3, 'reps': '1分钟', 'weight': '自重', 'rest': '30秒'}
                ],
                'cooldown': [
                    {'name': '全身拉伸', 'sets': 1, 'reps': '10分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周五',
            'body_parts': ['有氧训练'],
            'modules': {
                'warmup': [
                    {'name': '动态热身', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ],
                'main': [
                    {'name': 'HIIT训练', 'sets': 8, 'reps': '30秒', 'weight': '高强度', 'rest': '30秒'},
                    {'name': '慢走恢复', 'sets': 1, 'reps': '10分钟', 'weight': '低强度', 'rest': ''}
                ],
                'accessory': [
                    {'name': '瑜伽', 'sets': 1, 'reps': '15分钟', 'weight': '', 'rest': ''}
                ],
                'cooldown': [
                    {'name': '深度拉伸', 'sets': 1, 'reps': '15分钟', 'weight': '', 'rest': ''}
                ]
            }
        }
    ]
}

# 功能性训练模板
FUNCTIONAL_TRAINING_TEMPLATE = {
    'id': 'template_functional',
    'name': '功能性训练',
    'description': '注重实用性和运动表现的功能性训练',
    'mode': '功能性训练',
    'cycle_weeks': 6,
    'difficulty': 'intermediate',
    'target_goals': ['功能性', '运动表现'],
    'week_schedule': [
        {
            'weekday': '周一',
            'body_parts': ['全身'],
            'modules': {
                'warmup': [
                    {'name': '动态热身', 'sets': 1, 'reps': '8分钟', 'weight': '', 'rest': ''},
                    {'name': '激活训练', 'sets': 2, 'reps': '各10次', 'weight': '自重', 'rest': '30秒'}
                ],
                'main': [
                    {'name': '深蹲跳', 'sets': 4, 'reps': '8-10', 'weight': '自重', 'rest': '90秒'},
                    {'name': '俯卧撑', 'sets': 4, 'reps': '10-15', 'weight': '自重', 'rest': '90秒'},
                    {'name': '壶铃摆动', 'sets': 4, 'reps': '15-20', 'weight': '16kg', 'rest': '90秒'},
                    {'name': '农夫行走', 'sets': 3, 'reps': '40米', 'weight': '30kg', 'rest': '2分钟'}
                ],
                'accessory': [
                    {'name': '平板支撑', 'sets': 3, 'reps': '60秒', 'weight': '自重', 'rest': '60秒'},
                    {'name': '侧平板', 'sets': 2, 'reps': '30秒', 'weight': '自重', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '功能性拉伸', 'sets': 1, 'reps': '10分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周三',
            'body_parts': ['全身'],
            'modules': {
                'warmup': [
                    {'name': '动态热身', 'sets': 1, 'reps': '8分钟', 'weight': '', 'rest': ''},
                    {'name': '关节活动', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                ],
                'main': [
                    {'name': '土耳其起立', 'sets': 3, 'reps': '5/边', 'weight': '12kg', 'rest': '2分钟'},
                    {'name': '单腿硬拉', 'sets': 3, 'reps': '10/边', 'weight': '20kg', 'rest': '90秒'},
                    {'name': '熊爬', 'sets': 3, 'reps': '20米', 'weight': '自重', 'rest': '90秒'},
                    {'name': '箱子跳跃', 'sets': 4, 'reps': '8-10', 'weight': '自重', 'rest': '2分钟'}
                ],
                'accessory': [
                    {'name': '鸟狗式', 'sets': 3, 'reps': '10/边', 'weight': '自重', 'rest': '45秒'},
                    {'name': '死虫式', 'sets': 3, 'reps': '10/边', 'weight': '自重', 'rest': '45秒'}
                ],
                'cooldown': [
                    {'name': '运动按摩', 'sets': 1, 'reps': '10分钟', 'weight': '', 'rest': ''}
                ]
            }
        },
        {
            'weekday': '周五',
            'body_parts': ['全身'],
            'modules': {
                'warmup': [
                    {'name': '动态热身', 'sets': 1, 'reps': '8分钟', 'weight': '', 'rest': ''},
                    {'name': '爆发力激活', 'sets': 2, 'reps': '各5次', 'weight': '自重', 'rest': '30秒'}
                ],
                'main': [
                    {'name': '药球训练', 'sets': 4, 'reps': '12-15', 'weight': '8kg', 'rest': '90秒'},
                    {'name': '战绳训练', 'sets': 4, 'reps': '30秒', 'weight': '15kg', 'rest': '90秒'},
                    {'name': '轮胎翻转', 'sets': 3, 'reps': '8-10', 'weight': '重型', 'rest': '2分钟'},
                    {'name': '攀爬训练', 'sets': 3, 'reps': '5米', 'weight': '自重', 'rest': '2分钟'}
                ],
                'accessory': [
                    {'name': '瑜伽球训练', 'sets': 3, 'reps': '1分钟', 'weight': '自重', 'rest': '60秒'},
                    {'name': '平衡训练', 'sets': 3, 'reps': '30秒', 'weight': '自重', 'rest': '60秒'}
                ],
                'cooldown': [
                    {'name': '恢复拉伸', 'sets': 1, 'reps': '12分钟', 'weight': '', 'rest': ''}
                ]
            }
        }
    ]
}

# 所有模板的集合
ALL_TEMPLATES = {
    FIVE_DAY_SPLIT_TEMPLATE['id']: FIVE_DAY_SPLIT_TEMPLATE,
    THREE_DAY_SPLIT_TEMPLATE['id']: THREE_DAY_SPLIT_TEMPLATE,
    PUSH_PULL_LEGS_TEMPLATE['id']: PUSH_PULL_LEGS_TEMPLATE,
    CARDIO_TEMPLATE['id']: CARDIO_TEMPLATE,
    FUNCTIONAL_TRAINING_TEMPLATE['id']: FUNCTIONAL_TRAINING_TEMPLATE,
}

def get_all_templates():
    """获取所有模板数据"""
    return ALL_TEMPLATES

def get_template_by_id(template_id):
    """根据ID获取特定模板"""
    return ALL_TEMPLATES.get(template_id)

def get_templates_by_mode(mode):
    """根据训练模式获取模板"""
    return {k: v for k, v in ALL_TEMPLATES.items() if v['mode'] == mode}
