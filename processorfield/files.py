import os
from django.db.models.fields.files import FieldFile
from django.core.files.base import ContentFile

def change_file_extension(filename, ext):
    return '%s%s%s'%(os.path.splitext(filename)[0],os.extsep,ext)


class InnnerProccessorFieldFile(FieldFile):
    def __init__(self, instance, field, name, alias, processor):
        super(InnnerProccessorFieldFile, self).__init__(instance, field, name)
        self.alias = alias
        self.processor = processor
        if self.name:
            self.name = self.field.generate_filename(self.instance, self.filename(self.name), self.directory())

    def filename(self, name):
        filename = getattr(self.processor, 'filename', None)
        ext = getattr(self.processor, 'ext', None)
        if hasattr(filename, '__call__'):
            return filename(self.instance)
        elif filename:
            return filename
        elif ext:
            return change_file_extension(name, ext)
        return name

    def directory(self):
        directory = getattr(self.processor, 'directory', None)
        if hasattr(directory, '__call__'):
            return directory(self.instance)
        elif directory:
            return directory
        return self.alias

    def save(self, name, content):
        content = ContentFile(self.processor(content))

        name = self.field.generate_filename(self.instance, self.filename(name), self.directory())
        self.name = self.storage.save(name, content)

        # Update the filesize cache
        self._size = content.size
        self._committed = True

    save.alters_data = True

    def delete(self):
        if not self:
            return
        # Only close the file if it's already open, which we know by the
        # presence of self._file
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name)

        self.name = None
        # Delete the filesize cache
        if hasattr(self, '_size'):
            del self._size
        self._committed = False

    delete.alters_data = True

class ProcessorFieldFile(FieldFile):
    def __init__(self, *args, **kwargs):
        super(ProcessorFieldFile, self).__init__(*args, **kwargs)
        self._processors = {}
        for alias, processor in self.field.iterprocessors():
            self._processors[alias] = InnnerProccessorFieldFile(self.instance, self.field, self.name, alias, processor)

    def save(self, name, content, save=True):
        super(ProcessorFieldFile, self).save(name, content, save)
        if not content: return
        for _, processor in self._processors.iteritems():
            processor.save(name, content)

    def reprocess(self, *aliases):
        file = self.file
        if not file: return
        aliases = aliases or self._processors.keys()
        for alias in aliases:
            if alias not in self._processors:
                meta = self.field.model._meta
                raise Exception('"%s" alias doesnt exists in %s.%s.%s'%(alias, meta.app_label, meta.object_name, self.field.name))
            processor = self._processors[alias]
            processor.save(file.name, file)

    def delete(self, save=True):
        super(ProcessorFieldFile, self).delete(save)
        for _, processor in self._processors.iteritems():
            processor.delete()

    @property
    def aliases(self):
        return self._processors.keys()

    def __getitem__(self, alias):
        return self._processors[alias]
