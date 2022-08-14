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
        ui_main_menu = widgets.HBox(children=[self.difficulty, self.matrix_size, self.n_black_holes,
                                              self.restarted, self.progress_bar],
                                    layout={"align_items": self.settings.alignment,
                                            "width": self.settings.width,
                                            "justify_content": self.settings.alignment})

        self.ui_app = widgets.VBox(children=[ui_main_menu, self.start_button, self.output],
                                   layout={
                                       "align_items": self.settings.alignment,
                                       "width": self.settings.width,
                                       "padding": self.settings.layout_margin,
                                       "border": self.settings.borders.get("APP")})

    def calculate_n_of_cells_to_open(self):
        self.n_of_cells_to_open = self.matrix_size.value ** 2 - self.n_black_holes.value
