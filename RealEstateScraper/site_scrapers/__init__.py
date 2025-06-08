from pathlib import Path
import importlib

PLUGIN_PATH = Path(__file__).parent / 'plugins'


def load_plugin(name):
    module_name = f'RealEstateScraper.site_scrapers.plugins.{name}'
    return importlib.import_module(module_name)
