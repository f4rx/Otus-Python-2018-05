import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import log_analyzer
from mock import patch
import glob
import os
from collections import namedtuple


class LogAnalyzerTest(unittest.TestCase):

    def test_get_date_from_filename(self):
        self.assertEqual(tuple(log_analyzer.get_date_from_filename("nginx-access-ui.log-20170629.gz")), tuple(["2017",
                                                                                                          "06", "29"]))
        self.assertEqual(tuple(log_analyzer.get_date_from_filename("nginx-access-ui.log-20170629")), tuple(["2017",
                                                                                                          "06", "29"]))
        with self.assertRaises(ValueError):
            log_analyzer.get_date_from_filename("nginx-access-ui.log-2017-06-29.gz")
        with self.assertRaises(ValueError):
            log_analyzer.get_date_from_filename("nginx-access-ui.log-2017.06.29.gz")
        with self.assertRaises(ValueError):
            log_analyzer.get_date_from_filename("nginx-access-ui.log-2017-06-29")
        with self.assertRaises(ValueError):
            log_analyzer.get_date_from_filename("nginx-access-ui.log-2017.06.29")
        with self.assertRaises(ValueError):
            log_analyzer.get_date_from_filename("")

    def test_return_read_log_file(self):
        """
        Тут пробовал реализовать тестирование используя моки и патчинг. Делал в первый раз, в каком-то роде просто
        копипаста, поэтому неоптимально. Но оставтлю себе на память.
        """
        with patch('os.path.isdir') as dir_mock:
            dir_mock.return_value = True
            with patch('glob.glob') as glob_mock:
                glob_mock.return_value = ["nginx-access-ui.log-20170629.gz", "nginx-access-ui.log-20170630"]
                self.assertEqual(log_analyzer.detect_last_log_file("fake_dir1", "fake_dir2").filename,
                                 "fake_dir1/nginx-access-ui.log-20170630")

                self.assertEqual(log_analyzer.detect_last_log_file("fake_dir1", "fake_dir2").date,
                                 ("2017", "06", "30"))

                glob_mock.return_value = ["nginx-access-ui.log-20170629.gz", "nginx-access-ui.log-20170630",
                                      "nginx-access-ui.log-20170631.gz"]
                self.assertEqual(log_analyzer.detect_last_log_file("fake_dir1", "fake_dir2").filename,
                                 "fake_dir1/nginx-access-ui.log-20170631.gz")
                glob_mock.return_value = []
                self.assertEqual(log_analyzer.detect_last_log_file("fake_dir1", "fake_dir2"), None)
                # with self.assertRaises(log_analyzer.DoneException):
                #     log_analyzer.detect_last_log_file("fake_dir1", "fake_dir2")

    def test_merge_config(self):
        """
        Тут уже исхожу из blackbox тестирования, в Докере создаю тестовое окружение с фейковыми данными и уже после
        этого запускаю тест на реальных файлах(Реальной ФС), а не замоканных значениях. Такой подход мне показался
        более приемлемым и гибким.
        """
        self.assertEqual(log_analyzer.merge_config({1: 1, 2: 2}, "conf/conf1.yaml"), {1: 1, 2: "two", 3: 3})

        self.assertEqual(log_analyzer.merge_config({}, "conf/conf1.yaml"), {2: "two", 3: 3})

        with self.assertRaises(TypeError):
            log_analyzer.merge_config({1: 1, 2: 2}, "conf/conf2.yaml")

        self.assertEqual(log_analyzer.merge_config({1: 1, 2: 2}, "conf/conf3.yaml"), {1: 1, 2: 2, 4: 4})

    def test_get_statistic_from_log_file(self):
        LogFile = namedtuple('LogFile', ['filename', 'date'])
        log_file1 = LogFile(filename="log2/1.log", date="")
        log_file2 = LogFile(filename="log2/2.log", date="")
        self.assertEqual(log_analyzer.get_statistic_from_log_file(log_file1, 1, 1.0), {'/api/v2/banner/25019354':
                                          {'count': 2, 'count_perc': 40.0, 'time_avg': 5.768, 'time_max': 6.146,
                                           'time_med': 5.768, 'time_perc': 91.759, 'time_sum': 11.536}})

        self.assertEqual(log_analyzer.get_statistic_from_log_file(log_file2, 1, 1.0), {})


if __name__ == '__main__':
    unittest.main(verbosity=3)
