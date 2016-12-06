
from django.utils import importlib


def get_class_from_path(path):
    # This function is helpful to avoid circular imports.
    module_name, class_name = path.rsplit(".", 1)
    class_ = getattr(importlib.import_module(module_name), class_name)
    return class_
