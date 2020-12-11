from django.apps import AppConfig


class RmmapiConfig(AppConfig):
    name = 'rmmapi'

    def ready(self):
        import rmmapi.signals.handlers
