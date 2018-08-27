import copy
import importlib
import json


class ConfigParser:

    def __init__(self, existing_parsed_json_dict=None,
                 config_filename="ml_config.json"):
        """
        Constructor which opens config file and parses it.

        :param existing_parsed_json_dict: dict, optional (default=None)
            If config file was parsed, you can pass it to this class.

        :param config_filename: str, optional(default="ml_config.json")
            Name of the json file with configuration.
        """
        if existing_parsed_json_dict is None:
            if type(config_filename) is not str:
                raise ValueError(f"config_filename parameter must be str: "
                                 f"got {type(config_filename)}")

            with open(config_filename, "r") as f:
                self._parsed_json = json.loads(f.read())
        else:
            if type(existing_parsed_json_dict) is not dict:
                raise ValueError(f"existing_parsed_json_dict parameter must "
                                 f"be dict: got "
                                 f"{type(existing_parsed_json_dict)}")
            self._parsed_json = copy.deepcopy(existing_parsed_json_dict)

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
        importlib.invalidate_caches()
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def get_instance(self, class_name, module_name, **kwargs):
        """
        Get instance of class with class_name from module_name.

        :param class_name: str
            Name of the class to be created.

        :param module_name: str
            Name of the module which stores class with class_name.

        :param kwargs: dict
            Additional parameters which pass into constructor of needed class.

        :return: instance of class_name from module_name with kwargs params
        """
        return self.get_class(class_name, module_name)(**kwargs)

    def get_internal_params(self, list_name, internal_label=None):
        """
        Get internal dict based on name (and internal label).

        :param list_name: str
            Name of the global list in config file.

        :param internal_label: str, optional (default=None)
            Name of the internal field in the global list with dicts.

        :return: list, dict
            If label is not passed return lit with dicts otherwise return
            internal dict with label.
        """
        global_list_with_dicts = self[list_name]
        if internal_label is None:
            return global_list_with_dicts

        for internal_dict in global_list_with_dicts:
            if internal_label in internal_dict.values():
                return internal_dict
        raise KeyError(f"Not found key {internal_label} in {list_name}!")

    def get_params_for(self, label):
        """
        Get class name, module name and parameters for label tool.

        :param label: str
            Name of the tool which need to parse in config file.

        :return: dict {"class_name": str, "module_name": str, "params": dict)
            Tuple with label class name, label module name and parameters.
        """
        class_name = self[f"selected_{label}"]
        internal_dict = self.get_internal_params(f"{label}s", class_name)

        return {
            "class_name": class_name,
            "module_name": internal_dict[f"{label}_module_name"],
            "params": internal_dict[f"{label}_params"]
        }

    def get_metric(self):
        """
        Get name of selected metric class from config.

        :return: str
            Class name of the metric.
        """
        metric_name = self["selected_metric"]
        return self["metrics"][metric_name]

    def get_tester_params(self):
        """
        Get parameters from config for tester class.

        :return: dict
            Extract parameters from parsed json config.
        """
        return self["tester_params"][0]
