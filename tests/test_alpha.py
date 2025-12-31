import pytest
import re

from unittest import TestCase
from unittest.mock import call, patch
from neucbot.alpha import AlphaList
from neucbot.ensdf import Client, Parser


class TestAlphaList(TestCase):
    @patch.object(Parser, "parse")
    @patch.object(Client, "read_or_fetch_decay_file")
    @patch("os.path.exists")
    def test_write_success(
        self, mocked_os_path_exists, mocked_read_or_fetch, mocked_parse
    ):
        # Assume no decay or alpha files exist
        mocked_os_path_exists.return_value = False

        mocked_read_or_fetch.return_value = ""

        expected_alphas = {
            6089.88: 27.12,
            6050.78: 69.91,
            5768: 1.70,
            5626: 0.157,
            5607: 1.13,
            5481: 0.013,
            5345: 0.0010,
            5302: 0.00011,
        }

        expected_gammas = {
            39.857: 2.96,
            288.2: 0.938,
            328.03: 0.349,
            433.7: 0.047,
            452.98: 1.01,
            473.0: 0.14,
        }

        mocked_parse.return_value = {
            "alphas": expected_alphas,
            "gammas": expected_gammas,
            "intensity": 1.0,
        }

        alphas = AlphaList("Bi", 212)
        alphas.write()

        mocked_os_path_exists.assert_has_calls([call("./AlphaLists/Bi212Alphas.dat")])
        mocked_read_or_fetch.assert_called()
        mocked_parse.assert_called()

    @patch.object(Parser, "parse")
    @patch.object(Client, "read_or_fetch_decay_file")
    @patch("os.path.exists")
    def test_write_does_not_fetch_if_alpha_file_exists(
        self, mocked_os_path_exists, mocked_read_or_fetch, mocked_parse
    ):
        # Assume no decay or alpha files exist
        mocked_os_path_exists.return_value = True

        alphas = AlphaList("Bi", 212)
        alphas.write()

        mocked_os_path_exists.assert_has_calls([call("./AlphaLists/Bi212Alphas.dat")])
        mocked_read_or_fetch.assert_not_called()
        mocked_parse.assert_not_called()

    def test_load(self):
        alphas = AlphaList("Bi", 212).load()

        self.assertEqual(
            alphas,
            [
                ["6.08988", "27.12"],
                ["6.05078", "69.91"],
                ["5.768", "1.7"],
                ["5.626", "0.157"],
                ["5.607", "1.13"],
                ["5.481", "0.013"],
                ["5.345", "0.001"],
                ["5.302", "0.00011"],
            ],
        )

    def test_from_filepath(self):
        alphas = AlphaList.from_filepath("AlphaLists/Bi212Alphas.dat")

        self.assertEqual(
            alphas,
            [
                ["6.08988", "27.12"],
                ["6.05078", "69.91"],
                ["5.768", "1.7"],
                ["5.626", "0.157"],
                ["5.607", "1.13"],
                ["5.481", "0.013"],
                ["5.345", "0.001"],
                ["5.302", "0.00011"],
            ],
        )

    @patch.object(AlphaList, "write")
    @patch("os.path.isfile")
    def test_load_or_fetch_success(self, mocked_isfile, mocked_write):
        mocked_isfile.side_effect = [False, True]

        mocked_write.return_value = ""

        alphas = AlphaList("Bi", 212).load_or_fetch()

        self.assertEqual(mocked_isfile.call_count, 2)
        self.assertEqual(mocked_write.call_count, 1)
        self.assertEqual(
            alphas,
            [
                ["6.08988", "27.12"],
                ["6.05078", "69.91"],
                ["5.768", "1.7"],
                ["5.626", "0.157"],
                ["5.607", "1.13"],
                ["5.481", "0.013"],
                ["5.345", "0.001"],
                ["5.302", "0.00011"],
            ],
        )

    @patch.object(AlphaList, "write")
    @patch("os.path.isfile")
    def test_load_or_fetch_raises_on_failed_write(self, mocked_isfile, mocked_write):
        mocked_isfile.return_value = False
        mocked_write.return_value = ""

        with self.assertRaisesRegex(RuntimeError, r"Unable to write alpha file"):
            AlphaList("Bi", 212).load_or_fetch()
