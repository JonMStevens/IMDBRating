"""unit tests for imdbrating.py"""
import argparse
import unittest
from io import TextIOWrapper

from imdbrating import IMDBInfoGrabber, parse_args


class Test_IMDBInfoGrabber(unittest.TestCase):
    """tests IMDBInfoGrabber.get_imdb_info_for_show"""
    def test_happy(self):
        """happy path test
        imdb code for Home Movies"""
        self.assertIsInstance(IMDBInfoGrabber.get_imdb_info_for_show("tt0197159"), str)
        self.assertNotEqual(IMDBInfoGrabber.get_imdb_info_for_show("tt0197159"), "")
        # add more to check if output is what's expected
    def test_movie(self):
        """test imdb code of movie
        imdb code for Sleeping Beauty"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt0053285")
    def test_episode(self):
        """test imdb code of episode
        imdb code for futurama: luck of the fryish"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt0768678")
    def test_nothing_code(self):
        """test valid imdb code that points to nothing"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt0000000")
    def test_bad_code(self):
        """test invalid imdb code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt12")
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt1212121212121212")
    def test_non_code_string(self):
        """test a string that is not a code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("t")
    def test_non_code_empty_string(self):
        """test empty string that is not a code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("")
    def test_non_code_string_class(self):
        """test passing string class"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show(str)
    def test_non_code_int(self):
        """test an int that is not a code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show(0)
    def test_non_code_float(self):
        """test a float that is not a code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show(1.2)
class Test_ParseArgs(unittest.TestCase):
    """tests parse_args"""
    @staticmethod
    def has_all_attr(args: argparse.Namespace) -> bool:
        """helper function to test that all args exist in namespace"""
        return hasattr(args, "url") and hasattr(args, "code") and hasattr (args, "csv_file")
    def test_happy_with_code(self):
        """happy path test with code as arg
        imdb code for Home Movies"""
        argv = ["-code", "tt0197159", "homemovies.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(Test_ParseArgs.has_all_attr(args))
        self.assertIsNone(args.url)
        self.assertEqual(args.code, ["tt0197159"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()

    def test_happy_with_url_episode_list(self):
        """happy path test with url as arg
        url goes to episode list
        code is for star trek deep space 9"""
        argv = ["-url", "https://www.imdb.com/title/tt0106145/episodes?season=1", "ds9.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(Test_ParseArgs.has_all_attr(args))
        self.assertIsNone(args.code)
        self.assertEqual(args.url, ["tt0106145"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()
    def test_happy_with_url(self):
        """happy path test with url as arg
        code is for star trek deep space 9"""
        argv = ["-url", "https://www.imdb.com/title/tt0106145/", "ds9.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(Test_ParseArgs.has_all_attr(args))
        self.assertIsNone(args.code)
        self.assertEqual(args.url, ["tt0106145"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()
    def test_happy_with_url_no_trailing_slash(self):
        """happy path test with url as arg
        url has no traling /
        code is for star trek deep space 9"""
        argv = ["-url", "https://www.imdb.com/title/tt0106145", "ds9.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(Test_ParseArgs.has_all_attr(args))
        self.assertIsNone(args.code)
        self.assertEqual(args.url, ["tt0106145"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()
    def test_happy_with_url_with_ref(self):
        """happy path test with url as arg with a ?ref in url
        code is for fridays"""
        argv = ["-url", "https://www.imdb.com/title/tt0080219/?ref_=nm_flmg_wr_14", "fridays.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(Test_ParseArgs.has_all_attr(args))
        self.assertIsNone(args.code)
        self.assertEqual(args.url, ["tt0080219"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()
    def test_double_dashes(self):
        """test with double dashes in front of arg flag, should reject"""
        argv = ["--code", "tt0197159", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_csv_arg_flag(self):
        """test with arg flag for csv arg, should reject"""
        argv = ["-code", "tt0197159", "-csv", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_non_imdb_url(self):
        """test url that is not an imdb site, should reject"""
        argv = ["-url",
        ("https://stackoverflow.com/questions/827557/"
        "how-do-you-validate-a-url-with-a-regular-expression-in-python"),
        "ds9.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_non_url(self):
        """test url that goes nowhere, should reject"""
        argv = ["-url", "https://alfjalafafghagla.zzz/", "ds9.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_only_csv(self):
        """test argv only has csv argument, missing code or url"""
        argv = ["homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_only_code(self):
        """test argv only has csv argument, missing code or url"""
        argv = ["tt0197159"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_only_flag(self):
        """test argv only has csv argument, missing code or url"""
        argv = ["-code"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_missing_arg_flag(self):
        """test argv is missing -url or -code flag"""
        argv = ["tt0197159", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_empty_code(self):
        """test empty string as code arg"""
        argv = ["-code", "", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_empty_csv(self):
        """test empty string as csv arg"""
        argv = ["-code", "tt0197159", ""]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_nameless_csv(self):
        """test .csv csv arg"""
        argv = ["-code", "tt0197159", ".csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_short_code(self):
        """test invalid imdb code that is too short"""
        argv = ["-code", "tt12", ".csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_long_code(self):
        """test invalid imdb code that is too long"""
        argv = ["-code", "tt122112112211212", ".csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_non_code(self):
        """test a string that is not a code"""
        argv = ["-code", "t", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

if __name__ == "__main__":
    unittest.main()
