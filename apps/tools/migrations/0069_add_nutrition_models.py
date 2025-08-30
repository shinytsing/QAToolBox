# Generated manually for nutrition models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0068_auto_20250828_2300'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NutritionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='类别名称')),
                ('description', models.TextField(blank=True, null=True, verbose_name='描述')),
                ('unit', models.CharField(max_length=20, verbose_name='单位')),
                ('daily_value', models.FloatField(blank=True, null=True, verbose_name='每日推荐值')),
            ],
            options={
                'verbose_name': '营养成分类别',
                'verbose_name_plural': '营养成分类别',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FoodNutrition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='食物名称')),
                ('english_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='英文名称')),
                ('description', models.TextField(blank=True, null=True, verbose_name='描述')),
                ('cuisine', models.CharField(choices=[('chinese', '中餐'), ('italian', '意大利菜'), ('japanese', '日料'), ('american', '美式'), ('french', '法餐'), ('korean', '韩料'), ('healthy', '健康餐'), ('indian', '印度菜'), ('mexican', '墨西哥菜'), ('thai', '泰餐'), ('mixed', '混合菜系')], max_length=20, verbose_name='菜系')),
                ('meal_type', models.CharField(choices=[('breakfast', '早餐'), ('main', '主食'), ('appetizer', '开胃菜'), ('dessert', '甜点'), ('drink', '饮品'), ('snack', '零食'), ('lunch', '午餐'), ('dinner', '晚餐')], max_length=20, verbose_name='餐型')),
                ('difficulty', models.IntegerField(choices=[(1, '非常简单'), (2, '简单'), (3, '中等'), (4, '困难'), (5, '非常困难')], default=3, verbose_name='制作难度')),
                ('cooking_time', models.IntegerField(default=30, verbose_name='制作时间(分钟)')),
                ('serving_size', models.FloatField(default=100, verbose_name='参考份量(克)')),
                ('calories', models.FloatField(default=0, verbose_name='卡路里(kcal)')),
                ('protein', models.FloatField(default=0, verbose_name='蛋白质(g)')),
                ('fat', models.FloatField(default=0, verbose_name='脂肪(g)')),
                ('saturated_fat', models.FloatField(default=0, verbose_name='饱和脂肪(g)')),
                ('trans_fat', models.FloatField(default=0, verbose_name='反式脂肪(g)')),
                ('cholesterol', models.FloatField(default=0, verbose_name='胆固醇(mg)')),
                ('carbohydrates', models.FloatField(default=0, verbose_name='碳水化合物(g)')),
                ('dietary_fiber', models.FloatField(default=0, verbose_name='膳食纤维(g)')),
                ('sugar', models.FloatField(default=0, verbose_name='糖分(g)')),
                ('sodium', models.FloatField(default=0, verbose_name='钠(mg)')),
                ('potassium', models.FloatField(default=0, verbose_name='钾(mg)')),
                ('vitamin_a', models.FloatField(default=0, verbose_name='维生素A(μg)')),
                ('vitamin_c', models.FloatField(default=0, verbose_name='维生素C(mg)')),
                ('vitamin_d', models.FloatField(default=0, verbose_name='维生素D(μg)')),
                ('vitamin_e', models.FloatField(default=0, verbose_name='维生素E(mg)')),
                ('vitamin_k', models.FloatField(default=0, verbose_name='维生素K(μg)')),
                ('thiamine_b1', models.FloatField(default=0, verbose_name='维生素B1(mg)')),
                ('riboflavin_b2', models.FloatField(default=0, verbose_name='维生素B2(mg)')),
                ('niacin_b3', models.FloatField(default=0, verbose_name='维生素B3(mg)')),
                ('vitamin_b6', models.FloatField(default=0, verbose_name='维生素B6(mg)')),
                ('folate_b9', models.FloatField(default=0, verbose_name='叶酸(μg)')),
                ('vitamin_b12', models.FloatField(default=0, verbose_name='维生素B12(μg)')),
                ('calcium', models.FloatField(default=0, verbose_name='钙(mg)')),
                ('iron', models.FloatField(default=0, verbose_name='铁(mg)')),
                ('magnesium', models.FloatField(default=0, verbose_name='镁(mg)')),
                ('phosphorus', models.FloatField(default=0, verbose_name='磷(mg)')),
                ('zinc', models.FloatField(default=0, verbose_name='锌(mg)')),
                ('copper', models.FloatField(default=0, verbose_name='铜(mg)')),
                ('manganese', models.FloatField(default=0, verbose_name='锰(mg)')),
                ('selenium', models.FloatField(default=0, verbose_name='硒(μg)')),
                ('ingredients', models.JSONField(default=list, verbose_name='主要食材')),
                ('allergens', models.JSONField(default=list, verbose_name='过敏原')),
                ('tags', models.JSONField(default=list, verbose_name='标签')),
                ('is_vegetarian', models.BooleanField(default=False, verbose_name='素食')),
                ('is_vegan', models.BooleanField(default=False, verbose_name='严格素食')),
                ('is_gluten_free', models.BooleanField(default=False, verbose_name='无麸质')),
                ('is_dairy_free', models.BooleanField(default=False, verbose_name='无乳制品')),
                ('is_low_carb', models.BooleanField(default=False, verbose_name='低碳水')),
                ('is_high_protein', models.BooleanField(default=False, verbose_name='高蛋白')),
                ('is_low_fat', models.BooleanField(default=False, verbose_name='低脂')),
                ('is_organic', models.BooleanField(default=False, verbose_name='有机')),
                ('image_url', models.URLField(blank=True, null=True, verbose_name='图片链接')),
                ('recipe_url', models.URLField(blank=True, null=True, verbose_name='食谱链接')),
                ('popularity_score', models.FloatField(default=0, verbose_name='受欢迎度')),
                ('health_score', models.IntegerField(default=50, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='健康评分(0-100)')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
            ],
            options={
                'verbose_name': '食物营养信息',
                'verbose_name_plural': '食物营养信息',
                'ordering': ['-popularity_score', 'name'],
            },
        ),
        migrations.CreateModel(
            name='FoodNutritionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consumed_at', models.DateTimeField(auto_now_add=True, verbose_name='食用时间')),
                ('serving_amount', models.FloatField(default=1.0, verbose_name='食用份数')),
                ('rating', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='评分(1-5)')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tools.foodnutrition', verbose_name='食物')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '食物历史记录',
                'verbose_name_plural': '食物历史记录',
                'ordering': ['-consumed_at'],
            },
        ),
        migrations.CreateModel(
            name='FoodRandomizationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=100, verbose_name='会话ID')),
                ('cuisine_filter', models.CharField(blank=True, max_length=20, null=True, verbose_name='菜系筛选')),
                ('meal_type_filter', models.CharField(blank=True, max_length=20, null=True, verbose_name='餐型筛选')),
                ('selected', models.BooleanField(default=False, verbose_name='是否被选择')),
                ('rating', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='评分')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='推荐时间')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tools.foodnutrition', verbose_name='推荐食物')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '随机化记录',
                'verbose_name_plural': '随机化记录',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='foodnutrition',
            index=models.Index(fields=['cuisine', 'meal_type'], name='tools_foodn_cuisine_013aa2_idx'),
        ),
        migrations.AddIndex(
            model_name='foodnutrition',
            index=models.Index(fields=['is_active', 'popularity_score'], name='tools_foodn_is_acti_64ae1d_idx'),
        ),
        migrations.AddIndex(
            model_name='foodnutrition',
            index=models.Index(fields=['name'], name='tools_foodn_name_0a44e1_idx'),
        ),
    ]