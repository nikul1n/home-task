import os
import subprocess
import sys
import time
from pathlib import Path

env_file = Path(__file__).resolve().parent.parent / ".env"
env_vars = os.environ.copy()

if env_file.exists():
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip().strip('"').strip("'")

MESSAGE = sys.argv[1] if len(sys.argv) > 1 else "auto_migration"
PORT = "5439"
USER = env_vars.get("POSTGRES_USER", "postgres")
PASSWORD = env_vars.get("POSTGRES_PASSWORD", "postgres")
DB_NAME = env_vars.get("POSTGRES_DB", "temp_db")
CONTAINER = f"alembic-temp-pg-{os.getpid()}"

env_vars["DATABASE_URL"] = f"postgresql+asyncpg://{USER}:{PASSWORD}@localhost:{PORT}/{DB_NAME}"

try:
    print(f"Starting PostgreSQL ({USER}@localhost:{PORT}/{DB_NAME})...")
    subprocess.run([
        "docker", "run", "-d",
        "--name", CONTAINER,
        "-p", f"{PORT}:5432",
        "-e", f"POSTGRES_USER={USER}",
        "-e", f"POSTGRES_PASSWORD={PASSWORD}",
        "-e", f"POSTGRES_DB={DB_NAME}",
        "--tmpfs", "/var/lib/postgresql/data",
        "postgres:16-alpine"
    ], check=True, stdout=subprocess.DEVNULL)

    while True:
        res = subprocess.run(
            ["docker", "exec", CONTAINER, "pg_isready", "-h", "127.0.0.1", "-U", USER, "-d", DB_NAME],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if res.returncode == 0:
            break
        time.sleep(0.3)

    print("alembic upgrade head...")
    subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True, env=env_vars)

    print(f"alembic revision --autogenerate -m '{MESSAGE}'...")
    subprocess.run(["uv", "run", "alembic", "revision", "--autogenerate", "-m", MESSAGE], check=True, env=env_vars)
    print("Done!")

finally:
    print("Cleaning up container...")
    subprocess.run(["docker", "rm", "-f", "-v", CONTAINER], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)