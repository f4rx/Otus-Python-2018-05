#!/usr/bin/env python

import os
import glob
import re
import gzip
import statistics
import argparse
import yaml
import logging
import logging.handlers
from string import Template
import sys
from collections import namedtuple


DEFAULT_CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOG_FILE": None,
    "PARSE_ERROR_PERC": 1.0,
}


def get_last_log(log_dir):
    if not os.path.isdir(log_dir):
        logging.info("Log dir '%s' not found" % log_dir)
        return

    log_files = glob.glob(os.path.join(log_dir, "nginx-access-ui.log-*"))
    log_files.sort(reverse=True)
    try:
        log_date = get_date_from_filename(os.path.basename(log_files[0]))
    except (ValueError, IndexError):
        logging.info("Error during detect log_file. Please check files in log dir %r" % log_dir)
        return

    LogFile = namedtuple('LogFile', ['filename', 'date'])
    logging.info("Working with file %r" % log_files[0])
    return LogFile(filename=log_files[0], date=log_date)


def check_report_for_log_file(log_file, report_dir):
    return os.path.isfile(os.path.join(report_dir, "report-%s.%s.%s.html" % log_file.date))


def get_date_from_filename(filename):
    mo = re.search(r'nginx-access-ui\.log-(\d{4})(\d{2})(\d{2})(\.gz)?$', filename)
    if not mo:
        raise ValueError()
    log_year = mo.group(1)
    log_month = mo.group(2)
    log_day = mo.group(3)
    return log_year, log_month, log_day


# log_format ui_short
# '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
# '$status $body_bytes_sent "$http_referer" '
# '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID"
# "$http_X_RB_USER" '
# '$request_time';
# 1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1"
# 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759"
# "dc7161be3"
# 0.390
def get_statistic_from_log_file(log_file, report_size, parse_error_perc):

    urls_rate = {}
    parse_error_count = 0   # Количество ошибок при парсинге
    request_count = 0       # Общее количество запросов
    request_time_count = 0  # Общее время на все запросы
    for line in return_read_log_file(log_file.filename):
        mo = re.search(r'\] \"\w* (.*?) HTTP.* (.*?)$', line)
        if not mo or len(mo.groups()) != 2:
            parse_error_count += 1
            logging.debug("Bad Log line %r" % line)
            continue
        url = mo.group(1)
        request_time = float(mo.group(2))
        if url not in urls_rate:
            urls_rate[url] = []
        urls_rate[url].append(float(request_time))
        request_time_count += request_time
        request_count += 1

    if request_count > 0:
        parse_error_ratio = parse_error_count / request_count
        if parse_error_ratio > (parse_error_perc / 100.0):
            logging.info("There ara many errors during parcing log file. Error perc %f" % parse_error_ratio)
            return

    return count_statistic(urls_rate, request_count, request_time_count, report_size)


def count_statistic(urls_rate, request_count, request_time, report_size):
    urls_statistic = {}
    for key, value in urls_rate.items():
        total_request_time = sum(value)
        if total_request_time < report_size:
            continue
        urls_statistic[key] = {}
        urls_statistic[key]['count'] = len(value)
        urls_statistic[key]['count_perc'] = round(urls_statistic[key]['count'] / request_count * 100, 3)
        urls_statistic[key]['time_sum'] = round(total_request_time, 3)
        urls_statistic[key]['time_perc'] = round(urls_statistic[key]['time_sum'] / request_time * 100, 3)
        urls_statistic[key]['time_max'] = max(value)
        urls_statistic[key]['time_avg'] = round(statistics.mean(value), 3)
        urls_statistic[key]['time_med'] = round(statistics.median(value), 3)

    return urls_statistic


def return_read_log_file(filename):
    if re.match(".*\.gz$", filename):
        with gzip.open(filename, 'rb') as log_file:
            for line in log_file:
                yield line.decode()
    else:
        with open(filename) as log_file:
            for line in log_file:
                yield line


def write_report(urls_statistic, log_file, report_dir):
    report_filename = "report-%s.%s.%s.html" % log_file.date
    report_path = os.path.join(report_dir, report_filename)
    with open(report_path, 'w') as report_file:
        with open("resources/report.html.template", 'r') as template_file:
            template_file_raw = template_file.read()
            report_template = Template(template_file_raw)
            table_json = {"table_json": get_result_for_write(urls_statistic)}
            report_file.write(report_template.safe_substitute(table_json))
    logging.info("Отчет был записан в %s" % report_path)


def get_result_for_write(urls_statistic):
    result = []
    for url, value in urls_statistic.items():
        value['url'] = url
        result.append(value)

    return result


def get_args():
    parser = argparse.ArgumentParser(description='Parse log files.')
    parser.add_argument('-c', '--config', help='path to conf.yaml', default='conf.yaml')
    return parser.parse_args()


def merge_config(default_config, file_config):

    with open(file_config, 'r') as stream:
        user_config = {}
        try:
            user_config = yaml.load(stream)
        except yaml.YAMLError:
            return
    default_config.update(user_config)
    return default_config


def config_logger(filename):
    log_format = '[%(asctime)s] %(levelname).1s: %(message)s'
    log_date_format = "%Y-%m-%d %H:%M:%S"
    log_level = logging.INFO

    # По-умолчанию записываем в файл согласно ТЗ
    logging.basicConfig(filename=filename,
                        filemode='a',
                        level=log_level,
                        format=log_format,
                        datefmt=log_date_format)

    # Хочу дополнительно подключить stdout
    # По-умолчанию он шлет в stderr
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.set_name('log_analyzer')
    formatter = logging.Formatter(fmt='%(asctime)s %(filename)-6s: %(levelname)-5s %(message)s', datefmt='%H:%M:%S')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def run(config):
    args = get_args()
    if not os.path.isfile(args.config):
        logging.info("Config file '%s' not found" % args.config)
        return
    config = merge_config(config, args.config)

    if not config:
        logging.info("Errors during reading '%s'. Please check yaml file" % args.config)
        return

    config_logger(config['LOG_FILE'])

    if not os.path.isdir(config['REPORT_DIR']):
        os.mkdir(config['REPORT_DIR'])

    log_file = get_last_log(config['LOG_DIR'])
    if not log_file:
        return

    if check_report_for_log_file(log_file=log_file, report_dir=config['REPORT_DIR']):
        logging.info("The report for file %r is already exists. Exit" % log_file.filename)
        return

    urls_statistic = get_statistic_from_log_file(log_file, config['REPORT_SIZE'],
                                                 config['PARSE_ERROR_PERC'])
    if urls_statistic is None:
        return
    write_report(urls_statistic, log_file, config['REPORT_DIR'])


def main(config):
    # noinspection PyBroadException
    # https://stackoverflow.com/questions/40775709/avoiding-too-broad-exception-clause-warning-in-pycharm/40776385?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    # https://docs.python.org/2/howto/doanddont.html#exceptions
    try:
        run(config)
    except KeyboardInterrupt:
        logging.error("The script is interrupted and data report can be corrupted")
        sys.exit(2)
    except Exception:
        logging.exception("Critical error during execution the script, see logs")
        sys.exit(3)


if __name__ == "__main__":
    main(DEFAULT_CONFIG)
