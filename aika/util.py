import locale


class LocaleManager:
    """
    Context manager for temporarily overriding the system locale.

    https://stackoverflow.com/questions/50737783/temporarily-override-locale-with-a-context-manager
    """

    def __init__(self, localename):
        self.name = localename
        self.backup = None

    def __enter__(self):
        self.backup = locale.getlocale(locale.LC_CTYPE)
        locale.setlocale(locale.LC_ALL, self.name)

    def __exit__(self, exc_type, exc_value, traceback):
        locale.setlocale(locale.LC_ALL, self.backup)
