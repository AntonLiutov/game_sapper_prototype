import json
from IPython.display import display
from application.settings import Settings
from ui.widgets import Widgets
from ui.widget_utils import Utils

if __name__ == '__main__':
    with open('config.json', 'r+') as f:
        configs = json.load(f)

    settings = Settings(configs=configs)
    app_widgets = Widgets(settings=settings)
    utils = Utils(app_widgets=app_widgets, settings=settings)
    display(utils.app_widgets.ui_app)
