import csv

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ('Импорт данных из файла .csv в модель. '
            'Ввод аргументов в формате: model fields_number field_names')

    def add_arguments(self, parser):
        parser.add_argument('arguments', nargs='+')

    def handle(self, **kwargs):
        args = kwargs['arguments']
        fields = []
        for i in range(int(args[1])):
            fields.append(args[2 + i])
        name = args[0]
        model = {
            model.__name__: model for model in apps.get_models()
        }[name]
        try:
            with open(f'../data/{name}.csv', encoding='utf-8') as df:
                file_reader = csv.reader(df)
                for row in file_reader:
                    counter = 0
                    record = {}
                    for column in row:
                        record[fields[counter]] = column
                        counter += 1
                    model.objects.get_or_create(**record)
            print(f'The model {name} imported sucessfully!')
        except BaseException as e:
            print(f'For the model {name} {e}')
