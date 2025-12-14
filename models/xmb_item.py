# models/xmb_item.py

class XMBItem:
    def __init__(self, name, icon=None, subcategories=None):
        self.name = name
        self.icon_name = icon  # имя файла иконки
        self.subcategories = subcategories or []
        self.selected = False
        self.target_x = 0
        self.current_x = 0
        self.last_subcategory_index = 0
        self.first_visit = True
        self.alpha = 255