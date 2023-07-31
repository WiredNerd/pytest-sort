from pytest import Config


class SortConfig:
    mode = 'none'
    bucket = 'module'
    record = False
    reset = False

    @staticmethod
    def from_pytest(config: Config):
        SortConfig.mode = config.getoption('sort_mode', 'none')
        SortConfig.bucket = config.getoption('sort_bucket', 'module')
        SortConfig.record = config.getoption('sort_record', False)
        if SortConfig.mode == 'fastest':
            SortConfig.record = True

        SortConfig.reset = config.getoption("sort_reset_times", False)

    @staticmethod
    def dict():
        config = {
            "sort-mode": SortConfig.mode,
        }

        if not SortConfig.mode == 'none':
            config["sort-bucket"] = SortConfig.bucket

        if SortConfig.reset:
            config["sort-reset-times"] = True

        if SortConfig.record:
            config["sort-record-times"] = True

        return config
