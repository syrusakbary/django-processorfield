=====================
Django-processorfield
=====================

A powerful filefield with multiple processor outputs.


Installation
============

Run ``pip install django-processorfield``, or for the `in-development version`__
run ``pip install django-processorfield==dev``.

__ https://github.com/syrusakbary/django-processorfield/tarball/master#egg=django-processorfield

Add ``processorfield`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'processorfield',
    )


Fields
======

You can use ``FileProcessorField`` for easier
access to retrieve or process files.

For example:: python

    from processorfield.fields import FileProcessorField
    from PIL import Image
    import StringIO

    size = (100, 100)

    def thumbnail(imagefile):
        output = StringIO.StringIO()
        im = Image.open(imagefile)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(outfile, "JPEG")
        return outfile

    class Profile(models.Model):
        user = models.OneToOneField('auth.User')
        photo = FileProcessorField(upload_to='photos', processors={'thumbnail':thumbnail}, blank=True)

Accessing the field's predefined alias in a template:: jinja

    <img src="{{ profile.photo.thumbnail.url }}" alt="" />

Accessing the field's predefined alias in Python code:: python

    thumb_url = profile.photo['thumbnail'].url

