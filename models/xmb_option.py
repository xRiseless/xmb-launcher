# models/xmb_option.py

class XMBOption:
    def __init__(self, name, icon=None, command=None):
        self.name = name
        self.icon_name = icon  # имя файла иконки
        self.command = command  # команда для выполнения
        self.target_y = 0
        self.current_y = 0
        self.initialized = False
        self.alpha = 255