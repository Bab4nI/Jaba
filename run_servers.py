import os
import platform
import subprocess

def run_in_new_terminal(command, directory):
    if platform.system() == "Windows":
        subprocess.Popen(f'start powershell -NoExit -Command "cd \\"{directory}\\"; {command}"', shell=True)
    elif platform.system() == "Linux":
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'cd "{directory}" && {command}; exec bash'])
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(['osascript', '-e', f'tell app "Terminal" to do script "cd \\"{directory}\\" && {command}"'])

# Запуск серверов
run_in_new_terminal("python manage.py runserver", "backend/main")
run_in_new_terminal("npm run dev", 'frontend/jaba script')