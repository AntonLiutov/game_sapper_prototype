import numpy as np
import time
from IPython.display import display
from application.simulate_data import Game
from application.settings import Settings
from ui.widgets import Widgets


class Utils:
    n_open_cells = 0
    game = None
    grid = None

    def __init__(self, app_widgets: Widgets, settings: Settings):
        self.app_widgets = app_widgets
        self.settings = settings
        self.observe_widgets()
        self.observe_clicks()

    def observe_clicks(self):
        self.app_widgets.start_button.on_click(self.on_button_clicked)

    def on_button_clicked(self, button):
        self.app_widgets.start_button.style.button_color = self.settings.handle_color.get("START_BUTTON")
        self.app_widgets.start_button.description = self.settings.start_button.get("DESCRIPTION_STARTING")
        self.app_widgets.restarted.description = self.settings.validation.get("DESCRIPTION_LOAD")
        self.app_widgets.output.clear_output(wait=True)

        self.game = Game(app_widgets=self.app_widgets, settings=self.settings)
        self.app_widgets.create_grid(self.game.grid_buttons, self.game.matrix_size)
        with self.app_widgets.output:
            display(self.app_widgets.grid)
        self.app_widgets.calculate_n_of_cells_to_open()
        self.app_widgets.progress_bar.max = self.app_widgets.n_of_cells_to_open
        self.game.rows.loc[self.game.base_mask].button.apply(lambda x: x.on_click(self.on_click_cell))

        self.app_widgets.start_button.description = self.settings.start_button.get("DESCRIPTION_RESTART")
        self.app_widgets.restarted.description = self.settings.validation.get("DESCRIPTION_START")
        self.app_widgets.progress_bar.value = self.settings.progress_bar.get("VALUE")
        self.app_widgets.progress_bar.description_tooltip = self.settings.progress_bar.get("DESCRIPTION_TOOLTIP")

    def on_click_cell(self, button):
        self.game.calculate_open_cells()

        black_hole = button.black_hole
        adjacent_bh = button.adjacent_bh
        number = int(button.tooltip)

        if black_hole:
            self.update_buttons(mask=self.game.base_mask, func_update=self.open_black_holes)
            self.app_widgets.update_start_button(button_color="LOST", description="DESCRIPTION_LOST")
        else:
            if adjacent_bh != 0:
                self.update_progress(mask=self.game.base_mask & (self.game.rows.primary_key == number))
                self.update_buttons(mask=self.game.base_mask & (self.game.rows.primary_key == number),
                                    func_update=self.open_cells)
            else:
                all_cells_to_open = self.game.get_all_cells_to_open(number=number)
                self.update_progress(mask=self.game.base_mask & (self.game.rows.primary_key.isin(all_cells_to_open)))
                self.update_buttons(mask=self.game.base_mask & (self.game.rows.primary_key.isin(all_cells_to_open)),
                                    func_update=self.open_cells)

            if self.game.n_open_cells == self.app_widgets.n_of_cells_to_open:
                self.app_widgets.update_start_button(button_color="WON", description="DESCRIPTION_WON")
                self.update_buttons(mask=self.game.base_mask & (self.game.rows.cell_open == 0),
                                    func_update=self.disable)

    def update_progress(self, mask):
        self.game.rows.loc[mask, "cell_open"] = 1
        self.game.calculate_open_cells()

        self.app_widgets.progress_bar.value = self.game.n_open_cells
        progress = int(self.game.n_open_cells / self.app_widgets.progress_bar.max * 100)
        self.app_widgets.progress_bar.description_tooltip = f"{progress}% done "

    def update_buttons(self, mask, func_update):
        self.game.rows.loc[mask, "button"] = self.game.rows.loc[mask, "button"].apply(
            lambda cell_button: func_update(cell_button))
        self.app_widgets.grid.children = self.game.get_buttons()

    def observe_widgets(self):
        self.app_widgets.difficulty.observe(self.handle_change_difficulty, 'value')
        self.app_widgets.matrix_size.observe(self.handle_change_matrix, 'value')
        self.app_widgets.n_black_holes.observe(self.handle_change_n_holes, 'value')

    def handle_change_difficulty(self, change):
        if change.new != "Custom":
            self.app_widgets.matrix_size.value = self.settings.difficulty_dict[change.new][0]
            self.app_widgets.n_black_holes.max = self.settings.difficulty_dict[change.new][2]
            self.app_widgets.n_black_holes.value = self.settings.difficulty_dict[change.new][1]

    def handle_change_matrix(self, change):
        self.app_widgets.n_black_holes.max = np.max([change.owner.value * change.owner.value - 9, 1])
        if change.new != self.settings.difficulty_dict[self.app_widgets.difficulty.value][0]:
            self.app_widgets.difficulty.value = "Custom"

    def handle_change_n_holes(self, change):
        if change.new != self.settings.difficulty_dict[self.app_widgets.difficulty.value][1]:
            self.app_widgets.difficulty.value = "Custom"

    def open_black_holes(self, button):
        black_hole = button.black_hole
        if black_hole:
            button.style.button_color = self.settings.handle_color.get("LOST")
        else:
            button.disabled = True

        return button

    @staticmethod
    def disable(button):
        button.disabled = True
        return button

    def open_cells(self, button):
        adjacent_bh = button.adjacent_bh
        if adjacent_bh != 0:
            button.description = str(adjacent_bh)
            button.style.button_color = self.settings.handle_color.get("WARNING")
        else:
            button.style.button_color = self.settings.handle_color.get("START_BUTTON")
        self.app_widgets.restarted.description = f"Open cells: {self.game.n_open_cells}"

        return button
