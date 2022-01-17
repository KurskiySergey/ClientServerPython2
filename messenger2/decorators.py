import logging
from messenger2.logs.log_configs import client_log_config, server_log_config
from messenger2.protocols.JIM import JIM
import traceback
import sys

WAY = traceback.format_stack()[0].split()[1].strip('",').split('/')[-1]
if WAY == 'server_start.py':
    LOGGER = logging.getLogger(server_log_config.SERVER_LOGGER)
else:
    LOGGER = logging.getLogger(client_log_config.CLIENT_LOGGER)


def log_exception(exception):

    def deco(func):
        def wrap(*args, **kwargs):

            try:
                log_msg = f'Была вызвана функция {func.__name__} с параметрами {args}, {kwargs} ' \
                          f'В модуле {func.__module__}'
                LOGGER.info(log_msg)
                return func(*args, **kwargs)

            except exception:

                log_msg = f'Возникла критическая ошибка в функции {func.__name__}' \
                          f'С параметрами {args}, {kwargs}' \
                          f'В модуле {func.__module__}' \
                          f'В файле {WAY}'
                LOGGER.critical(log_msg)
                LOGGER.critical(traceback.format_exc())
                sys.exit(-1)

        return wrap

    return deco


def thread_lock(locker):

    def deco(func):

        def wrap(*args, **kwargs):
            locker.acquire()
            result = func(*args, **kwargs)
            locker.release()
            return result

        return wrap

    return deco


class LogException:

    def __init__(self, exception):
        self.exception = exception

    def __call__(self, func):

        def deco(*args, **kwargs):
            try:
                log_msg = f'Была вызвана функция {func.__name__} с параметрами {args}, {kwargs} ' \
                          f'В модуле {func.__module__}'
                LOGGER.info(log_msg)
                return func(*args, **kwargs)

            except self.exception:
                log_msg = f'Возникла критическая ошибка в функции {func.__name__}' \
                          f'С параметрами {args}, {kwargs}' \
                          f'В модуле {func.__module__}' \
                          f'В файле {WAY}'
                LOGGER.critical(log_msg)
                LOGGER.critical(traceback.format_exc())
                sys.exit(-1)

        return deco


if __name__ == "__main__":
    pass
