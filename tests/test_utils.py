import pytest
import utils


class TestUtils:
    def test_process_lines_full_url(self):
        new_list = utils.process_lines("", 'hi!', True)

        assert len(new_list) == 0
