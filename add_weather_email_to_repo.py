#!/usr/bin/env python3
"""
Script to add weather email files to your existing GitHub repository
This will automatically trigger a deployment on Render
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        print(f"✅ {cmd}")
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    print("🚀 Adding Daily Weather Email Service to your GitHub repository...")
    print("📧 This will enable automatic emails to suryakumar56394@gmail.com and monikam11g1@gmail.com")
    print("⏰ Schedule: 6:00 AM and 7:00 PM IST daily")
    print("")
    
    # Clone the repository
    repo_dir = "../smart-irrigation-AI-update"
    if os.path.exists(repo_dir):
        print("🗂️ Removing existing directory...")
        run_command(f"rm -rf {repo_dir}")
    
    print("📥 Cloning your repository...")
    if not run_command(f"git clone https://github.com/tnsurya7/smart-irrigation-AI.git {repo_dir}"):
        sys.exit(1)
    
    # Copy weather email files
    print("📁 Copying weather email service files...")
    files_to_copy = [
        "daily_weather_email_service.py",
        "auto_start_weather_emails.py", 
        "send_test_emails.py",
        "render_weather_email_service.py",
        "WEATHER_EMAIL_SUMMARY.md",
        "RENDER_INTEGRATION_GUIDE.md"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            run_command(f"cp {file} {repo_dir}/")
            print(f"✅ Copied {file}")
        else:
            print(f"⚠️ File not found: {file}")
    
    # Modify backend.py to add weather email integration
    backend_file = f"{repo_dir}/backend.py"
    if os.path.exists(backend_file):
        print("🔧 Adding weather email integration to backend.py...")
        
        with open(backend_file, 'r') as f:
            content = f.read()
        
        # Add the integration at the end
        integration_code = '''
# Auto-start Daily Weather Email Service
# This will send emails to suryakumar56394@gmail.com and monikam11g1@gmail.com
# at 6:00 AM and 7:00 PM IST daily with weather updates for Erode, Tamil Nadu
try:
    import auto_start_weather_emails
    print("✅ Daily Weather Email Service integrated successfully")
except Exception as e:
    print(f"⚠️ Weather email service not available: {e}")
    print("⚠️ Main application continues normally")
'''
        
        if "auto_start_weather_emails" not in content:
            content += integration_code
            
            with open(backend_file, 'w') as f:
                f.write(content)
            print("✅ Backend.py updated with weather email integration")
        else:
            print("✅ Weather email integration already exists in backend.py")
    
    # Update requirements.txt
    requirements_file = f"{repo_dir}/requirements.txt"
    if os.path.exists(requirements_file):
        print("📦 Updating requirements.txt...")
        
        with open(requirements_file, 'r') as f:
            requirements = f.read()
        
        # Add schedule dependency if not present
        if "schedule" not in requirements:
            requirements += "\nschedule==1.2.2"
            
            with open(requirements_file, 'w') as f:
                f.write(requirements)
            print("✅ Added schedule dependency to requirements.txt")
    
    # Commit and push changes
    print("📤 Committing and pushing changes to GitHub...")
    
    os.chdir(repo_dir)
    
    run_command("git add .")
    run_command('git commit -m "🌱 Add Daily Weather Email Service - Automated emails at 6AM & 7PM IST to suryakumar56394@gmail.com and monikam11g1@gmail.com with weather updates for Erode, Tamil Nadu"')
    
    if run_command("git push origin main"):
        print("")
        print("🎉 SUCCESS! Weather Email Service added to your repository!")
        print("🚀 Render will automatically deploy the changes")
        print("")
        print("📧 Email Configuration:")
        print("   - Recipients: suryakumar56394@gmail.com, monikam11g1@gmail.com")
        print("   - Schedule: 6:00 AM and 7:00 PM IST daily")
        print("   - Location: Erode, Tamil Nadu")
        print("   - Sender: suryakumar56394@gmail.com")
        print("")
        print("⏰ Expected deployment time: 2-3 minutes")
        print("📊 Monitor deployment: https://dashboard.render.com/")
        print("")
        print("✅ The service will start automatically after deployment!")
    else:
        print("❌ Failed to push changes to GitHub")
        sys.exit(1)
    
    # Cleanup
    os.chdir("..")
    run_command(f"rm -rf {repo_dir}")
    print("🧹 Cleanup completed")

if __name__ == "__main__":
    main()