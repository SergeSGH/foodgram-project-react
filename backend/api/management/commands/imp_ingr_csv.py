import pandas as pd
from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Импорт данных из файла .csv в модель. \
        Ввод аргументов в формате: model fields_number field_names'

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='+')

    def handle(self, **kwargs):
        names = kwargs['models']
        fields = []
        for i in range(int(names[1])):
            fields.append(names[2 + i])
        names = names[:1]
        models = {
            model.__name__: model for model in apps.get_models()
        }
        for name in names:
            try:
                df = pd.read_csv(f'../data/{name}.csv')
                list_last_rows = df.to_dict('records')
                list_first_row = {}
                for key in list_last_rows[0].keys():
                    list_first_row[key] = key
                record_list = [list_first_row]
                record_list += list_last_rows
                dict = []
                for record in record_list:
                    new_record = {}
                    field_n = 0
                    for key in list_last_rows[0].keys():
                        new_record[fields[field_n]] = record[key]
                        field_n += 1
                    dict.append(new_record)
                for i in range(len(dict)):
                    models[name].objects.get_or_create(**dict[i])
                print(f'The model {name} imported sucessfully!')
            except BaseException as e:
                print(f'For the model {name} {e}')
