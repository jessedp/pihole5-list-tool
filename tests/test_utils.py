import utils


class TestUtils:
    def test_valid_url(self):
        assert utils.valid_url("") is False
        assert utils.valid_url("pihole") is False
        assert utils.valid_url("pihole.net") is False
        assert utils.valid_url("http://pihole.net") is True
        assert utils.valid_url("http://pihole.net/v5") is True
        assert utils.valid_url("http://pihole.net/v5?install=trye") is True

    def test_validate_host(self):
        test1 = "nope"
        test2 = "nope.c"
        test3 = "nope.com"
        assert utils.validate_host(test1) is False
        assert utils.validate_host(test2) is False
        assert utils.validate_host(test3) is True

    # TODO: enforce pi-url regex
    def test_validate_regex(self):
        assert utils.validate_regex("github") is True

    def test_process_lines_empty(self):
        new_list = utils.process_lines("", "", True)
        assert len(new_list) == 0

    def test_process_lines_full_url(self):
        comment = "MyComment"
        new_list = utils.process_lines(
            """
http://google.com
invalid
http://github.com
""",
            comment,
            True,
        )
        assert len(new_list) == 2

        assert new_list[1]["url"] == "http://github.com"
        assert new_list[1]["comment"] == comment

    # TODO: Breakout host/url/regexes
    def test_process_lines_any(self):
        comment = "MyComment"
        new_list = utils.process_lines(
            """
github
github.com
http://github.com
http://github.com/test
http://github.com/test?f08s
""",
            comment,
            True,
        )
        assert len(new_list) == 3

        # assert new_list[1]["url"] == "http://github.com"
        assert new_list[1]["comment"] == comment
