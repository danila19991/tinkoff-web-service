import importlib
import json


class ConfigParser:

    def __init__(self, config_filename="ml_config.json"):
        """
        Constructor which opens config file and parses it.

        :param config_filename: str, optional(default="ml_config.json")
            Name of the json file with configuration.
        """
        with open(config_filename, "r") as f:
            self._parsed_json = json.loads(f.read())

    def __getitem__(self, item):
        """
        Add dict-like interface: config[item]

        :param item: str
            Parameter name in config file.

        :return: int, str, dict, list, bool, None
            Value of parameter in config file.
        """
        return self._parsed_json[item]

    @staticmethod
    def get_class(class_name, module_name):
        """
        Get class with class_name from module_name.

        :param class_name: str
            Name of the class to be created.

        :param module_name: str
            Name of the module which stores class with class_name.

        :return: type of class_name from module_name
        """
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def get_instance(self, class_name, module_name, **kwargs):
        """
        Get instance of class with class_name from module_name.

        :param class_name: str
            Name of the class to be created.

        :param module_name: str
            Name of the module which stores class with class_name.

        :return: instance of class_name from module_name
        """
        return self.get_class(class_name, module_name)(**kwargs)
