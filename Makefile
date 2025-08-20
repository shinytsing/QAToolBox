.PHONY: help install test lint format clean build deploy dev prod

# 默认目标
help:
	@echo "可用的命令:"
	@echo "  install    - 安装依赖"
	@echo "  test       - 运行测试"
	@echo "  lint       - 代码检查"
	@echo "  format     - 代码格式化"
	@echo "  clean      - 清理临时文件"
	@echo "  build      - 构建Docker镜像"
	@echo "  deploy     - 部署到生产环境"
	@echo "  dev        - 启动开发环境"
	@echo "  prod       - 启动生产环境"

# 安装依赖
install:
	pip install -r requirements/base.txt
	pip install -r requirements/dev.txt

# 运行测试
test:
	python manage.py test --verbosity=2
	coverage run --source='.' manage.py test
	coverage report
	coverage html

# 代码检查
lint:
	flake8 .
	black --check --diff .
	isort --check-only --diff .
	mypy apps/ --ignore-missing-imports
	bandit -r apps/ -f json -o bandit-report.json || true
	safety check

# 代码格式化
format:
	black .
	isort .

# 清理临时文件
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov dist build *.egg-info
	rm -rf staticfiles media

# 构建Docker镜像
build:
	docker build -t qatoolbox:latest .

# 构建生产镜像
build-prod:
	docker build --target production -t qatoolbox:prod .

# 启动开发环境
dev:
	docker-compose -f docker-compose.yml up --build

# 启动生产环境
prod:
	docker-compose -f docker-compose.yml up -d

# 停止服务
stop:
	docker-compose down

# 查看日志
logs:
	docker-compose logs -f

# 数据库迁移
migrate:
	python manage.py makemigrations
	python manage.py migrate

# 创建超级用户
superuser:
	python manage.py createsuperuser

# 收集静态文件
collectstatic:
	python manage.py collectstatic --noinput

# 备份数据库
backup:
	python manage.py dumpdata > backup_$(shell date +%Y%m%d_%H%M%S).json

# 恢复数据库
restore:
	python manage.py loaddata backup_*.json

# 检查依赖安全漏洞
security:
	safety check
	bandit -r apps/ -f json -o bandit-report.json
	@echo "安全检查完成，查看 bandit-report.json 获取详细信息"

# 性能测试
perf:
	python manage.py test --tag=performance

# 代码覆盖率报告
coverage:
	coverage run --source='.' manage.py test
	coverage report
	coverage html
	@echo "覆盖率报告已生成，打开 htmlcov/index.html 查看详细信息"

# 部署到测试环境
deploy-staging:
	@echo "部署到测试环境..."
	# 这里添加部署脚本

# 部署到生产环境
deploy-production:
	@echo "部署到生产环境..."
	# 这里添加部署脚本

# 快速开发设置
setup-dev:
	pip install -r requirements/dev.txt
	python manage.py migrate
	python manage.py collectstatic --noinput
	@echo "开发环境设置完成！"

# 检查代码质量
quality:
	@echo "运行代码质量检查..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	black --check --diff .
	isort --check-only --diff .
	mypy apps/ --ignore-missing-imports
	@echo "代码质量检查完成！"
