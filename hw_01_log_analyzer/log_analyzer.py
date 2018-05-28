#!/usr/bin/env python

import os
import glob
import re
import gzip
import traceback
import statistics
import argparse
import yaml
import logging
import logging.handlers


global_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOG_FILE": None,
    "PARSE_ERROR_PERC": 1.0,
}


class DoneException(Exception):
    pass


class ParseException(Exception):
    pass


def detect_last_log_file(log_dir, report_dir):
    if not os.path.isdir(log_dir):
        raise NotADirectoryError("Log dir '%s' not found" % log_dir)

    if not os.path.isdir(report_dir):
        os.mkdir(report_dir)

    log_files = glob.glob(os.path.join(log_dir, "nginx-access-ui.log-*"))

    for log_file in log_files:
        if not check_log_filename(os.path.basename(log_file)):
            log_files.remove(log_file)

    if not log_files:
        raise FileNotFoundError("Dir %s is empty or not contains log files with valid names" % log_dir)

    # формат даты YYYYMMDD позволяет просто сортировать в лексикографическом порядке
    log_files.sort(reverse=True)

    log_file_to_work = None
    for log_file in log_files:
        try:
            log_date = get_date_from_filename(log_file)
        except ValueError:
            continue

        #  Добавить поддержку md5 report, когда файл уже записался, чтобы знать, что запись файла не прирвалась
        if not os.path.isfile(os.path.join(report_dir, "report-%s.%s.%s.html" % log_date)):
            log_file_to_work = log_file
            break

    if not log_file_to_work:
        raise DoneException("All logs files were parsered")

    print_and_log_info("Working with file %r" % log_file_to_work)
    return log_file_to_work


def get_date_from_filename(filename):
    mo = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
    if not mo or len(mo.groups()) != 3:
        raise ValueError()
    log_year = mo.group(1)
    log_month = mo.group(2)
    log_day = mo.group(3)
    return log_year, log_month, log_day


def check_log_filename(filename):
    return bool(re.match("^nginx-access-ui\.log-\d{8}(\.gz)?$", filename))


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
def parse_log_file(filename, report_size, parse_error_perc):

    urls_rate = {}
    parse_error_count = 0   # Количество ошибок при парсинге
    request_count = 0       # Общее количество запросов
    request_time_count = 0  # Общее время на все запросы
    read_log_file = return_read_log_file(filename)
    for line in read_log_file(filename):
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

    if request_count > 0 and parse_error_count / request_count > (parse_error_perc / 100.0):
        raise ParseException("There ara many errors during parcing log file. Error perc %f" % (parse_error_count /
                                                                                               request_count))

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
        return read_log_file_gz
    else:
        return read_log_file_plain


def read_log_file_plain(filename):
    with open(filename) as log_file:
        for cnt, line in enumerate(log_file):
            yield line


def read_log_file_gz(filename):
    with gzip.open(filename, 'rb') as log_file:
        for cnt, line in enumerate(log_file):
            yield line.decode()


def write_report(urls_statistic, log_filename, report_dir):
    report_date = get_date_from_filename(log_filename)
    report_filename = "report-%s.%s.%s.html" % report_date
    report_path = os.path.join(report_dir, report_filename)
    with open(os.path.join(report_path), 'w') as report_file:
        with open("resources/report.html.template") as template_file:
            for cnt, line in enumerate(template_file):
                if line == "    var table = $table_json;\n":
                    report_file.write("    var table = %s;\n" % get_result_for_write(urls_statistic))
                else:
                    report_file.write(line)
    print_and_log_info("Отчет был записан в %s" % report_path)


def get_result_for_write(urls_statistic):
    result = []
    for url, value in urls_statistic.items():
        value['url'] = url
        result.append(value)

    return result


def get_config_path():
    parser = argparse.ArgumentParser(description='Parse log files.')
    parser.add_argument('-c', '--config', help='path to conf.yaml', required=True)
    args = parser.parse_args()
    return args.config


def merge_config(default_config, file_config):
    if not os.path.isfile(file_config):
        raise FileNotFoundError("Config file '%s' not found" % file_config)

    with open(file_config, 'r') as stream:
        user_config = {}
        try:
            user_config = yaml.load(stream)
        except yaml.YAMLError as exc:
            raise yaml.YAMLError("Errors during reading '%s'. Please check yaml file" % file_config)
    return {**default_config, **user_config}


def config_logger(filename):
    log_format = '[%(asctime)s] %(levelname).1s: %(message)s'
    log_date_format = "%Y-%m-%d %H:%M:%S"
    log_level = logging.INFO
    logging.basicConfig(filename=filename, level=log_level, format=log_format, datefmt=log_date_format)

    # Example for Syslog
    # syslog_address = '/dev/log'
    # if platform.system() == 'Darwin':
    #     syslog_address = '/var/run/syslog'
    # logging.basicConfig(handlers=[logging.handlers.SysLogHandler(address=syslog_address)], level=log_level,
    #                     format=log_format, datefmt=log_date_format)


def print_and_log_info(str):
    print(str)
    logging.info(str)


def print_and_log_error(str):
    print(str)
    logging.error(str)


def run(config):
    config = merge_config(config, get_config_path())
    config_logger(config['LOG_FILE'])
    logging.info("CONFIG: %r" % config)
    log_file = detect_last_log_file(config['LOG_DIR'], config['REPORT_DIR'])
    urls_statistic = parse_log_file(log_file, config['REPORT_SIZE'], config['PARSE_ERROR_PERC'])
    write_report(urls_statistic, log_file, config['REPORT_DIR'])


def main(config):
    # noinspection PyBroadException
    # https://stackoverflow.com/questions/40775709/avoiding-too-broad-exception-clause-warning-in-pycharm/40776385?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    # https://docs.python.org/2/howto/doanddont.html#exceptions
    try:
        run(config)
    except DoneException as e:
        print_and_log_info(e)
    except SystemExit:
        pass
    except (FileNotFoundError, NotADirectoryError, yaml.YAMLError, ParseException) as e:
        print(e)
        logging.error(e)
        exit(1)
    except KeyboardInterrupt:
        logging.exception("The script was interrupted")
        print("The script is interrupted and data report can be corrupted")
        exit(2)
    except BaseException:
        print("Critical error during execution the script, see logs")
        logging.exception(traceback)
        exit(3)


if __name__ == "__main__":
    main(global_config)
