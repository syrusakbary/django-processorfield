from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe


class ClearableProcessedFileInput(ClearableFileInput):
    template_with_super = (
        u'%(clear_template)s'
        u'%(aliases)s'
    )
    template_with_processor = u'<p><b>%(alias)s</b>: <a href="%(file_url)s">%(file_name)s</a></p>'
    template_with_initial = ('<p class="file-upload">%s</p>'
                            % ClearableFileInput.template_with_initial)
    template_with_clear = ('<span class="clearable-file-input">%s</span>'
                           % ClearableFileInput.template_with_clear)


    def render(self, name, value, attrs=None):
        clear_template = super(ClearableProcessedFileInput, self).render(
            name, value, attrs)

        aliases = ""
        if value and hasattr(value, "aliases"):
            for alias in value.aliases:
                file = value[alias]
                file_url = file.url
                file_name = file.name
                aliases += self.template_with_processor%{'alias':alias, 'file_url': file_url, 'file_name': file_name}
        return mark_safe(self.template_with_super%{'clear_template': clear_template, 'aliases':aliases})

        # if not value or not hasattr(value, 'storage'):
        #     return output
        # thumb = self.get_thumbnail(value)
        # substitution = {
        #     'template': output,
        #     'thumb': thumb.tag(id=self.thumbnail_id(name)),
        #     'source_url': value.storage.url(value.name),
        # }
        # return mark_safe(self.template_with_thumbnail % substitution)
