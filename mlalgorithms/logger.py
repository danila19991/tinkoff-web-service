import json
import functools
import logging
import logging.config
import time
import types


def _log_newline(self, how_many_lines=1):
    """
    Add option to log blank new line at Streams.

    :param self: logging.Logger
        Instance of Logger object.

    :param how_many_lines: int
        Define how many lines Logger should write.
    """
    # Switch handler, output a blank line.
    self.addHandler(self.blank_handler_console)
    self.addHandler(self.blank_handler_file)
    self.removeHandler(self.console_handler)
    self.removeHandler(self.file_handler)

    for i in range(how_many_lines):
        self.info("")

    # Switch back.
    self.removeHandler(self.blank_handler_console)
    self.removeHandler(self.blank_handler_file)
    self.addHandler(self.console_handler)
    self.addHandler(self.file_handler)


def _configure_logger():
    """
    Add to logger attributes handlers and add method for Logger object.
    """
    logger = get_logger()

    # Save some data and add a method to logger object.
    logger.console_handler = logger.handlers[0]
    logger.blank_handler_console = logger.handlers[1]
    logger.file_handler = logger.handlers[2]
    logger.blank_handler_file = logger.handlers[3]
    logger.newline = types.MethodType(_log_newline, logger)

    logger.removeHandler(logger.blank_handler_console)
    logger.removeHandler(logger.blank_handler_file)


def get_logger():
    """
    Get current logger for library.

    :return: logging.Logger
        Reference to library logger.
    """
    return logging.getLogger("mlalgorithms")


def setup_logging(config_filename="log_config.json"):
    """
    Setup logging for the library.

    :param config_filename: str
        File name of the logger config.
    """
    with open(config_filename, "r") as logging_configuration_file:
        config = json.load(logging_configuration_file)
    logging.config.dictConfig(config)
    _configure_logger()

    # ATTENTION! Do not see at the warning on next code line, in
    # _configure_logger method we add newline method for Logger instance.
    get_logger().newline()


def decor_exception(func):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occurred.

    :param func: function
        Function to decorate.

    :return function
        Decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            get_logger().exception(f"Exception occurred in {func.__name__} "
                                   f"with arguments %s %s!",
                                   args,
                                   kwargs,
                                   exc_info=False)
            # Re-raise the exception.
            raise
    return wrapper


def decor_timer(func):
    """
    A decorator that wraps the passed in function and logs lead time.

    :param func: function
        Function to decorate.

    :return function
        Decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        get_logger().debug(f"function: {func.__name__}"
                           f"\t\tdate: {time.asctime(time.gmtime(start))}.")
        result = func(*args, **kwargs)
        end = time.time()
        duration = end - start
        get_logger().debug(
            f"function: {func.__name__}"
            f"\t\tdate: {time.asctime(time.gmtime(end))}"
            f"\t\ttime: {duration * 1000:.8f}ms."
        )
        return result
    return wrapper


def decor_class_logging_error_and_time():
    """
    Decorate all methods in class.

    :return: function
        Class with decorated methods.
    """
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr,
                        decor_timer(decor_exception(getattr(cls, attr))))
        return cls
    return decorate
