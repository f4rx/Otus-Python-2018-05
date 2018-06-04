## log_analyzer

### Описание
log_analyzer.py - берет один последний лог из каталога logs, для которого еще не сделан отчет в каталоге reports, 
парсит урл и время повылнения запроса. Далее по условиям задания записывает ститиску в reports/report-YYYY.MM.DD
.html файл.

```bash
usage: log_analyzer.py [-h] -c CONFIG

Parse log files.

optional arguments:
  -h, --help                    show this help message and exit
  -c CONFIG, --config CONFIG    path to conf.yaml
```

Пример использования:
```bash
$ python3 log_analyzer.py -c conf.yaml
Working with file './log/nginx-access-ui.log-20170629.gz'
Отчет был записан в ./reports/report-2017.06.29.html

```

### Конфирурация
Дефолтные значения скрипта:
```python
global_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOG_FILE": None,
    "PARSE_ERROR_PERC": 1.0,
}
```
Значения можно переопределить в yaml-файле и подключать его через опции -c/--conf
```yaml
REPORT_SIZE: 1000
REPORT_DIR: ./reports
LOG_DIR: ./log
#LOG_FILE: null
LOG_FILE: logs/log_analyzer.log
```

* REPORT_SIZE - суммарное количество времени запроса по данному урлу
* REPORT_DIR - каталог с отчетами
* LOG_DIR - каталог с логами nginx
* LOG_FILE - путь к файлу для сохранения логов или `null` для вывода логов в stdout

### Тестирование
Писал первый раз тесты в жизни, для маленьких функций сделал простые юниттесты, но все остальные функции хоть и не 
большие, но читают/пишут в файл, или работают с директориями из-за чего пошел по пути сервисного (или системного) 
тестирования, представляя, что функция для меня blackbox. И мне важны конечные данные - что найден нужный файл в 
каталоге или выкинуто исключение, если каталог не найдет.

По этой причине тестирование проходит в докер контейнере, в котором создается тестовое окружение башовским скриптом.
 Для упрощения запуска сделал Makefile и докер-композ.
```bash
$ make test
docker-compose down && docker-compose  up
Removing hw01loganalyzer_log_analyzer_1 ... done
Removing network hw01loganalyzer_default
Creating network "hw01loganalyzer_default" with the default driver
Creating hw01loganalyzer_log_analyzer_1 ... done
Attaching to hw01loganalyzer_log_analyzer_1
log_analyzer_1  | test_check_log_filename (__main__.LogAnalyzerTest) ... ok
log_analyzer_1  | test_get_date_from_filename (__main__.LogAnalyzerTest) ... ok
log_analyzer_1  | test_merge_config (__main__.LogAnalyzerTest) ... ok
log_analyzer_1  | test_parse_log_file (__main__.LogAnalyzerTest) ... ok
log_analyzer_1  | test_return_read_log_file (__main__.LogAnalyzerTest) ... ok
log_analyzer_1  |
log_analyzer_1  | ----------------------------------------------------------------------
log_analyzer_1  | Ran 5 tests in 0.012s
log_analyzer_1  |
log_analyzer_1  | OK
hw01loganalyzer_log_analyzer_1 exited with code 0
```

Линтером выступает flake8 `flake8 --max-line-length=119 log_analyzer.py`, с размером строки в 119 символов против 
стандартных 79.

### Производительность
Замер скорости и потребления памяти, на gz и текстовых файлах скорость сопоставима. 16-18 секунд, 170 Мб памяти на 
тестовом логе:
```bash
root at (Docker Container) #518f7d62fb1b in /code
$ \time -v python3 log_analyzer.py -c conf.yaml
Working with file './log/nginx-access-ui.log-20170630'
Отчет был записан в ./reports/report-2017.06.30.html
	Command being timed: "python3 log_analyzer.py -c conf.yaml"
	User time (seconds): 14.20
	System time (seconds): 1.21
	Percent of CPU this job got: 95%
	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:16.19
	Average shared text size (kbytes): 0
	Average unshared data size (kbytes): 0
	Average stack size (kbytes): 0
	Average total size (kbytes): 0
	Maximum resident set size (kbytes): 171264
	Average resident set size (kbytes): 0
	Major (requiring I/O) page faults: 0
	Minor (reclaiming a frame) page faults: 47625
	Voluntary context switches: 216
	Involuntary context switches: 15410
	Swaps: 0
	File system inputs: 1125456
	File system outputs: 0
	Socket messages sent: 0
	Socket messages received: 0
	Signals delivered: 0
	Page size (bytes): 4096
	Exit status: 0
	
root at (Docker Container) #518f7d62fb1b in /code
$ \time -v python3 log_analyzer.py -c conf.yaml
Working with file './log/nginx-access-ui.log-20170629.gz'
Отчет был записан в ./reports/report-2017.06.29.html
	Command being timed: "python3 log_analyzer.py -c conf.yaml"
	User time (seconds): 17.66
	System time (seconds): 0.42
	Percent of CPU this job got: 99%
	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:18.22
	Average shared text size (kbytes): 0
	Average unshared data size (kbytes): 0
	Average stack size (kbytes): 0
	Average total size (kbytes): 0
	Maximum resident set size (kbytes): 171044
	Average resident set size (kbytes): 0
	Major (requiring I/O) page faults: 0
	Minor (reclaiming a frame) page faults: 52036
	Voluntary context switches: 146
	Involuntary context switches: 2298
	Swaps: 0
	File system inputs: 104152
	File system outputs: 0
	Socket messages sent: 0
	Socket messages received: 0
	Signals delivered: 0
	Page size (bytes): 4096
	Exit status: 0
```
