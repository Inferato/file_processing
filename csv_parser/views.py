import pandas as pd
import hashlib
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse

@method_decorator(csrf_exempt, name='dispatch')
class ProcessCSVView(View):
    template_name = 'process_csv.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            # Читання CSV файла
            df = pd.read_csv(csv_file)

            # Функція для заміни символів та сумування останнього стовбця
            def process_dataframe(df):
                # Заміна символів
                df.replace({'С': 'S', 'Т': 'T'}, inplace=True)
                # Сортування за останнім стовбцем
                df.sort_values(by=df.columns[-1], inplace=True)
                # Додавання нового стовбця
                df.insert(1, 'Property', 'None')
                # Сумування останнього стовбця
                last_column_sum = df.iloc[:, -1].sum()
                return df, last_column_sum

            # Обробка даних
            processed_df, last_column_sum = process_dataframe(df)

            # Запис до CSV файла з роздільником ";"
            processed_csv = processed_df.to_csv(index=False, sep=';')

            # Вирахування MD5 хеша файлу
            md5_hash = hashlib.md5(processed_csv.encode()).hexdigest()


            # Функція для запису DataFrame у JSON файл
            def write_to_json(df):
                json_data = {}
                columns = df.columns.to_list()
                for column in columns:
                    json_data[column] = df[column].tolist()
                return json_data

            # Запис до JSON файла
            processed_json = write_to_json(processed_df)

            # Збереження обробленого CSV файла на сервері
            processed_csv_filename = 'processed_csv.csv'
            processed_csv_path = f'media/{processed_csv_filename}'
            with open(processed_csv_path, 'w') as f:
                f.write(processed_csv)

            # Підготовка контексту для передачі в шаблон
            context = {
                'processed_csv_url': processed_csv_path,
                'md5_checksum': md5_hash,
                'last_column_sum': last_column_sum,
                'processed_json': processed_json,
            }

            return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, {'error_message': 'No CSV file uploaded.'})
        