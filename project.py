import os
import csv


class PriceMachine:

    def __init__(self):
        self.data = []

    def load_prices(self, directory):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
        '''
        for filename in os.listdir(directory):
            if 'price' in filename.lower() and filename.endswith('.csv'):
                file_path = os.path.join(directory, filename)
                print(f"Обрабатывается файл: {file_path}")
                self._read_csv(file_path)

    def _read_csv(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames  # Получаем заголовки
            print(f"Заголовки: {headers}")  # Отладочная информация
            product_idx, price_idx, weight_idx = self._search_product_price_weight(headers)

            for row in reader:
                product = row[headers[product_idx]]
                price = float(row[headers[price_idx]])
                weight = float(row[headers[weight_idx]])
                price_per_kg = price / weight if weight > 0 else 0
                self.data.append({
                    'product': product,
                    'price': price,
                    'weight': weight,
                    'price_per_kg': price_per_kg,
                    'file': os.path.basename(file_path)
                })

    def _search_product_price_weight(self, headers):
        '''
            Возвращает номера столбцов
        '''
        try:
            product_idx = next(
                i for i, h in enumerate(headers) if h.lower() in ['товар', 'название', 'наименование', 'продукт'])
            price_idx = next(i for i, h in enumerate(headers) if h.lower() in ['розница', 'цена'])
            weight_idx = next(i for i, h in enumerate(headers) if h.lower() in ['вес', 'масса', 'фасовка'])
        except StopIteration as e:
            print("Ошибка: не найден один из необходимых столбцов.")
            raise e  # Прекращаем выполнение, если не удалось найти необходимые индексы
        return product_idx, price_idx, weight_idx

    def export_to_html(self, fname='output.html'):
        # Сортируем данные по цене за кг. перед экспортом
        sorted_data = sorted(self.data, key=lambda x: x['price_per_kg'])

        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
            <style>
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid black; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <table>
                <tr>
                    <th>№</th>
                    <th>Наименование</th>
                    <th>Цена</th>
                    <th>Вес</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for index, item in enumerate(sorted_data, start=1):
            result += f'''
                <tr>
                    <td>{index}</td>
                    <td>{item['product']}</td>
                    <td>{item['price']}</td>
                    <td>{item['weight']}</td>
                    <td>{item['file']}</td>
                    <td>{item['price_per_kg']:.2f}</td>
                </tr>
            '''
        result += '''
            </table>
        </body>
        </html>
        '''
        with open(fname, 'w', encoding='utf-8') as file:
            file.write(result)
        return fname

    def find_text(self, text):
        # Реализация поиска текста в названиях продуктов
        found_items = [item for item in self.data if text.lower() in item['product'].lower()]
        return found_items

    def display_results(self, results):
        if not results:
            print("Не найдено товаров по вашему запросу.")
            return
        print(f"{'№':<3} {'Наименование':<30} {'Цена':<6} {'Вес':<6} {'Файл':<15} {'Цена за кг.':<10}")
        for index, item in enumerate(results, start=1):
            print(
                f"{index:<3} {item['product']:<30} {item['price']:<6} {item['weight']:<6} {item['file']:<15} {item['price_per_kg']:.2f}")


pm = PriceMachine()
pm.load_prices('D:\\PythonProject\\pythonProject')  # Укажите путь к каталогу с файлами
print('Загруженные данные:', pm.data)

# Циклический ввод от пользователя
while True:
    search_text = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
    if search_text.lower() == 'exit':
        print("Работа программы завершена.")
        break

    # Поиск товаров по фрагменту названия
    results = pm.find_text(search_text)

    # Сортировка по цене за кг. (по возрастанию)
    results.sort(key=lambda x: x['price_per_kg'])

    # Вывод результатов
    pm.display_results(results)

# Экспорт данных в HTML
output_file = pm.export_to_html()
print(f'Данные экспортированы в HTML файл: {output_file}')
