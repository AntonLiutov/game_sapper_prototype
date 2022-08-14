#!/usr/bin/env python
# coding: utf-8

# # Libraries

# In[16]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from ipywidgets import interact, interactive, fixed, interact_manual, Layout, ButtonStyle, Button
from ipywidgets import GridspecLayout, VBox, HBox, GridBox
from IPython.display import display
import ipywidgets as widgets


# # Functions

# In[2]:


def find_all_potential_adjacents(elements_list):
    row, col, width = elements_list
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


# In[3]:


def find_exact_adjacents(height, width):
    rows = pd.DataFrame({"primary_key": np.repeat(np.arange(height), height),
                         "secondary_key": np.tile(np.arange(height), height),
                         "size": np.repeat(height, height ** 2)
                         }, index=np.arange(height ** 2) + 1)
    rows = pd.DataFrame(rows.apply(lambda x: (x[0], x[1], x[2]), axis=1).rename("adjacents"))
    rows = rows.applymap(lambda x: find_all_potential_adjacents(x))

    end_inds = np.linspace(height, width * height, height, dtype=int)
    start_inds = np.linspace(1, width * height - (height - 1), width, dtype=int)
    rows.adjacents.loc[end_inds] = rows.loc[end_inds].adjacents.apply(lambda x: np.delete(x, [2, 5, 8]))
    rows.adjacents.loc[start_inds] = rows.loc[start_inds].adjacents.apply(lambda x: np.delete(x, [0, 3, 6]))

    rows.adjacents = rows.adjacents.apply(lambda x: list(x))
    rows = rows.reset_index().rename(columns={"index": "primary_key"})
    rows = rows.explode('adjacents')

    rows = rows[(rows.adjacents >= 1) & (rows.adjacents <= width * height)].reset_index(drop=True)

    return rows


# In[4]:


def generate_black_holes(rows, n_black_holes):
    black_holes_index = np.random.choice(rows[rows.primary_key == rows.adjacents].index.tolist(),
                                         size=n_black_holes, replace=False)

    rows["black_holes"] = 0
    rows.loc[black_holes_index, "black_holes"] = 1

    black_keys = rows.groupby(["primary_key"]).apply(lambda x: x.black_holes.sum()).rename("black_key").reset_index()
    rows = pd.merge(rows, black_keys, on=["primary_key"], how="inner")

    return rows


# In[5]:


def calculate_adjacent_black_holes(rows):
    adjacent_black_hole = rows.groupby(["adjacents"]).apply(lambda x: x.black_key.sum()).rename(
        "adjacent_black_hole").reset_index()

    rows = pd.merge(rows, adjacent_black_hole, on=["adjacents"], how="inner")

    rows = rows.sort_values(by=["primary_key", "adjacents"]).reset_index(drop=True)

    return rows


# In[6]:


def get_adjacent_holes_matrix(rows, height, width):
    black_holes_matrix = rows[rows.primary_key == rows.adjacents].black_holes.values.reshape(height, width)
    black_holes_matrix_invert = np.logical_xor(black_holes_matrix, 1).astype(int)

    adjacent_black_holes_matrix = rows[rows.primary_key == rows.adjacents].adjacent_black_hole.values.reshape(height,
                                                                                                              width)
    adjacent_black_holes_matrix = adjacent_black_holes_matrix * black_holes_matrix_invert + (-1 * black_holes_matrix)

    return adjacent_black_holes_matrix


# In[7]:


def create_expanded_button(x):
    number = x.primary_key
    black_hole = x.black_holes
    adjacent_bh = x.adjacent_black_hole
    button = Button(
        tooltip=f"{number}",
        style={"button_color": "dodgerblue"},
        layout=Layout(height='auto',
                      width='auto',
                      border="1px solid grey",
                      ))
    button.black_hole = bool(black_hole)
    button.adjacent_bh = adjacent_bh
    return button


# In[8]:


def plot_heatmap():
    fig = plt.figure(figsize=(15, 8))
    sns.heatmap(adjacent_black_holes_matrix)
    plt.title("New game")
    plt.show()


# In[9]:


def game(matrix_size, n_black_holes):
    height = matrix_size
    width = matrix_size

    rows = find_exact_adjacents(height, width)
    rows = generate_black_holes(rows, n_black_holes)
    rows = calculate_adjacent_black_holes(rows)

    rows["cell_open"] = 0
    rows["button"] = None
    rows.loc[rows.primary_key == rows.adjacents, "button"] = rows.loc[rows.primary_key == rows.adjacents].apply(
        lambda x: create_expanded_button(x), axis=1)

    adjacent_black_holes_matrix = get_adjacent_holes_matrix(rows, height, width)

    # plot_heatmap()

    grid_buttons = rows[rows.primary_key == rows.adjacents].button.values.reshape(-1).tolist()
    grid = GridBox(children=grid_buttons,
                   layout=Layout(
                       grid_template_columns=("auto " * matrix_size)[:-1],
                       grid_template_rows=("auto " * matrix_size)[:-1],
                       overflow="scroll",
                   ),
                   )
    # grid = None

    return adjacent_black_holes_matrix, rows, grid


# In[10]:


def open_black_holes(button):
    black_hole = button.black_hole
    if black_hole:
        button.description = "B"
        button.style.button_color = "red"
    button.disabled = True
    start_button.style.button_color = "red"
    start_button.description = "You Lost. Try Again"

    return button


def disable(button):
    button.disabled = True

    return button


def open_cells(button):
    global n_open_cells
    adjacent_bh = button.adjacent_bh
    if adjacent_bh != 0:
        button.description = str(adjacent_bh)
        button.style.button_color = "orange"
    else:
        button.style.button_color = "lightskyblue"
    restarted.description = f"Open cells: {n_open_cells}"

    return button


# # Constants

# In[11]:


Difficulty_dict = {"Easy": [8, 10, 55], "Medium": [16, 40, 247], "Hard": [24, 99, 567], "Custom": [-1, -1, -1]}

# # Defining UI elements

# In[12]:


Difficulty = widgets.Dropdown(options=["Easy", "Medium", "Hard", "Custom"],
                              index=0,
                              layout={
                                  "margin": "10px",
                              },
                              continuous_update=False
                              )

matrix_size = widgets.IntSlider(value=8, min=3, max=40, step=1,
                                description='Matrix Size:',
                                style={"description_width": "initial",
                                       "handle_color": "royalblue",
                                       },
                                layout={
                                    "margin": "10px",
                                },
                                continuous_update=False
                                )

n_black_holes = widgets.IntSlider(value=10, min=1, max=55, step=1,
                                  description='# of black holes:',
                                  style={"description_width": "initial",
                                         "handle_color": "royalblue",
                                         },
                                  layout={
                                      "margin": "10px",
                                  },
                                  continuous_update=False
                                  )

restarted = widgets.Valid(description="Main Menu", value=True,
                          style={"description_width": "initial"},
                          )

progressBar = widgets.IntProgress(value=0,
                                  min=0,
                                  max=8 * 8 - 10,
                                  step=1,
                                  description="Progress",
                                  description_tooltip='0% done',
                                  style={"description_width": "initial"},
                                  )

start_button = widgets.Button(description="Start Game",
                              style={"button_color": "lightskyblue",
                                     },
                              layout=Layout(
                                  width="99%",
                                  height="50px",
                                  border="2px solid black"
                              )
                              )
output = widgets.Output()


# # UI Functions

# In[13]:


def handle_change_difficulty(change):
    if change.new != "Custom":
        matrix_size.value = Difficulty_dict[change.new][0]
        n_black_holes.max = Difficulty_dict[change.new][2]
        n_black_holes.value = Difficulty_dict[change.new][1]


Difficulty.observe(handle_change_difficulty, 'value')


def handle_change_matrix(change):
    n_black_holes.max = np.max([change.owner.value * change.owner.value - 9, 1])
    progressBar.max = matrix_size.value ** 2 - n_black_holes.value
    if change.new != Difficulty_dict[Difficulty.value][0]:
        Difficulty.value = "Custom"


matrix_size.observe(handle_change_matrix, 'value')


def handle_change_n_holes(change):
    progressBar.max = matrix_size.value ** 2 - n_black_holes.value
    if change.new != Difficulty_dict[Difficulty.value][1]:
        Difficulty.value = "Custom"


n_black_holes.observe(handle_change_n_holes, 'value')


@output.capture()
def on_button_clicked(button):
    global grid, rows, n_black_holes_value, matrix_size_value
    start_button.style.button_color = "lightskyblue"
    start_button.description = "Restart Game"
    restarted.description = "Loading"
    restarted.value = True
    output.clear_output(wait=True)
    matrix_size_value = ui_h.children[1].value
    n_black_holes_value = ui_h.children[2].value
    adjacent_black_holes_matrix, rows, grid = game(matrix_size=matrix_size_value, n_black_holes=n_black_holes_value)
    display(grid)
    rows.loc[rows.primary_key == rows.adjacents].button.apply(lambda x: x.on_click(on_click_cell))
    restarted.description = "Started"
    progressBar.value = 0
    progressBar.description_tooltip = "0% done"


start_button.on_click(on_button_clicked)


def on_cell_clicked(button):
    display(button)


# In[14]:


def on_click_cell(button):
    global rows, n_open_cells, n_black_holes_value, matrix_size_value

    black_hole = button.black_hole
    adjacent_bh = button.adjacent_bh
    number = int(button.tooltip)
    if black_hole:
        all_butons_mask = (rows.primary_key == rows.adjacents)
        rows.loc[all_butons_mask, "button"] = rows.loc[all_butons_mask, "button"].apply(
            lambda button: open_black_holes(button))
        grid_buttons = rows[rows.primary_key == rows.adjacents].button.values.reshape(-1).tolist()
        grid.children = grid_buttons
    else:
        if adjacent_bh != 0:
            open_unique_cell_mask = (rows.primary_key == rows.adjacents) & (rows.primary_key == number)
            rows.loc[open_unique_cell_mask, "cell_open"] = 1
            n_open_cells = rows.loc[(rows.primary_key == rows.adjacents), "cell_open"].sum()
            progressBar.value = n_open_cells
            progressBar.description_tooltip = f"{int(n_open_cells / progressBar.max * 100)}% done"
            rows.loc[open_unique_cell_mask, "button"] = rows.loc[open_unique_cell_mask, "button"].apply(
                lambda button: open_cells(button))
            grid_buttons = rows[rows.primary_key == rows.adjacents].button.values.reshape(-1).tolist()
            grid.children = grid_buttons
        else:
            all_cells_to_open = set()
            adjacent_open_cells = set([number])

            while len(adjacent_open_cells) != 0:
                # only zero
                open_adj_cells_mask = (rows.primary_key.isin(adjacent_open_cells)) & (
                    ~rows.adjacents.isin(adjacent_open_cells)) & (rows.adjacent_black_hole == 0)
                open_tmp_all_adj_cells_mask = (rows.primary_key.isin(adjacent_open_cells))

                adjacent_open_cells = set(rows.loc[open_adj_cells_mask].adjacents.values.tolist())
                adjacent_open_cells = adjacent_open_cells.difference(all_cells_to_open)

                # all adjacents to zero
                all_adjacent_open_cells = rows.loc[open_tmp_all_adj_cells_mask].adjacents.values.tolist()
                all_cells_to_open.update(all_adjacent_open_cells)

            open_all_adj_cells_mask = (rows.primary_key == rows.adjacents) & (rows.primary_key.isin(all_cells_to_open))
            rows.loc[open_all_adj_cells_mask, "cell_open"] = 1
            n_open_cells = rows.loc[(rows.primary_key == rows.adjacents), "cell_open"].sum()
            progressBar.value = n_open_cells
            progressBar.description_tooltip = f"{int(n_open_cells / progressBar.max * 100)}% done"
            rows.loc[open_all_adj_cells_mask, "button"] = rows.loc[open_all_adj_cells_mask, "button"].apply(
                lambda button: open_cells(button))
            grid_buttons = rows[rows.primary_key == rows.adjacents].button.values.reshape(-1).tolist()
            grid.children = grid_buttons
        if n_open_cells == (matrix_size_value ** 2 - n_black_holes_value):
            start_button.style.button_color = "dodgerblue"
            start_button.description = "You Won. Play Again"
            rows.loc[(rows.primary_key == rows.adjacents), "button"] = rows.loc[
                (rows.primary_key == rows.adjacents), "button"].apply(lambda button: disable(button))
            grid_buttons = rows[rows.primary_key == rows.adjacents].button.values.reshape(-1).tolist()
            grid.children = grid_buttons


# In[ ]:


def combine_widgets():
    hbox_layout = Layout(
        align_items="center",
        width="100%",
        # padding="10px",
        justify_content='center',
    )
    ui_h = widgets.HBox(children=[Difficulty, matrix_size, n_black_holes, restarted, progressBar],
                        layout=hbox_layout
                        )

    vbox_layout = Layout(align_items="stretch",
                         width="100%",
                         padding="10px",
                         border="10px double black"
                         )

    ui_grid = widgets.VBox(children=[ui_h, start_button, output],
                           layout=vbox_layout
                           )

    return ui_grid


# # Play Game

# In[18]:


if __name__ == '__main__':
    ui_grid = combine_widgets()
    display(ui_grid)

