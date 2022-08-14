from ipywidgets import widgets


class Widgets:
    output = None
    start_button = None
    progress_bar = None
    n_black_holes = None
    matrix_size = None
    restarted = None
    difficulty = None
    grid = None
    grid_buttons = None
    ui_main_menu = None
    ui_app = None
    n_of_cells_to_open = None

    def __init__(self, settings):
        self.settings = settings
        self.create_main_menu_widgets()
        self.link_widgets()
        self.calculate_n_of_cells_to_open()

    def create_grid(self, grid_buttons, matrix_size):
        """
            This function creates a grid layout of buttons
        :param grid_buttons: a list of buttons
        :param matrix_size: int, a size of a matrix
        :return:
        """
        self.grid = widgets.GridBox(children=grid_buttons,
                                    layout={"grid_template_columns": ("auto " * matrix_size)[:-1],
                                            "grid_template_rows": ("auto " * matrix_size)[:-1],
                                            "overflow": "scroll"})

    def create_main_menu_widgets(self):
        """
            This function creates widgets for the app
        :return:
        """
        # a dropdown widget
        self.difficulty = widgets.Dropdown(options=self.settings.dropdown_settings.get("OPTIONS"),
                                           index=self.settings.dropdown_settings.get("INDEX"),
                                           layout={"margin": self.settings.layout_margin},
                                           continuous_update=self.settings.continuous_update)

        # a matrix size widget
        self.matrix_size = widgets.IntSlider(value=self.settings.matrix_size.get("VALUE"),
                                             min=self.settings.matrix_size.get("MIN"),
                                             max=self.settings.matrix_size.get("MAX"),
                                             step=self.settings.matrix_size.get("STEP"),
                                             description=self.settings.matrix_size.get("DESCRIPTION"),
                                             style={"description_width": self.settings.description_width,
                                                    "handle_color": self.settings.handle_color.get("PRIMARY_COLOR")},
                                             layout={"margin": self.settings.layout_margin},
                                             continuous_update=self.settings.continuous_update)

        # a black holes widget
        self.n_black_holes = widgets.IntSlider(value=self.settings.black_holes.get("VALUE"),
                                               min=self.settings.black_holes.get("MIN"),
                                               max=self.settings.black_holes.get("MAX"),
                                               step=self.settings.black_holes.get("STEP"),
                                               description=self.settings.black_holes.get("DESCRIPTION"),
                                               style={"description_width": self.settings.description_width,
                                                      "handle_color": self.settings.handle_color.get("PRIMARY_COLOR")},
                                               layout={"margin": self.settings.layout_margin},
                                               continuous_update=self.settings.continuous_update)

        # a validation widget
        self.restarted = widgets.Valid(description=self.settings.validation.get("DESCRIPTION"),
                                       value=self.settings.validation.get("VALUE"),
                                       style={"description_width": self.settings.description_width})

        # a progress bar
        self.progress_bar = widgets.IntProgress(value=self.settings.progress_bar.get("VALUE"),
                                                min=self.settings.progress_bar.get("MIN"),
                                                max=self.settings.progress_bar.get("MAX"),
                                                step=self.settings.progress_bar.get("STEP"),
                                                description=self.settings.progress_bar.get("DESCRIPTION"),
                                                description_tooltip=self.settings.progress_bar.get(
                                                    "DESCRIPTION_TOOLTIP"),
                                                style={"description_width": self.settings.description_width})

        # a start button
        self.start_button = widgets.Button(description=self.settings.start_button.get("DESCRIPTION"),
                                           style={"button_color": self.settings.handle_color.get("START_BUTTON")},
                                           layout={"width": self.settings.width,
                                                   "height": self.settings.height,
                                                   "border": self.settings.borders.get("BUTTON")})

        self.output = widgets.Output()

    def link_widgets(self):
        """
            This function creates a layout of widgets
        :return:
        """
        ui_main_menu = widgets.HBox(children=[self.difficulty, self.matrix_size, self.n_black_holes],
                                    layout={"align_items": self.settings.alignment.get("STRETCH"),
                                            "width": self.settings.width,
                                            "justify_content": self.settings.alignment.get("CENTER")})

        ui_info = widgets.HBox(children=[self.restarted, self.progress_bar],
                               layout={"align_items": self.settings.alignment.get("STRETCH"),
                                       "width": self.settings.width,
                                       "justify_content": self.settings.alignment.get("CENTER")})

        self.ui_app = widgets.VBox(children=[ui_main_menu, ui_info, self.start_button, self.output],
                                   layout={
                                       "align_items": self.settings.alignment.get("STRETCH"),
                                       "width": self.settings.width,
                                       "padding": self.settings.layout_margin,
                                       "border": self.settings.borders.get("APP")})

    def calculate_n_of_cells_to_open(self):
        """
            This function calculates # of cells to open to win the game
        :return:
        """
        self.n_of_cells_to_open = self.matrix_size.value ** 2 - self.n_black_holes.value

    def update_widgets(self, button_color=None, description=None, validation_description=None,
                       progress_value=None, progress_tooltip=None):
        """
            This function updates the start button whether a player wins or loses the game
        :param button_color: key to button color from settings
        :param description: key to button description from settings
        :param validation_description: key to validation description from settings
        :param progress_value: key to progress value from settings
        :param progress_tooltip: key to progress tooltip from settings
        :return:
        """
        if button_color is not None:
            self.start_button.style.button_color = self.settings.handle_color.get(button_color)
        if description is not None:
            self.start_button.description = self.settings.start_button.get(description)
        if validation_description is not None:
            self.restarted.description = self.settings.validation.get(validation_description)
        if progress_value is not None:
            self.progress_bar.value = self.settings.progress_bar.get(progress_value)
        if progress_tooltip is not None:
            self.progress_bar.description_tooltip = self.settings.progress_bar.get(progress_tooltip)
