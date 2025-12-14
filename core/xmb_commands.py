# xmb_commands.py
import os
import subprocess

class XMBCommands:
    def __init__(self, xmb_interface):
        self.xmb = xmb_interface
    
    def execute_command(self, command):
        """Выполнение команды (exe, sh файл или Steam URI)"""
        if not command:
            return
        
        try:
            print(f"Executing command: {command}")
            
            if command.startswith('steam://'):
                self._execute_steam_command(command)
            elif command.endswith('.exe'):
                self._execute_exe_command(command)
            elif command.endswith('.sh'):
                self._execute_sh_command(command)
            else:
                self._execute_generic_command(command)
                
            print(f"Command executed successfully: {command}")
        except Exception as e:
            print(f"Error executing command {command}: {e}")
    
    def _execute_steam_command(self, command):
        """Обработка Steam URI"""
        if os.name == 'nt':  # Windows
            # Способ 1: Используем os.startfile (самый надежный для Windows)
            try:
                os.startfile(command)
                print(f"Successfully opened with os.startfile: {command}")
            except Exception as e:
                print(f"os.startfile failed: {e}, trying alternative method...")
                self._execute_steam_windows_fallback(command)
        else:  # Linux
            self._execute_steam_linux(command)
    
    def _execute_steam_windows_fallback(self, command):
        """Резервные методы для Steam на Windows"""
        try:
            # Ищем Steam в типичных местах
            steam_paths = [
                os.path.join(os.environ.get('ProgramFiles', ''), 'Steam', 'steam.exe'),
                os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Steam', 'steam.exe'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'Steam', 'steam.exe')
            ]
            
            steam_exe = None
            for path in steam_paths:
                if os.path.exists(path):
                    steam_exe = path
                    break
            
            if steam_exe:
                subprocess.Popen([steam_exe, command])
                print(f"Successfully opened with Steam: {command}")
            else:
                # Способ 3: Используем rundll32 для открытия URI
                subprocess.Popen(['rundll32', 'url.dll,FileProtocolHandler', command])
                print(f"Successfully opened with rundll32: {command}")
                
        except Exception as e2:
            print(f"All Steam methods failed: {e2}")
    
    def _execute_steam_linux(self, command):
        """Обработка Steam на Linux"""
        try:
            subprocess.Popen(['xdg-open', command])
            print(f"Successfully opened with xdg-open: {command}")
        except FileNotFoundError:
            try:
                subprocess.Popen(['steam', command])
                print(f"Successfully opened with steam: {command}")
            except FileNotFoundError:
                print(f"Neither xdg-open nor steam found for: {command}")
    
    def _execute_exe_command(self, command):
        """Для Windows exe файлов"""
        subprocess.Popen([command], shell=True)
        print(f"Successfully executed EXE: {command}")
    
    def _execute_sh_command(self, command):
        """Для Linux/Mac sh файлов"""
        subprocess.Popen(['sh', command])
        print(f"Successfully executed SH: {command}")
    
    def _execute_generic_command(self, command):
        """Другие команды"""
        subprocess.Popen(command.split())
        print(f"Successfully executed command: {command}")