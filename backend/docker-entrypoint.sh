#!/bin/bash
set -e

# 兜底保证 app 包可被导入：alembic 命令行脚本不会自动把工作目录加入 sys.path，
# 且 Railway 不一定传递 Dockerfile 的 ENV，这里显式设置 CWD 与 PYTHONPATH。
cd /app
export PYTHONPATH="/app:${PYTHONPATH}"

echo "Running database migrations..."
alembic upgrade head

echo "Checking if seed data is needed..."
python -c "
import asyncio, sys, os
sys.path.insert(0, '/app')
os.environ.setdefault('PYTHONPATH', '/app')

async def check_and_seed():
    from sqlalchemy import text
    from app.core.database import async_session_factory
    async with async_session_factory() as session:
        result = await session.execute(text('SELECT COUNT(*) FROM skills'))
        count = result.scalar()
        if count == 0:
            print('Database is empty, seeding...')
            from app.services.ingestion.seed_data import seed_database
            await seed_database()
        else:
            print(f'Database already has {count} skills, skipping seed.')

asyncio.run(check_and_seed())
" || echo "Seed check failed (non-fatal), continuing..."

echo "Starting application..."
exec "$@"
