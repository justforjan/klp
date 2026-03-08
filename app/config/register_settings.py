
_SETTINGS_CLASS_MAP = {}

def register_setting(name: str):

    def wrapper(setting_class):
        if name in _SETTINGS_CLASS_MAP:
            raise ValueError(f"Setting with name '{name}' is already registered.")
        _SETTINGS_CLASS_MAP[name] = setting_class
        return setting_class

    return wrapper

def _get_settings(env: str):
    setting = _SETTINGS_CLASS_MAP.get(env)
    if setting is None:
        raise ValueError(f"Setting with name '{env}' is not registered.")
    return setting()