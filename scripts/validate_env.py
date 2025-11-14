"""Environment variable validator for FitRecs."""
import os
import sys
from typing import Dict, List, Optional

def validate_env_vars(env_file: str, required_vars: List[str]) -> Dict[str, Optional[str]]:
    """Validate environment variables from a .env file."""
    missing_vars = []
    invalid_vars = []
    env_values = {}

    if not os.path.exists(env_file):
        print(f"[ERROR] {env_file} not found")
        return {}

    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    env_values[key] = value
                except ValueError:
                    continue

    for var in required_vars:
        if var not in env_values:
            missing_vars.append(var)
        elif not env_values[var] or env_values[var] == f"your-{var.lower()}-here":
            invalid_vars.append(var)

    if missing_vars:
        print(f"\n[ERROR] Missing environment variables in {env_file}:")
        for var in missing_vars:
            print(f"  - {var}")

    if invalid_vars:
        print(f"\n[WARNING] Invalid or empty environment variables in {env_file}:")
        for var in invalid_vars:
            print(f"  - {var}")

    return env_values

def main():
    """Main validation function."""
    print("Validating environment variables...")
    
    # Root .env variables
    root_vars = ["OPENAI_API_KEY"]
    root_env = validate_env_vars(".env", root_vars)
    
    # Backend .env variables
    backend_vars = [
        "POSTGRES_SERVER",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "SECRET_KEY",
        "BACKEND_CORS_ORIGINS"
    ]
    backend_env = validate_env_vars("backend/.env", backend_vars)
    
    # Frontend .env variables
    frontend_vars = [
        "VITE_API_URL",
        "VITE_ENABLE_AI_FEATURES"
    ]
    frontend_env = validate_env_vars("frontend/.env", frontend_vars)
    
    all_ok = (
        len(root_env) == len(root_vars) and
        len(backend_env) == len(backend_vars) and
        len(frontend_env) == len(frontend_vars)
    )
    
    if all_ok:
        print("\n[OK] All environment variables are properly configured")
        sys.exit(0)
    else:
        print("\n[ERROR] Please fix the environment variables before starting")
        sys.exit(1)

if __name__ == "__main__":
    main()