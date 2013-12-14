import os
from django.db import models
from django import forms

from .files import ProcessorFieldFile
from .widgets import ClearableProcessedFileInput

class FileFieldProcessor(forms.FileField):
    widget = ClearableProcessedFileInput

class FileProcessorField(models.FileField):
    attr_class = ProcessorFieldFile
    def __init__(self, *args, **kwargs):
        self._processors = {}
        processors = kwargs.pop('processors', None)
        if processors:
            for alias, processor in processors.iteritems():
                self[alias] = processor
        super(FileProcessorField, self).__init__(*args, **kwargs)

    def __getitem__(self, alias):
        return self._processors[alias]

    def __setitem__(self, alias, value):
        self._processors[alias] = value

    def iterprocessors(self):
        return self._processors.iteritems()

    def generate_filename(self, instance, filename, subdir=None):
        return os.path.join(self.get_directory_name(), subdir or '', self.get_filename(filename))

    def formfield(self, **kwargs):
        defaults = {'form_class': FileFieldProcessor}
        defaults.update(kwargs)
        field = super(FileProcessorField, self).formfield(**defaults)
        field.widget = ClearableProcessedFileInput()
        return field

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^processorfield\.fields\.FileProcessorField"])
except ImportError:
    pass
