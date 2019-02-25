import os

from django.apps import apps
from django.contrib.staticfiles import utils
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage


class AngularTemplateFinder(BaseFinder):
    """Incomplete implementation of a finder. Only implements list."""
    storage_class = FileSystemStorage
    source_dir = 'static'
    app_name = 'web'

    def __init__(self, *args, **kwargs):
        """Init the finder."""
        self.storage = None
        app_config = apps.get_app_config(self.app_name)
        app_storage = self.storage_class(
            os.path.join(app_config.path, self.source_dir)
        )
        if os.path.isdir(app_storage.location):
            self.storage = app_storage
        super().__init__(*args, **kwargs)

    def list(self, ignore_patterns):
        """
        List all html angular templates in the web app.

        :param ignore_patterns: Collection of patterns to ignore
        :type ignore_patterns: list
        :yields: (path, storage object) tuple
        :ytype: tuple
        """
        if self.storage.exists(''):
            for path in utils.get_files(self.storage, ignore_patterns):
                if path.startswith('web/html') and path.endswith('.html'):
                    yield path, self.storage
