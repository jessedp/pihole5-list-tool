import utils


class TestUtils:
    def test_valid_url(self):
        assert utils.valid_url("pihole") is False
        assert utils.valid_url("pihole.net") is False
        assert utils.valid_url("http://pihole.net") == True
        assert utils.valid_url("http://pihole.net/v5") == True
        assert utils.valid_url("http://pihole.net/v5?install=trye") == True

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

    def test_process_lines_no_scheme(self):
        comment = "MyComment"
        new_list = utils.process_lines(
            """
http://github.com
github.com
github
""",
            comment,
            False,
        )
        assert len(new_list) == 3

        assert new_list[2]["url"] == "github"
        assert new_list[2]["comment"] == comment
