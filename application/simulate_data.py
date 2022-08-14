import ipywidgets as widgets
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from application.settings import Settings
from ui.widgets import Widgets


class Game:
    CELL_OPEN_FLAG = 0
    BUTTON_INIT = None
    grid_buttons = None
    base_mask = None
    n_open_cells = 0

    def __init__(self, app_widgets: Widgets, settings: Settings):
        # initializing the basic properties

        self.matrix_size = app_widgets.matrix_size.value
        self.n_black_holes = app_widgets.n_black_holes.value
        self.settings = settings
        self.height = self.matrix_size
        self.width = self.matrix_size

        # defining a table, black holes, adjacent black holes cells, and buttons
        self.rows = self.find_exact_adjacent()
        self.generate_black_holes()
        self.calculate_adjacent_black_holes()
        self.get_base_mask()
        self.rows["cell_open"] = self.CELL_OPEN_FLAG
        self.rows["button"] = self.BUTTON_INIT
        self.rows.loc[self.base_mask, "button"] = self.rows.loc[self.base_mask].apply(
            lambda row: self.create_expanded_button(row), axis=1)

        # defining a grid of buttons
        self.grid_buttons = self.get_buttons()

    def get_base_mask(self):
        self.base_mask = (self.rows.primary_key == self.rows.adjacent)

    @staticmethod
    def find_all_potential_adjacent(elements_list):
        """
            The function generates all potential adjacent cells
        :return:
            element - an array of all potential adjacent cells
        """

        # getting the current row and column index, and the matrix width
        row, col, width = elements_list

        # generating all potential adjacent cells
        element = np.array([
            (row * width + 1 + col) - width - 1,
            (row * width + 1 + col) - width,
            (row * width + 1 + col) - width + 1,
            (row * width + 1 + col) - 1,
            (row * width + 1 + col),
            (row * width + 1 + col) + 1,
            (row * width + 1 + col) + width - 1,
            (row * width + 1 + col) + width,
            (row * width + 1 + col) + width + 1,
        ])

        return element

    def find_exact_adjacent(self):
        """
            The function generates a table with cells information and theirs adjacent cells details
        :return:
            rows - pd.DataFrame, a table with columns:
                primary_key - an ordered id from 0 to self.matrix_size - 1
                adjacent - a vector of corresponding adjacent cells for the corresponding primary key
        """

        # generating a table with primary keys, potential adjacent cells, and the matrix size as a constant
        rows = pd.DataFrame({"primary_key": np.repeat(np.arange(self.matrix_size), self.matrix_size),
                             "secondary_key": np.tile(np.arange(self.matrix_size), self.matrix_size),
                             "size": np.repeat(self.matrix_size, self.matrix_size ** 2)
                             }, index=np.arange(self.matrix_size ** 2) + 1)

        # concatenating columns
        rows = pd.DataFrame(rows.apply(lambda x: (x[0], x[1], x[2]), axis=1).rename("adjacent"))

        # finding all potential adjacent cells
        rows = rows.applymap(lambda x: self.find_all_potential_adjacent(x))

        # keeping only right adjacent cells
        end_inds = np.linspace(self.height, self.width * self.height, self.height, dtype=int)
        start_inds = np.linspace(1, self.width * self.height - (self.height - 1), self.width, dtype=int)
        rows.adjacent.loc[end_inds] = rows.loc[end_inds].adjacent.apply(lambda x: np.delete(x, [2, 5, 8]))
        rows.adjacent.loc[start_inds] = rows.loc[start_inds].adjacent.apply(lambda x: np.delete(x, [0, 3, 6]))

        # converting the column of arrays to the column of lists
        rows.adjacent = rows.adjacent.apply(lambda x: list(x))

        # resetting the index and exploding the variable
        rows = rows.reset_index().rename(columns={"index": "primary_key"})
        rows = rows.explode('adjacent')

        # keeping only visible values
        rows = rows[(rows.adjacent >= 1) & (rows.adjacent <= self.width * self.height)].reset_index(drop=True)

        return rows

    def generate_black_holes(self):
        """
            The function generates black holes with the uniform distribution
        """
        # generating random indexes of potential black holes
        black_holes_index = np.random.choice(self.rows[self.rows.primary_key == self.rows.adjacent].index.tolist(),
                                             size=self.n_black_holes,
                                             replace=False)

        # initializing a column and filling with black holes flag
        self.rows["black_holes"] = 0
        self.rows.loc[black_holes_index, "black_holes"] = 1

        # sharing the information about black holes flags among their adjacent cells
        black_keys = self.rows.groupby(["primary_key"]).apply(
            lambda x: x.black_holes.sum()).rename("black_key").reset_index()
        self.rows = pd.merge(self.rows, black_keys, on=["primary_key"], how="inner")

    def calculate_adjacent_black_holes(self):
        """
            The function calculates a number of adjacent cells
        """

        # calculating the sum of adjacent black holes
        adjacent_black_hole = self.rows.groupby(["adjacent"]).apply(lambda x: x.black_key.sum()).rename(
            "adjacent_black_hole").reset_index()
        self.rows = pd.merge(self.rows, adjacent_black_hole, on=["adjacent"], how="inner")
        self.rows = self.rows.sort_values(by=["primary_key", "adjacent"]).reset_index(drop=True)

    def create_expanded_button(self, row):
        """
            The function create a button for a cell
        :param row:
        :return:
            button - widgets.Button with special properties
        """

        # extracting a number of a cell, a black hole flag, and a number of adjacent black holes
        number = row.primary_key
        black_hole = row.black_holes
        adjacent_bh = row.adjacent_black_hole

        # creating a button with its properties
        button = widgets.Button(
            tooltip=f"{number}",
            style={"button_color": self.settings.handle_color.get("WON")},
            layout={"height": self.settings.cell.get("HEIGHT_CELL"),
                    "width": self.settings.cell.get("WIDTH_CELL"),
                    "border": self.settings.borders.get("CELL"),
                    })
        button.black_hole = bool(black_hole)
        button.adjacent_bh = adjacent_bh

        return button

    def plot_heatmap(self):
        """
            This function plots a figure with # of adjacent black hole cells and black holes itself
        """
        # defining # of adjacent black hole cells and black holes itself
        adjacent_black_holes_matrix = self.get_adjacent_holes_matrix()

        # plotting a figure
        plt.figure(figsize=(15, 8))
        sns.heatmap(adjacent_black_holes_matrix)
        plt.title("# of adjacent black hole cells and black holes")
        plt.show()

    def get_adjacent_holes_matrix(self):
        """
            This function convert the table to a matrix of # of adjacent black hole cells, and marks the black hole
            cell as -1
        :return:
        """
        # defining a matrix whether a cell is black hole or not, and inverting 1 -> 0, and 0 -> 1
        black_holes_matrix = self.rows[self.rows.primary_key == self.rows.adjacent
                                       ].black_holes.values.reshape(self.height, self.width)
        black_holes_matrix_invert = np.logical_xor(black_holes_matrix, 1).astype(int)

        # defining a matrix of # adjacent black holes cells
        adjacent_black_holes_matrix = self.rows[self.rows.primary_key == self.rows.adjacent
                                                ].adjacent_black_hole.values.reshape(self.height, self.width)
        adjacent_black_holes_matrix = adjacent_black_holes_matrix * black_holes_matrix_invert + (
                -1 * black_holes_matrix)

        return adjacent_black_holes_matrix

    def get_buttons(self):
        """
            This function extracts all buttons to a list
        :return:
           grid_buttons: a list of buttons
        """
        grid_buttons = self.rows[self.rows.primary_key == self.rows.adjacent].button.values.reshape(-1).tolist()

        return grid_buttons

    def get_all_cells_to_open(self, number):
        """
            This function finds all adjacent cells to open while clicking a specific cell
        :param number: a cell clicked
        :return:
        """
        # defining a set of all buttons to be open and buttons with zero adjacent black hole cells
        all_cells_to_open = set()
        adjacent_open_cells = {number}

        # while there is any cells with zero adjacent black hole -> find adjacent cells
        while len(adjacent_open_cells) != 0:
            # only cells with zero adjacent black hole cells
            open_adj_cells_mask = (self.rows.primary_key.isin(adjacent_open_cells)) & (
                ~self.rows.adjacent.isin(adjacent_open_cells)) & (self.rows.adjacent_black_hole == 0)
            open_tmp_all_adj_cells_mask = (self.rows.primary_key.isin(adjacent_open_cells))

            # extracting new cells with zero adjacent black hole cells
            adjacent_open_cells = set(self.rows.loc[open_adj_cells_mask].adjacent.values.tolist())
            adjacent_open_cells = adjacent_open_cells.difference(all_cells_to_open)

            # all adjacent cells to cells with zero adjacent black hole cells
            all_adjacent_open_cells = self.rows.loc[open_tmp_all_adj_cells_mask].adjacent.values.tolist()
            all_cells_to_open.update(all_adjacent_open_cells)

        return all_cells_to_open

    def calculate_open_cells(self):
        """
            This function calculates # of open cells
        :return:
        """
        self.n_open_cells = self.rows.loc[self.base_mask, "cell_open"].sum()
