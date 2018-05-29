##### 0. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/requirements.txt 
> в задании указано 
не использовать сторонние инструменты (ну для проверки стиля можно, конечно)

**Комментарий.** Там по-сути три сторонние библиотеки - pyyaml, т.к. конфиг я yaml. Можно передать на json-конфиг, 
но сути это не меняет. Ну и вы разрешили использовать yaml.mock для тестов, на тот момент не разобрался с unittest.mock, но и в целом только один тест с использованием mock
.patch оставил как напоминание себе.  
flake8 - без комментариев  
Остальное подтянуто по зависимостям.

##### 1. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/logs/log_analyzer.log - 
>(1) логи не 
надо коммитить в гит (2) конфиг в лог не распечатывают, это небезопасно

**Комментарий.** Поправил

##### 2. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L24
> в кастомных эксепшенах нет необходимости скрипту на 300 LOC

**Комментарий.** Я хочу выходить с разными exit status'ами в зависимости от произошедшего.  
Я долго думал как сделать, из того что обдумывал:
* выходить сразу в функции, когда нужно.
* проверять ли return у каждой функции на None или как-то по другому, 

Но то, что я реализовал описано в офф доке (возможно, конечно, я неправильно понял) - 
https://docs.python.org/2/howto/doanddont.html#exceptions
>or a catch-all in a main function.

Как бы вы сделали выход в моем случае ?

##### 3. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L217
>зачем print'ы, если есть логирование? если есть желание писать в stdout, то при настройте логгинга передавайте 
filename=None, если есть желание писать в лог и консоль (но зачем?) настройтке логгинг соответствующим образом.

**Комментарий.** Вот часто приходится запускать скрипты/демоны в консоли и не понимать что происходит. А для того, 
чтобы понять, что есть какая-то ошибка нужно открывать вторую консоль с `tail -F log` или править предварительно 
конфиг. Хотелось избежать этой ситуации. Удалил принты.

##### 4. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L243
 > какой толк от перечисления всех этих вариантов эксепшенов? в данном месте же задача в том, чтобы залогировать 
 неотловленные (неожиданные) ошибки. Достаточно try...except: logging.exception. И в такой блок можно прямо вызов main 
 обернуть. Т.е. нужно проще и лаконичнее.

Комментарий дан в П2.
```python
# нужен, чтобы корректно выходить, когда, к примеру, argparse выходит (кидает SystemExit)
except SystemExit: 
```

##### 5. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L182
>а если еще параметры добавяться? ну то есть вы скорее хотите функцию, которая возвращает распаршенные аргументы, а 
не ожин конкретный

**Комментарий.** Поправил.

##### 6. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L199
> использование метода update куда более очевидно, на мой взгляд

**Комментарий.** Гугл выдает первое решение такое https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
```Python
In Python 3.5 or greater, :

z = {**x, **y}
In Python 2, (or 3.4 or lower) write a function:

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z
``` 
https://docs.python.org/dev/whatsnew/3.5.html#pep-448-additional-unpacking-generalizations

Я бы хотел использовать свежие фишки языка и а тут надо писать две строчки вместо одной.... Скрепя сердцем исправил.

##### 7. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L184
> у этого пути есть дефолтное значние, кстати, согласно ТЗ

**Комментарий.** Неправильно понял комментарий в слаке, исправил.

8. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L32 - то, как функция называется и то, что она делает на самом деле - почему-то две разные вещи. Наверное, хочется иметь отдельно функцию, которая ищет последний лог и отдельно проверку есть ли соответсвующий репорт
##### 9. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L46
>согласно ТЗ это не является ошибкой

**Комментарий.** Заменил на DoneException, теперь выходит с 0

##### 10. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L49
>sorted более идеоматично

**Комментарий.** Тогда мне надо будет писать такое ?
```python
log_files = sorted(log_files)
```

##### 11. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L54
>вот вместо того, чтобы глобом искать, потом фильтровать, а потом еще раз парсить, можно было один раз по файлам 
пройтись и выпарсить даты сразу

**Комментарий.** Вот пошел сейчас упрощать... Раньше было понятно, что мы выходим что нет логов в каталоге или все 
логи были распарсены, а если схлопывать в один проход, то это одно и тоже действие... 

##### 12. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L58
>это я не понял к чему

**Комментарий.** В этот месте сделать что-то типа транзакции. Вот мы открыли лог, распарсили, начали записывать 
репорт и тут сервер перезагрузили. Репорт так и останется битым. Если в конце операции класть report-yyyy.mm.yy.html
.md5 файл, то при следующем прогоне скрипта можно перезаписать битый репорт, если нет md5-файла.

##### 13. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L140
>кажется эти три функции про чтения файла можно в одну объудинить. Та и кода меньше дублироваться будет

**Комментарий.** Не знаю прям уж... Мне кажется тяжело читаемой и 4 вложения, да и тестировать тяжело. В одном месте
 gzip.open, в другом просто open, в одном c decode, во втором нет. Наверно я не вижу тут решения из-за 
отсутствия опыта. Как бы вы тут поступили ?
```python
def return_read_log_file(filename):
    if re.match(".*\.gz$", filename):
        with gzip.open(filename, 'rb') as log_file:
            for line in log_file:
                yield line.decode()
    else:
        with open(filename) as log_file:
            for line in log_file:
                yield line
```

##### 14. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L94
> опять же, функция парсинга почему-то вызывает подсчет статистики сама. Это, например, тестировать не особо удобно

**Комментарий.** Согласен, имя не удачное, переименовал. Тесты на нее были:
```python
    def test_parse_log_file(self):
        self.assertEqual(log_analyzer.parse_log_file("log2/1.log", 1, 1.0), {'/api/v2/banner/25019354': {'count': 2,
                                        'count_perc': 40.0, 'time_avg': 5.768, 'time_max': 6.146, 'time_med': 5.768,
                                         'time_perc': 91.759, 'time_sum': 11.536}})

        self.assertEqual(log_analyzer.parse_log_file("log2/2.log", 1, 1.0), {})
```

##### 15. https://github.com/f4rx/Otus-Python-2018-05/blob/HW_01/hw_01_log_analyzer/log_analyzer.py#L165
>https://docs.python.org/3.6/library/string.html#string.Template.safe_substitute

**Комментарий.** Да, искал такое, но думал о джинже, спасибо. Но вопрос - тут надо читать весь файл целиком, а моем 
случае я читал и записывал его построчно. Памяти не больше будет тратиться пока файл-темплейт в памяти ?
