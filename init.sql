-- PostgreSQL初始化脚本
-- 创建数据库和用户（如果不存在）

-- 创建数据库
CREATE DATABASE qatoolbox_production;

-- 创建用户
CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE qatoolbox_production TO qatoolbox;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO qatoolbox;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO qatoolbox;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO qatoolbox;

-- 设置时区
SET timezone = 'Asia/Shanghai';
