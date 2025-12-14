# models/xmb_subcategory.py

class XMBSubcategory:
    def __init__(self, name, icon=None, subcategory_type=1, command=None):
        self.name = name
        self.icon_name = icon  # имя файла иконки
        self.type = subcategory_type  # 0 - выполнить команду, 1 - открыть опции
        self.command = command  # команда для выполнения (если type=0)
        self.target_y = 0
        self.current_y = 0
        self.initialized = False
        self.alpha = 0