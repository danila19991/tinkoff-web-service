import json
import functools
import logging
import logging.config
import time


# TODO(Timur): need to write doc for your functions. And you nothing wrote
#              about parameters of your functions.
def setup_logging(config_filename="log_config.json"):
    with open(config_filename, 'r') as logging_configuration_file:
        config = json.load(logging_configuration_file)
    logging.config.dictConfig(config)


def decor_exception(func):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occurred.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logging.exception(f"Exception occurred in {func.__name__} with "
                              f"arguments %s %s!",
                              args,
                              kwargs,
                              exc_info=False)
            # Re-raise the exception.
            raise
    return wrapper


def decor_timer(func):
    """
    A decorator that wraps the passed in function and logs lead time.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        duration = time.time() - start
        logging.debug(
            f"{func.__name__} completed in {duration * 1000:.8f}ms.")
    return wrapper


def decor_class_logging_error_and_time(*method_names):
    def class_rebuild(cls):
        class NewClass(cls):
            def __getattribute__(self, attr_name):
                obj = super(NewClass, self).__getattribute__(attr_name)
                if hasattr(obj, "__call__") and attr_name in method_names:
                    return decor_timer(decor_exception(obj))
                return obj

        return NewClass
    return class_rebuild
