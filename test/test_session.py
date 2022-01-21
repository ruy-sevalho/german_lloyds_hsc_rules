import pytest as pt
from dataclass_tools.tools import serialize_dataclass
from gl_hsc_scantling.session import Session


def test_session_serialization(session_example):
    orignal_session_dict = serialize_dataclass(session_example)
    new_session = Session()
    new_session.load_session(orignal_session_dict)
    new_session_dict = serialize_dataclass(new_session)
    assert session_example == new_session
