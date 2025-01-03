#!/bin/bash
export PYTHONPATH=/usr/local/lib/python3.10/site-packages:$PYTHONPATH

# 生成迁移脚本
echo "生成数据库迁移脚本..."
python -m flask db migrate

# 检查是否有待应用的数据库迁移
MIGRATIONS=$(python -m flask db current)
if [ -n "$MIGRATIONS" ]; then
    # 如果有待应用的迁移，执行迁移
    echo "检测到数据库变更，正在应用迁移..."
    python -m flask db upgrade
else
    echo "数据库已是最新，无需迁移"
fi

# 启动 Flask 应用
python app.py