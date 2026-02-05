import pytest
import re

from unittest import TestCase
from unittest.mock import call, patch
from neucbot.alpha import AlphaList, ChainAlphaList
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
                [6.08988, 27.12],
                [6.05078, 69.91],
                [5.768, 1.7],
                [5.626, 0.157],
                [5.607, 1.13],
                [5.481, 0.013],
                [5.345, 0.001],
                [5.302, 0.00011],
            ],
        )

    def test_from_filepath(self):
        alpha_list = AlphaList.from_filepath("AlphaLists/Bi212Alphas.dat")
        alpha_list.load_or_fetch()

        self.assertEqual(
            alpha_list.alphas,
            [
                [6.08988, 27.12],
                [6.05078, 69.91],
                [5.768, 1.7],
                [5.626, 0.157],
                [5.607, 1.13],
                [5.481, 0.013],
                [5.345, 0.001],
                [5.302, 0.00011],
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
                [6.08988, 27.12],
                [6.05078, 69.91],
                [5.768, 1.7],
                [5.626, 0.157],
                [5.607, 1.13],
                [5.481, 0.013],
                [5.345, 0.001],
                [5.302, 0.00011],
            ],
        )

    def test_scale_by(self):
        alpha_list = AlphaList.from_filepath("AlphaLists/Bi212Alphas.dat")
        alpha_list.load_or_fetch()
        alpha_list.scale_by(0.5)

        # Expect alpha intensities to be 50% of regular values
        self.assertEqual(
            alpha_list.alphas,
            [
                [6.08988, 13.56],
                [6.05078, 34.955],
                [5.768, 0.85],
                [5.626, 0.0785],
                [5.607, 0.565],
                [5.481, 0.0065],
                [5.345, 0.0005],
                [5.302, 0.000055],
            ],
        )

    @patch.object(AlphaList, "write")
    @patch("os.path.isfile")
    def test_load_or_fetch_raises_on_failed_write(self, mocked_isfile, mocked_write):
        mocked_isfile.return_value = False
        mocked_write.return_value = ""

        with self.assertRaisesRegex(RuntimeError, r"Unable to write alpha file"):
            AlphaList("Bi", 212).load_or_fetch()


class TestChainAlphaList(TestCase):
    def test_from_filepath(self):
        chain_list = ChainAlphaList.from_filepath("Chains/Th232Chain.dat")

        assert chain_list.element == "Th"
        assert chain_list.isotope == "232"

    def test_from_filepath_error_invalid_filepath(self):
        with self.assertRaisesRegex(
            RuntimeError, r"Invalid file path for chain alpha list"
        ):
            ChainAlphaList.from_filepath("Chains/Th232Alphas.dat")

    def test_load_or_fetch(self):
        chain_list = ChainAlphaList.from_filepath("Chains/Th232Chain.dat")
        chain_list.load_or_fetch()

        assert len(chain_list._alpha_lists) == 7
        self.assertEqual(
            chain_list.alphas,
            [
                # Th232 Alphas
                [4.0123, 78.2],
                [3.9471999999999996, 21.7],
                [3.8110999999999997, 0.069],
                # Th228 Alphas
                [5.42315, 73.4],
                [5.3403599999999996, 26.0],
                [5.211, 0.408],
                [5.173, 0.218],
                [5.138, 0.036],
                [4.99, 1e-05],
                [4.944, 2.4e-05],
                [4.507, 1.7e-05],
                [4.43, 4.6e-06],
                # Ra224 Alphas
                [5.68537, 94.92],
                [5.448600000000001, 5.06],
                [5.161, 0.0071],
                [5.051, 0.0076],
                [5.034, 0.003],
                # Rn220 Alphas
                [6.28808, 99.886],
                [5.747, 0.114],
                # Po216 Alphas
                [6.7783, 99.9981],
                [5.985, 0.0019],
                # Bi212 Alphas (multiplied by branching fraction .3594)
                [6.08988, 9.746928],
                [6.05078, 25.125653999999997],
                [5.768, 0.61098],
                [5.626, 0.0564258],
                [5.607, 0.406122],
                [5.481, 0.0046722],
                [5.345, 0.0003594],
                [5.302, 3.9534e-05],
                # Po212 Alphas (multiplied by branching fraction .6406
                [8.78486, 64.06],
            ],
        )
