
from dler.tasker.video_tasker import HeaderModel


def test_header():

    h = HeaderModel()
    assert not h.content_length
