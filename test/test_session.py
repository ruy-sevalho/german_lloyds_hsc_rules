import pytest as pt
from dataclass_tools.tools import serialize_dataclass
from gl_hsc_scantling.session import Session
from json import loads


def test_session_serialization(session_example: Session):
    orignal_session_json = session_example.dumps_json()
    new_session = Session()
    new_session.loads_json(orignal_session_json)
    assert session_example == new_session
