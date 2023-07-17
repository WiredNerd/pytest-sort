from pytest import Config


class SortConfig:
    def __init__(self, config: Config):
        self._config = config

    @property
    def mode(self):
        return self._config.getoption('sort_mode', 'none')

    @property
    def bucket(self):
        return self._config.getoption('sort_bucket', 'module')
