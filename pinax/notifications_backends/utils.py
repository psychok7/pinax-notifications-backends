
try:
    # Django versions >= 1.9
    from django.utils.module_loading import import_module
except ImportError:
    # Django versions < 1.9
    from django.utils.importlib import import_module


def get_class_from_path(path):
    # This function is helpful to avoid circular imports.
    module_name, class_name = path.rsplit(".", 1)
    class_ = getattr(import_module(module_name), class_name)
    return class_
