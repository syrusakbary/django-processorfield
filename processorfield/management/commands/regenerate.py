import sys
from collections import OrderedDict
from optparse import make_option
from django.db import models
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured

from processorfield import FileProcessorField

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--alias', dest='alias', action='append', default=[],
            help='Specifies the output serialization format for fixtures.'),
        make_option('-e', '--exclude', dest='exclude',action='append', default=[],
            help='An appname or appname.ModelName to exclude (use multiple --exclude to exclude multiple apps/models).'),
        make_option('-a', '--all', action='store_true', dest='all', default=False,
            help="Use Django's base manager to dump all models stored in the database, including those that would otherwise be filtered or modified by a custom manager."),
    )
    help = 'Regenerate the processor fields for each model in the apps'
    args = '[appname appname.ModelName ...]'
    can_import_settings = True
    def handle(self, *app_labels, **options):
        from django.conf import settings
        from django.db.models import get_app, get_apps, get_model, get_models
        from django.utils import translation
        translation.deactivate()
        alias = options.get('alias')
        excludes = options.get('exclude')
        all = options.get('all')

        excluded_apps = set()
        excluded_models = set()
        for exclude in excludes:
            if '.' in exclude:
                app_label, model_name = exclude.split('.', 1)
                model_obj = get_model(app_label, model_name)
                if not model_obj:
                    raise CommandError('Unknown model in excludes: %s' % exclude)
                excluded_models.add(model_obj)
            else:
                try:
                    app_obj = get_app(exclude)
                    excluded_apps.add(app_obj)
                except ImproperlyConfigured:
                    raise CommandError('Unknown app in excludes: %s' % exclude)

        if len(app_labels) == 0:
            app_list = OrderedDict((app, None) for app in get_apps() if app not in excluded_apps)
        else:
            app_list = OrderedDict()
            for label in app_labels:
                try:
                    app_label, model_label = label.split('.')
                    try:
                        app = get_app(app_label)
                    except ImproperlyConfigured:
                        raise CommandError("Unknown application: %s" % app_label)
                    if app in excluded_apps:
                        continue
                    model = get_model(app_label, model_label)
                    if model is None:
                        raise CommandError("Unknown model: %s.%s" % (app_label, model_label))

                    if app in app_list.keys():
                        if app_list[app] and model not in app_list[app]:
                            app_list[app].append(model)
                    else:
                        app_list[app] = [model]
                except ValueError:
                    # This is just an app - no model qualifier
                    app_label = label
                    try:
                        app = get_app(app_label)
                    except ImproperlyConfigured:
                        raise CommandError("Unknown application: %s" % app_label)
                    if app in excluded_apps:
                        continue
                    app_list[app] = None

        model_list = OrderedDict()
        for app, app_models in app_list.iteritems():
            app_models = app_models or get_models(app) or []
            for model in app_models:
                fields = []
                for field in model._meta.fields:
                    if isinstance(field, FileProcessorField):
                        fields.append(field)
                if fields:
                    model_list[model] = fields
        
        spaces = ' '*20
        for model, fields in model_list.iteritems():
            field_names = [f.name for f in fields]
            base = "Processing %s in %s.%s"%(', '.join(field_names), model._meta.app_label, model._meta.object_name)
            sys.stdout.write(base)
            sys.stdout.flush()
            try:
                instances = model.objects.only(*field_names).all()[:]
                count = len(instances)
                total = (count*len(fields))
                enumerated_fields = list(enumerate(fields))
                for i, instance in enumerate(instances):
                    for j, field in enumerated_fields:
                        current = float(i+j)
                        sys.stdout.write("\r\033[93m[IN PROGRESS]\033[0m %s [%d/%d] (%d%%)" %(base, current, total, current/total*100))
                        sys.stdout.flush()
                        file = getattr(instance, field.name)
                        file.reprocess(*alias)
                sys.stdout.write("\r\033[92m[COMPLETED]\033[0m %s%s\n"%(base,spaces))
                sys.stdout.flush()
            except Exception, e:
                sys.stdout.write("\r\033[91m[FAILED]\033[0m %s%s\n"%(base,spaces))
                sys.stdout.flush()
                raise e
