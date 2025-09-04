# QAToolbox/apps/tools/admin_nutrition.py
"""
营养信息模型的Django管理后台配置
"""

from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import FoodNutrition, FoodNutritionHistory, FoodRandomizationLog, NutritionCategory


@admin.register(NutritionCategory)
class NutritionCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "unit", "daily_value", "description"]
    search_fields = ["name", "description"]
    list_filter = ["unit"]
    ordering = ["name"]


@admin.register(FoodNutrition)
class FoodNutritionAdmin(admin.ModelAdmin):
    list_display = ["name", "cuisine", "meal_type", "calories", "health_score", "popularity_score", "is_active", "created_at"]
    list_filter = [
        "cuisine",
        "meal_type",
        "difficulty",
        "is_active",
        "is_vegetarian",
        "is_vegan",
        "is_high_protein",
        "is_low_carb",
        "is_gluten_free",
    ]
    search_fields = ["name", "english_name", "description"]
    readonly_fields = ["created_at", "updated_at", "macronutrients_display", "nutrition_summary_display"]

    fieldsets = (
        ("基本信息", {"fields": ("name", "english_name", "description", "cuisine", "meal_type")}),
        ("制作信息", {"fields": ("difficulty", "cooking_time", "serving_size")}),
        (
            "主要营养成分",
            {"fields": ("calories", "protein", "fat", "carbohydrates", "dietary_fiber", "sugar"), "classes": ["collapse"]},
        ),
        (
            "详细营养成分",
            {
                "fields": (
                    "saturated_fat",
                    "trans_fat",
                    "cholesterol",
                    "sodium",
                    "potassium",
                    "vitamin_a",
                    "vitamin_c",
                    "vitamin_d",
                    "vitamin_e",
                    "vitamin_k",
                    "thiamine_b1",
                    "riboflavin_b2",
                    "niacin_b3",
                    "vitamin_b6",
                    "folate_b9",
                    "vitamin_b12",
                    "calcium",
                    "iron",
                    "magnesium",
                    "phosphorus",
                    "zinc",
                    "copper",
                    "manganese",
                    "selenium",
                ),
                "classes": ["collapse"],
            },
        ),
        ("食材和标签", {"fields": ("ingredients", "allergens", "tags")}),
        (
            "健康信息",
            {
                "fields": (
                    "is_vegetarian",
                    "is_vegan",
                    "is_gluten_free",
                    "is_dairy_free",
                    "is_low_carb",
                    "is_high_protein",
                    "is_low_fat",
                    "is_organic",
                )
            },
        ),
        ("评分和媒体", {"fields": ("health_score", "popularity_score", "image_url", "recipe_url")}),
        ("系统信息", {"fields": ("is_active", "created_by", "created_at", "updated_at"), "classes": ["collapse"]}),
        ("营养摘要", {"fields": ("macronutrients_display", "nutrition_summary_display"), "classes": ["collapse"]}),
    )

    actions = ["make_active", "make_inactive", "update_popularity"]

    def macronutrients_display(self, obj):
        """显示宏量营养素比例"""
        ratios = obj.get_macronutrients_ratio()
        return format_html(
            '<div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">'
            "<strong>宏量营养素比例:</strong><br>"
            "🍖 蛋白质: {protein}%<br>"
            "🧈 脂肪: {fat}%<br>"
            "🍞 碳水: {carbs}%"
            "</div>",
            protein=ratios["protein"],
            fat=ratios["fat"],
            carbs=ratios["carbs"],
        )

    macronutrients_display.short_description = "宏量营养素比例"

    def nutrition_summary_display(self, obj):
        """显示营养摘要"""
        summary = obj.get_nutrition_summary()
        return format_html(
            '<div style="background: #e8f5e8; padding: 10px; border-radius: 5px;">'
            "<strong>营养摘要 (每份):</strong><br>"
            "⚡ 热量: {calories} kcal<br>"
            "🍖 蛋白质: {protein}g<br>"
            "🧈 脂肪: {fat}g<br>"
            "🍞 碳水: {carbohydrates}g<br>"
            "🌾 纤维: {fiber}g<br>"
            "🧂 钠: {sodium}mg"
            "</div>",
            calories=int(summary["calories"]),
            protein=summary["protein"],
            fat=summary["fat"],
            carbohydrates=summary["carbohydrates"],
            fiber=summary["fiber"],
            sodium=int(summary["sodium"]),
        )

    nutrition_summary_display.short_description = "营养摘要"

    def make_active(self, request, queryset):
        """批量激活食物"""
        count = queryset.update(is_active=True)
        self.message_user(request, f"成功激活 {count} 个食物项目")

    make_active.short_description = "激活选中的食物"

    def make_inactive(self, request, queryset):
        """批量停用食物"""
        count = queryset.update(is_active=False)
        self.message_user(request, f"成功停用 {count} 个食物项目")

    make_inactive.short_description = "停用选中的食物"

    def update_popularity(self, request, queryset):
        """更新受欢迎度"""
        for food in queryset:
            # 基于推荐次数更新受欢迎度
            recommendation_count = food.foodrandomizationlog_set.count()
            rating_avg = (
                food.foodrandomizationlog_set.filter(rating__isnull=False).aggregate(avg_rating=models.Avg("rating"))[
                    "avg_rating"
                ]
                or 0
            )

            # 计算新的受欢迎度分数
            new_score = min(10.0, (recommendation_count * 0.1) + (rating_avg * 2))
            food.popularity_score = round(new_score, 1)
            food.save(update_fields=["popularity_score"])

        count = queryset.count()
        self.message_user(request, f"成功更新 {count} 个食物的受欢迎度")

    update_popularity.short_description = "更新受欢迎度分数"


@admin.register(FoodNutritionHistory)
class FoodNutritionHistoryAdmin(admin.ModelAdmin):
    list_display = ["food", "user", "serving_amount", "rating", "consumed_at"]
    list_filter = ["rating", "consumed_at", "food__cuisine"]
    search_fields = ["food__name", "user__username", "notes"]
    readonly_fields = ["consumed_at", "total_nutrition_display"]
    raw_id_fields = ["food", "user"]

    fieldsets = (
        ("基本信息", {"fields": ("food", "user", "serving_amount", "rating")}),
        ("时间和备注", {"fields": ("consumed_at", "notes")}),
        ("营养计算", {"fields": ("total_nutrition_display",), "classes": ["collapse"]}),
    )

    def total_nutrition_display(self, obj):
        """显示总营养摄入"""
        if obj.pk:
            nutrition = obj.get_total_nutrition()
            return format_html(
                '<div style="background: #fff3cd; padding: 10px; border-radius: 5px;">'
                "<strong>总营养摄入 ({serving}份):</strong><br>"
                "⚡ 热量: {calories} kcal<br>"
                "🍖 蛋白质: {protein}g<br>"
                "🧈 脂肪: {fat}g<br>"
                "🍞 碳水: {carbohydrates}g<br>"
                "🌾 纤维: {fiber}g<br>"
                "🧂 钠: {sodium}mg"
                "</div>",
                serving=obj.serving_amount,
                calories=int(nutrition["calories"]),
                protein=round(nutrition["protein"], 1),
                fat=round(nutrition["fat"], 1),
                carbohydrates=round(nutrition["carbohydrates"], 1),
                fiber=round(nutrition["fiber"], 1),
                sodium=int(nutrition["sodium"]),
            )
        return "-"

    total_nutrition_display.short_description = "总营养摄入"


@admin.register(FoodRandomizationLog)
class FoodRandomizationLogAdmin(admin.ModelAdmin):
    list_display = ["food", "user", "cuisine_filter", "meal_type_filter", "selected", "rating", "created_at"]
    list_filter = ["selected", "rating", "cuisine_filter", "meal_type_filter", "created_at"]
    search_fields = ["food__name", "user__username", "session_id"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["food", "user"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("推荐信息", {"fields": ("food", "user", "session_id")}),
        ("筛选条件", {"fields": ("cuisine_filter", "meal_type_filter")}),
        ("用户反馈", {"fields": ("selected", "rating")}),
        ("时间信息", {"fields": ("created_at",)}),
    )

    actions = ["mark_as_selected", "export_recommendations"]

    def mark_as_selected(self, request, queryset):
        """标记为已选择"""
        count = queryset.update(selected=True)
        self.message_user(request, f"成功标记 {count} 条记录为已选择")

    mark_as_selected.short_description = "标记为已选择"

    def export_recommendations(self, request, queryset):
        """导出推荐数据"""
        # 这里可以实现CSV导出功能
        count = queryset.count()
        self.message_user(request, f"准备导出 {count} 条推荐记录（功能待实现）")

    export_recommendations.short_description = "导出推荐数据"


# 在主admin.py中注册或导入这些配置
