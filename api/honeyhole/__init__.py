class Environment(object):
    PROD = 1
    DEV0 = 2
    USER = 3
    TEST = 4

    _active_environment = None

    @classmethod
    def set(cls, env):
        cls._active_environment = env

    @classmethod
    def get(cls):
        return cls._active_environment


def set_default_environment():
    Environment.set(Environment.DEV0)


set_default_environment()