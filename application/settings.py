class Settings:

    def __init__(self, configs):
        # general settings
        self.alignment = configs.get("ALIGNMENT", None)
        self.layout_margin = configs.get("LAYOUT_MARGIN", None)
        self.continuous_update = configs.get("CONTINUOUS_UPDATE", None)
        self.description_width = configs.get("DESCRIPTION_WIDTH", None)
        self.width = configs.get("WIDTH", None)
        self.height = configs.get("HEIGHT", None)
        self.borders = configs.get("BORDER", None)
        self.handle_color = configs.get("HANDLE_COLOR", None)

        # cells
        self.cell = configs.get("CELL", None)

        # difficulty levels
        self.difficulty_dict = configs.get("DIFFICULTY_DICT", None)

        # widget settings
        self.dropdown_settings = configs.get("DROPDOWN_SETTINGS", None)
        self.matrix_size = configs.get("MATRIX_SIZE", None)
        self.black_holes = configs.get("BLACK_HOLES", None)
        self.validation = configs.get("VALIDATION", None)
        self.progress_bar = configs.get("PROGRESS_BAR", None)
        self.start_button = configs.get("START_BUTTON", None)
