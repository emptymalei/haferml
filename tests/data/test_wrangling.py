from nose import tools as _tools
from haferml.data.wrangle.misc import convert_str_repr_to_list


def test_convert_to_list():

    _tools.eq_(convert_str_repr_to_list("[1,2,3]"), [1, 2, 3])
