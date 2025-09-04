from django.core.management.base import BaseCommand
from django.db import transaction

from apps.tools.models.exercise_library_models import BodyPart, Equipment, Exercise, MuscleGroup
from apps.tools.models.fitness_achievement_models import EnhancedFitnessAchievement, FitnessAchievementModule
from apps.tools.models.training_plan_models import TrainingPlanCategory


class Command(BaseCommand):
    help = "初始化健身系统数据"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="重置所有数据",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("重置健身系统数据...")
            self.reset_data()

        self.stdout.write("开始初始化健身系统数据...")

        with transaction.atomic():
            self.create_achievement_modules()
            self.create_muscle_groups()
            self.create_body_parts()
            self.create_equipment()
            self.create_exercises()
            self.create_achievements()
            self.create_plan_categories()

        self.stdout.write(self.style.SUCCESS("健身系统初始化完成!"))

    def reset_data(self):
        """重置数据"""
        EnhancedFitnessAchievement.objects.all().delete()
        FitnessAchievementModule.objects.all().delete()
        Exercise.objects.all().delete()
        Equipment.objects.all().delete()
        BodyPart.objects.all().delete()
        MuscleGroup.objects.all().delete()
        TrainingPlanCategory.objects.all().delete()

    def create_achievement_modules(self):
        """创建成就模块"""
        modules_data = [
            {
                "name": "strength",
                "display_name": "力量训练",
                "description": "力量训练相关成就，包括重量提升、技术掌握等",
                "icon": "fas fa-dumbbell",
                "color": "#e74c3c",
            },
            {
                "name": "cardio",
                "display_name": "有氧运动",
                "description": "有氧运动相关成就，包括耐力提升、距离目标等",
                "icon": "fas fa-running",
                "color": "#3498db",
            },
            {
                "name": "nutrition",
                "display_name": "营养管理",
                "description": "营养管理相关成就，包括饮食记录、体重管理等",
                "icon": "fas fa-apple-alt",
                "color": "#27ae60",
            },
            {
                "name": "consistency",
                "display_name": "连续性",
                "description": "训练连续性相关成就，包括连续天数、习惯养成等",
                "icon": "fas fa-calendar-check",
                "color": "#f39c12",
            },
            {
                "name": "social",
                "display_name": "社交互动",
                "description": "社交互动相关成就，包括分享、互动、社区参与等",
                "icon": "fas fa-users",
                "color": "#9b59b6",
            },
            {
                "name": "milestone",
                "display_name": "里程碑",
                "description": "重要里程碑成就，包括总体进步、长期目标等",
                "icon": "fas fa-trophy",
                "color": "#f1c40f",
            },
            {
                "name": "special",
                "display_name": "特殊成就",
                "description": "特殊条件下获得的稀有成就",
                "icon": "fas fa-star",
                "color": "#e67e22",
            },
        ]

        for module_data in modules_data:
            module, created = FitnessAchievementModule.objects.get_or_create(name=module_data["name"], defaults=module_data)
            if created:
                self.stdout.write(f"创建成就模块: {module.display_name}")

    def create_muscle_groups(self):
        """创建肌肉群"""
        muscle_groups_data = [
            ("chest", "胸大肌", "#ff6b6b"),
            ("back_lat", "背阔肌", "#4ecdc4"),
            ("back_rhomboid", "菱形肌", "#45b7d1"),
            ("back_trap", "斜方肌", "#96ceb4"),
            ("shoulders_front", "前三角肌", "#feca57"),
            ("shoulders_side", "中三角肌", "#ff9ff3"),
            ("shoulders_rear", "后三角肌", "#54a0ff"),
            ("biceps", "二头肌", "#5f27cd"),
            ("triceps", "三头肌", "#00d2d3"),
            ("forearms", "前臂肌群", "#ff6348"),
            ("abs", "腹肌", "#2ed573"),
            ("obliques", "腹斜肌", "#1e90ff"),
            ("lower_back", "下背部", "#ffa502"),
            ("glutes", "臀大肌", "#ff3838"),
            ("quads", "股四头肌", "#2f3542"),
            ("hamstrings", "股二头肌", "#57606f"),
            ("calves", "小腿肌群", "#3742fa"),
            ("hip_flexors", "髋屈肌", "#2ed573"),
        ]

        for name, chinese_name, color in muscle_groups_data:
            muscle_group, created = MuscleGroup.objects.get_or_create(
                name=name, defaults={"chinese_name": chinese_name, "color": color}
            )
            if created:
                self.stdout.write(f"创建肌肉群: {muscle_group.chinese_name}")

    def create_body_parts(self):
        """创建身体部位"""
        body_parts_data = [
            {
                "name": "chest",
                "display_name": "胸部",
                "icon": "fas fa-expand-arrows-alt",
                "color": "#ff6b6b",
                "muscle_groups": ["chest"],
            },
            {
                "name": "back",
                "display_name": "背部",
                "icon": "fas fa-arrows-alt-v",
                "color": "#4ecdc4",
                "muscle_groups": ["back_lat", "back_rhomboid", "back_trap", "lower_back"],
            },
            {
                "name": "shoulders",
                "display_name": "肩部",
                "icon": "fas fa-expand",
                "color": "#feca57",
                "muscle_groups": ["shoulders_front", "shoulders_side", "shoulders_rear"],
            },
            {
                "name": "arms",
                "display_name": "手臂",
                "icon": "fas fa-fist-raised",
                "color": "#5f27cd",
                "muscle_groups": ["biceps", "triceps", "forearms"],
            },
            {
                "name": "legs",
                "display_name": "腿部",
                "icon": "fas fa-walking",
                "color": "#2f3542",
                "muscle_groups": ["quads", "hamstrings", "calves"],
            },
            {
                "name": "core",
                "display_name": "核心",
                "icon": "fas fa-circle",
                "color": "#2ed573",
                "muscle_groups": ["abs", "obliques"],
            },
            {
                "name": "glutes",
                "display_name": "臀部",
                "icon": "fas fa-circle-notch",
                "color": "#ff3838",
                "muscle_groups": ["glutes", "hip_flexors"],
            },
        ]

        for part_data in body_parts_data:
            muscle_group_names = part_data.pop("muscle_groups")
            body_part, created = BodyPart.objects.get_or_create(name=part_data["name"], defaults=part_data)

            if created:
                self.stdout.write(f"创建身体部位: {body_part.display_name}")

                # 关联肌肉群
                muscle_groups = MuscleGroup.objects.filter(name__in=muscle_group_names)
                body_part.muscle_groups.set(muscle_groups)

    def create_equipment(self):
        """创建器械设备"""
        equipment_data = [
            ("杠铃", "barbell", "用于大重量复合动作的基础器械"),
            ("哑铃", "dumbbell", "灵活多变的自由重量器械"),
            ("绳索", "cable", "提供恒定阻力的绳索系统"),
            ("史密斯机", "machine", "提供安全支撑的固定轨道器械"),
            ("自重", "bodyweight", "使用自身体重进行训练"),
            ("壶铃", "kettlebell", "功能性训练的球形重量器械"),
            ("弹力带", "resistance_band", "便携式阻力训练工具"),
            ("药球", "medicine_ball", "爆发力和核心训练用球"),
            ("TRX", "suspension", "悬吊训练系统"),
            ("跑步机", "cardio", "室内有氧训练设备"),
            ("引体向上杆", "other", "上肢训练的悬挂设备"),
            ("平行杠", "other", "双杠训练设备"),
        ]

        for name, equipment_type, description in equipment_data:
            equipment, created = Equipment.objects.get_or_create(
                name=name, defaults={"equipment_type": equipment_type, "description": description}
            )
            if created:
                self.stdout.write(f"创建器械: {equipment.name}")

    def create_exercises(self):
        """创建动作库"""
        # 胸部动作
        chest_exercises = [
            {
                "name": "杠铃卧推",
                "english_name": "Barbell Bench Press",
                "body_parts": ["chest"],
                "primary_muscles": ["chest"],
                "secondary_muscles": ["shoulders_front", "triceps"],
                "exercise_type": "compound",
                "difficulty": "intermediate",
                "equipment": ["杠铃"],
                "description": "胸部训练的王牌动作，主要锻炼胸大肌",
                "instructions": "仰卧在卧推凳上，双手握杠铃，宽度略宽于肩膀，缓慢下降至胸部，然后用力推起",
                "form_cues": ["肩胛骨收紧", "核心保持稳定", "控制下降速度"],
                "common_mistakes": ["弓背过度", "杠铃路径不直", "下降不充分"],
                "safety_tips": ["使用安全杠", "有人保护", "充分热身"],
            },
            {
                "name": "哑铃卧推",
                "english_name": "Dumbbell Bench Press",
                "body_parts": ["chest"],
                "primary_muscles": ["chest"],
                "secondary_muscles": ["shoulders_front", "triceps"],
                "exercise_type": "compound",
                "difficulty": "beginner",
                "equipment": ["哑铃"],
                "description": "使用哑铃进行的卧推动作，活动范围更大",
                "instructions": "仰卧持哑铃，双臂伸直，缓慢下降至胸部两侧，然后推起至起始位置",
                "form_cues": ["保持哑铃平衡", "肘部适度内收", "顶部不要碰撞"],
                "common_mistakes": ["哑铃下降过低", "速度过快", "两臂不平衡"],
                "safety_tips": ["选择适当重量", "控制动作幅度", "注意哑铃平衡"],
            },
        ]

        # 背部动作
        back_exercises = [
            {
                "name": "引体向上",
                "english_name": "Pull-up",
                "body_parts": ["back"],
                "primary_muscles": ["back_lat"],
                "secondary_muscles": ["biceps", "shoulders_rear"],
                "exercise_type": "compound",
                "difficulty": "intermediate",
                "equipment": ["引体向上杆"],
                "description": "上肢训练的经典动作，主要锻炼背阔肌",
                "instructions": "悬挂在单杠上，双手正握，身体向上拉至下巴超过杠子",
                "form_cues": ["肩胛骨下沉", "核心收紧", "避免摆动"],
                "common_mistakes": ["借助摆动", "动作幅度不足", "下降过快"],
                "safety_tips": ["充分热身肩部", "循序渐进", "使用辅助带"],
            },
            {
                "name": "杠铃划船",
                "english_name": "Barbell Row",
                "body_parts": ["back"],
                "primary_muscles": ["back_lat", "back_rhomboid"],
                "secondary_muscles": ["biceps", "shoulders_rear"],
                "exercise_type": "compound",
                "difficulty": "intermediate",
                "equipment": ["杠铃"],
                "description": "背部厚度训练的重要动作",
                "instructions": "俯身持杠铃，保持背部挺直，将杠铃拉至腹部",
                "form_cues": ["背部保持中立", "肩胛骨收缩", "肘部贴近身体"],
                "common_mistakes": ["弓背", "借助惯性", "肘部外展过度"],
                "safety_tips": ["保持核心稳定", "选择合适重量", "避免圆背"],
            },
        ]

        # 合并所有动作数据
        all_exercises = chest_exercises + back_exercises

        for exercise_data in all_exercises:
            # 处理关联字段
            body_part_names = exercise_data.pop("body_parts")
            primary_muscle_names = exercise_data.pop("primary_muscles")
            secondary_muscle_names = exercise_data.pop("secondary_muscles")
            equipment_names = exercise_data.pop("equipment")

            exercise, created = Exercise.objects.get_or_create(name=exercise_data["name"], defaults=exercise_data)

            if created:
                self.stdout.write(f"创建动作: {exercise.name}")

                # 设置关联关系
                body_parts = BodyPart.objects.filter(name__in=body_part_names)
                exercise.body_parts.set(body_parts)

                primary_muscles = MuscleGroup.objects.filter(name__in=primary_muscle_names)
                exercise.primary_muscles.set(primary_muscles)

                secondary_muscles = MuscleGroup.objects.filter(name__in=secondary_muscle_names)
                exercise.secondary_muscles.set(secondary_muscles)

                equipment = Equipment.objects.filter(name__in=equipment_names)
                exercise.equipment.set(equipment)

    def create_achievements(self):
        """创建成就数据"""
        # 力量训练成就
        strength_module = FitnessAchievementModule.objects.get(name="strength")
        strength_achievements = [
            {
                "name": "力量新手",
                "description": "完成第一次力量训练",
                "level": "bronze",
                "rarity": "common",
                "icon": "fas fa-dumbbell",
                "badge_color": "#cd7f32",
                "unlock_condition": {"exercise_count": 1},
                "points_reward": 10,
            },
            {
                "name": "卧推达人",
                "description": "卧推重量达到体重的1倍",
                "level": "silver",
                "rarity": "rare",
                "icon": "fas fa-medal",
                "badge_color": "#c0c0c0",
                "unlock_condition": {"exercise_type": "bench_press", "max_weight": 70},
                "points_reward": 50,
            },
            {
                "name": "力量之王",
                "description": "三大项总重量达到400kg",
                "level": "gold",
                "rarity": "epic",
                "icon": "fas fa-crown",
                "badge_color": "#ffd700",
                "unlock_condition": {"total_1rm": 400},
                "points_reward": 100,
            },
        ]

        # 连续性成就
        consistency_module = FitnessAchievementModule.objects.get(name="consistency")
        consistency_achievements = [
            {
                "name": "坚持一周",
                "description": "连续训练7天",
                "level": "bronze",
                "rarity": "common",
                "icon": "fas fa-calendar-week",
                "badge_color": "#cd7f32",
                "unlock_condition": {"streak_days": 7},
                "points_reward": 25,
            },
            {
                "name": "月度战士",
                "description": "连续训练30天",
                "level": "gold",
                "rarity": "rare",
                "icon": "fas fa-fire",
                "badge_color": "#ffd700",
                "unlock_condition": {"streak_days": 30},
                "points_reward": 100,
            },
        ]

        # 有氧运动成就
        cardio_module = FitnessAchievementModule.objects.get(name="cardio")
        cardio_achievements = [
            {
                "name": "有氧初体验",
                "description": "完成第一次有氧训练",
                "level": "bronze",
                "rarity": "common",
                "icon": "fas fa-running",
                "badge_color": "#cd7f32",
                "unlock_condition": {"cardio_sessions": 1},
                "points_reward": 10,
            },
            {
                "name": "耐力达人",
                "description": "累计有氧训练时间达到1000分钟",
                "level": "silver",
                "rarity": "rare",
                "icon": "fas fa-stopwatch",
                "badge_color": "#c0c0c0",
                "unlock_condition": {"total_cardio_duration": 1000},
                "points_reward": 75,
            },
        ]

        # 合并所有成就
        all_achievements = [
            (strength_module, strength_achievements),
            (consistency_module, consistency_achievements),
            (cardio_module, cardio_achievements),
        ]

        for module, achievements in all_achievements:
            for achievement_data in achievements:
                achievement, created = EnhancedFitnessAchievement.objects.get_or_create(
                    module=module, name=achievement_data["name"], defaults=achievement_data
                )
                if created:
                    self.stdout.write(f"创建成就: {achievement.name}")

    def create_plan_categories(self):
        """创建训练计划分类"""
        categories_data = [
            {"name": "力量训练", "description": "专注于力量提升的训练计划", "icon": "fas fa-dumbbell", "color": "#e74c3c"},
            {
                "name": "增肌训练",
                "description": "以肌肉增长为目标的训练计划",
                "icon": "fas fa-fist-raised",
                "color": "#3498db",
            },
            {"name": "减脂训练", "description": "燃脂塑形的综合训练计划", "icon": "fas fa-fire", "color": "#e67e22"},
            {"name": "功能性训练", "description": "提升日常功能性的训练计划", "icon": "fas fa-running", "color": "#27ae60"},
            {"name": "康复训练", "description": "伤后恢复和预防的训练计划", "icon": "fas fa-heart", "color": "#9b59b6"},
        ]

        for category_data in categories_data:
            category, created = TrainingPlanCategory.objects.get_or_create(name=category_data["name"], defaults=category_data)
            if created:
                self.stdout.write(f"创建计划分类: {category.name}")
