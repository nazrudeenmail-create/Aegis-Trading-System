import os
import sys
import subprocess

def run_command(command, cwd=None):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        sys.exit(1)

def main():
    print("==================================================")
    print("ATS Developer Environment Bootstrap")
    print("==================================================")

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    backend_dir = os.path.join(root_dir, 'backend')
    
    # Check if database is reachable
    print("\n[1/4] Verifying database connection...")
    sys.path.insert(0, backend_dir)
    try:
        from app.database.connection import verify_database_connection
        if not verify_database_connection():
            print("❌ Cannot connect to database. Ensure Docker/PostgreSQL is running.")
            sys.exit(1)
        print("✅ Database connected.")
    except Exception as e:
        print(f"❌ Failed to verify database connection: {e}")
        sys.exit(1)
    
    print("\n[2/4] Running database migrations...")
    run_command("alembic upgrade head", cwd=backend_dir)
    print("✅ Migrations completed.")
    
    print("\n[3/4] Running system seed scripts...")
    scripts_dir = os.path.join(root_dir, 'scripts')
    run_command(f"{sys.executable} {os.path.join(scripts_dir, 'seed_settings.py')}")
    run_command(f"{sys.executable} {os.path.join(scripts_dir, 'seed_user.py')}")
    print("✅ System data seeded.")
    
    print("\n[4/4] System ready.")
    print("==================================================")
    print("Your ATS development environment is fully synchronized!")

if __name__ == "__main__":
    main()
