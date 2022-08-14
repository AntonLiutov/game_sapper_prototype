from IPython.display import display
import numpy as np
from application.simulate_data import Game
from application.settings import Settings
from ui.widgets import Widgets


class Utils:
    game = None
    grid = None

    def __init__(self, app_widgets: Widgets, settings: Settings):
        self.app_widgets = app_widgets
        self.settings = settings
        self.observe_widgets()
        self.observe_clicks()

    def observe_clicks(self):
        """
            This function observes clicks on the start button
        :return:
        """
        self.app_widgets.start_button.on_click(self.on_button_clicked)

    def on_button_clicked(self, button):
        """
            This function updates the widgets of the main menu, outputs the grid layout with buttons for the game
            and listens to clicks to the cell buttons
        :param button: the start button
        :return:
        """
        # updating the widgets
        self.app_widgets.update_widgets(button_color="START_BUTTON", description="DESCRIPTION_STARTING",
                                        validation_description="DESCRIPTION_LOAD")
        self.app_widgets.output.clear_output(wait=True)

        # creating the game, and the layout of buttons
        self.game = Game(app_widgets=self.app_widgets, settings=self.settings)
        self.app_widgets.create_grid(self.game.grid_buttons, self.game.matrix_size)
        with self.app_widgets.output:
            display(self.app_widgets.grid)
        self.app_widgets.calculate_n_of_cells_to_open()
        self.app_widgets.progress_bar.max = self.app_widgets.n_of_cells_to_open

        # observing to clicks to cell buttons
        self.game.rows.loc[self.game.base_mask].button.apply(lambda x: x.on_click(self.on_click_cell))

        # updating the widgets
        self.app_widgets.update_widgets(description="DESCRIPTION_RESTART", validation_description="DESCRIPTION_START",
                                        progress_value="VALUE", progress_tooltip="DESCRIPTION_TOOLTIP")

    def on_click_cell(self, button):
        """
            This function reacts on the cell button click:
        :param button: cell button
        :return:
        """
        # extracting a cell button info
        black_hole = button.black_hole
        adjacent_bh = button.adjacent_bh
        number = int(button.tooltip)

        if black_hole:
            # updating buttons and the widgets
            self.app_widgets.update_widgets(button_color="LOST", description="DESCRIPTION_LOST")
            self.update_buttons(mask=self.game.base_mask, func_update=self.open_black_holes)
        else:
            # if there are non-zero adjacent black hole cells
            if adjacent_bh != 0:
                # updating progress and buttons
                self.update_progress(mask=self.game.base_mask & (self.game.rows.primary_key == number))
                self.update_buttons(mask=self.game.base_mask & (self.game.rows.primary_key == number),
                                    func_update=self.open_cells)
            else:
                # otherwise, finding all adjacent not black hole cells near to zero adjacent black hole cells
                all_cells_to_open = self.game.get_all_cells_to_open(number=number)

                # updating progress and buttons
                self.update_progress(mask=self.game.base_mask & (self.game.rows.primary_key.isin(all_cells_to_open)))
                self.update_buttons(mask=self.game.base_mask & (self.game.rows.primary_key.isin(all_cells_to_open)),
                                    func_update=self.open_cells)

            if self.game.n_open_cells == self.app_widgets.n_of_cells_to_open:
                # if all not black hole cells are open, then updating buttons and the widgets
                self.app_widgets.update_widgets(button_color="WON", description="DESCRIPTION_WON")
                self.update_buttons(mask=self.game.base_mask & (self.game.rows.cell_open == 0),
                                    func_update=self.disable)

    def update_progress(self, mask):
        """
            This function updates the progress bar
        :param mask: pd.Series of boolean values
        :return:
        """
        # setting 1 to open cells and recalculating # of open cells
        self.game.rows.loc[mask, "cell_open"] = 1
        self.game.calculate_open_cells()

        # updating the widgets
        self.app_widgets.progress_bar.value = self.game.n_open_cells
        progress = int(self.game.n_open_cells / self.app_widgets.progress_bar.max * 100)
        self.app_widgets.progress_bar.description_tooltip = f"{progress}% done "

    def update_buttons(self, mask, func_update):
        """
            This function updates cell buttons
        :param mask: pd.Series of boolean mask
        :param func_update: a function to apply to buttons
        :return:
        """
        # updating buttons
        self.game.rows.loc[mask, "button"] = self.game.rows.loc[mask, "button"].apply(
            lambda cell_button: func_update(cell_button))
        # updating the grid layout
        self.app_widgets.grid.children = self.game.get_buttons()

    def observe_widgets(self):
        """
            This function observes changes to the widgets
        :return:
        """
        self.app_widgets.difficulty.observe(self.handle_change_difficulty, 'value')
        self.app_widgets.matrix_size.observe(self.handle_change_matrix, 'value')
        self.app_widgets.n_black_holes.observe(self.handle_change_n_holes, 'value')

    def handle_change_difficulty(self, change):
        """
            This function observes changes to the dropdown widget
        :param change: an object with attributes of the widget
        :return:
        """
        if change.new != "Custom":
            self.app_widgets.matrix_size.value = self.settings.difficulty_dict[change.new][0]
            self.app_widgets.n_black_holes.max = self.settings.difficulty_dict[change.new][2]
            self.app_widgets.n_black_holes.value = self.settings.difficulty_dict[change.new][1]

    def handle_change_matrix(self, change):
        """
            This function observes changes to the matrix size widget
        :param change: an object with attributes of the widget
        :return:
        """
        self.app_widgets.n_black_holes.max = np.max([change.owner.value * change.owner.value - 9, 1])
        if change.new != self.settings.difficulty_dict[self.app_widgets.difficulty.value][0]:
            self.app_widgets.difficulty.value = "Custom"

    def handle_change_n_holes(self, change):
        """
            This function observes changes to the # of black holes' widget
        :param change: an object with attributes of the widget
        :return:
        """
        if change.new != self.settings.difficulty_dict[self.app_widgets.difficulty.value][1]:
            self.app_widgets.difficulty.value = "Custom"

    def open_black_holes(self, button):
        """
            This function updates cells with black holes and disables the rest of the cell buttons
        :param button: the cell button object
        :return:
        """
        black_hole = button.black_hole
        if black_hole:
            button.style.button_color = self.settings.handle_color.get("LOST")
        else:
            button.disabled = True

        return button

    @staticmethod
    def disable(button):
        """
            This function disables all the cell buttons
        :param button: the cell button object
        :return:
        """
        button.disabled = True
        return button

    def open_cells(self, button):
        """
            This function updates cells without black holes and updates the validation widget
        :param button: the cell button object
        :return:
        """
        adjacent_bh = button.adjacent_bh
        if adjacent_bh != 0:
            button.description = str(adjacent_bh)
            button.style.button_color = self.settings.handle_color.get("WARNING")
        else:
            button.style.button_color = self.settings.handle_color.get("START_BUTTON")
        self.app_widgets.restarted.description = f"Open cells: {self.game.n_open_cells}"

        return button
