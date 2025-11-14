#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def find_env_vars_in_files(directory):
    env_vars = set()
    
    # Look for common env var patterns in Python files
    for filepath in Path(directory).rglob('*.py'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for os.environ, os.getenv, and settings patterns
            for line in content.split('\n'):
                if 'os.environ.get' in line or 'os.getenv' in line or 'env: str =' in line:
                    # Extract variable name
                    if 'os.environ.get' in line:
                        start = line.find('os.environ.get(') + 14
                    elif 'os.getenv' in line:
                        start = line.find('os.getenv(') + 10
                    else:
                        start = line.find('env: str =') + 10
                    
                    if start > 0:
                        end = line.find(')', start)
                        if end == -1:
                            end = line.find(',', start)
                        if end == -1:
                            continue
                            
                        var_name = line[start:end].strip('"\'')
                        if var_name:
                            env_vars.add(var_name)

    return sorted(list(env_vars))

def generate_env_example(backend_dir, frontend_dir):
    backend_vars = find_env_vars_in_files(backend_dir)
    frontend_vars = find_env_vars_in_files(frontend_dir)
    
    print("Found environment variables:")
    print("\nBackend variables:")
    for var in backend_vars:
        print(f"- {var}")
    
    print("\nFrontend variables:")
    for var in frontend_vars:
        print(f"- {var}")
    
    # Generate .env.example for backend
    with open(os.path.join(backend_dir, '.env.example'), 'w') as f:
        f.write("# Backend Environment Variables\n\n")
        f.write("# PostgreSQL Settings\n")
        f.write("POSTGRES_SERVER=db\n")
        f.write("POSTGRES_USER=postgres\n")
        f.write("POSTGRES_PASSWORD=your-db-password\n")
        f.write("POSTGRES_DB=fitrecs\n\n")
        
        f.write("# JWT Settings\n")
        f.write("SECRET_KEY=your-secret-key-at-least-32-chars\n")
        f.write("ACCESS_TOKEN_EXPIRE_MINUTES=30\n\n")
        
        f.write("# AI Settings\n")
        f.write("OPENAI_API_KEY=your-openai-api-key\n")
        f.write("AI_MODEL_NAME=gpt-4\n")
        f.write("AI_FEATURES_ENABLED=true\n\n")
        
        f.write("# Server Settings\n")
        f.write('BACKEND_CORS_ORIGINS=["http://localhost:5173"]\n')
        f.write("PROJECT_NAME=FitRecs\n")
        
        for var in backend_vars:
            if var not in [
                "POSTGRES_SERVER", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
                "SECRET_KEY", "ACCESS_TOKEN_EXPIRE_MINUTES", "OPENAI_API_KEY",
                "AI_MODEL_NAME", "AI_FEATURES_ENABLED", "BACKEND_CORS_ORIGINS",
                "PROJECT_NAME"
            ]:
                f.write(f"{var}=\n")
    
    # Generate .env.example for frontend
    with open(os.path.join(frontend_dir, '.env.example'), 'w') as f:
        f.write("# Frontend Environment Variables\n\n")
        f.write("# API Settings\n")
        f.write("VITE_API_URL=http://localhost:8000/api/v1\n\n")
        
        for var in frontend_vars:
            if var != "VITE_API_URL":
                f.write(f"{var}=\n")

if __name__ == "__main__":
    # Assuming script is in the root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, 'backend')
    frontend_dir = os.path.join(root_dir, 'frontend')
    
    generate_env_example(backend_dir, frontend_dir)
    print("\nGenerated .env.example files in backend and frontend directories")