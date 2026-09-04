#!/bin/bash
set -e

# 兜底保证 app 包可被导入：alembic 命令行脚本不会自动把工作目录加入 sys.path，
# 且 Railway 不一定传递 Dockerfile 的 ENV，这里显式设置 CWD 与 PYTHONPATH。
cd /app
export PYTHONPATH="/app:${PYTHONPATH}"

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
