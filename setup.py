from setuptools import setup, find_packages

setup(name='django-processorfield',
      version = '0.1',
      download_url = 'git@github.com:syrusakbary/django-processorfield.git',
      packages = find_packages(),
      author = 'Syrus Akbary',
      author_email = 'me@syrusakbary.com',
      description = 'A powerful filefield for Django with multiple processor outputs',
      long_description=open('README.rst').read(),
      keywords = 'django process processor field file thumbnails',
      url = 'http://github.com/syrusakbary/django-processorfield',
      platforms='any',
      license = 'BSD',
      install_requires=[
          'django>=1.4',
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Multimedia :: Graphics',
          'Framework :: Django',
      ],
    )