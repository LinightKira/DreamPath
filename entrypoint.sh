#!/bin/bash

# 运行数据库迁移
flask db migrate

# 应用数据库迁移
flask db upgrade

# 启动 Flask 应用
python app.py
