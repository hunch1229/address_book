# 여러 테스트가 같이 쓰는 준비 코드(fixture)를 모아 둔 파일
# pytest 가 자동으로 읽으므로 테스트 파일에서 import 하지 않아도 된다.

import pytest

import db
from app import create_app


@pytest.fixture
def app(tmp_path):
    """테스트 하나마다 새 임시 DB를 쓰는 Flask 앱을 만든다.

    tmp_path: pytest 가 테스트마다 만들어 주는 빈 임시 폴더.
    테스트가 끝나면 pytest 가 알아서 정리한다.
    → 실제 instance/addressbook.db 는 전혀 건드리지 않는다.
    """
    test_db = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE": str(test_db)})

    # 혹시라도 실제 DB를 가리키고 있으면 테스트를 바로 멈춘다. (안전장치)
    assert not app.config["DATABASE"].endswith("instance/addressbook.db")

    # 임시 DB에 contacts 테이블을 만든다.
    with app.app_context():
        db.init_db()

    yield app


@pytest.fixture
def client(app):
    """브라우저 대신 요청을 보내는 Flask 테스트 클라이언트."""
    return app.test_client()


@pytest.fixture
def add(client):
    """연락처를 등록하는 도우미 함수를 돌려준다.

    사용 예) add("홍길동", "010-1234-5678")
    이메일·주소·메모는 필요할 때만 키워드로 넘긴다.
    """

    def _add(name, phone, **extra):
        data = {"name": name, "phone": phone, **extra}
        return client.post("/add", data=data)

    return _add


@pytest.fixture
def all_contacts(app):
    """DB에 실제로 저장된 연락처 목록을 딕셔너리 리스트로 돌려주는 함수.

    화면(HTML)만 보지 않고 DB까지 확인해야 '정말 저장/수정/삭제됐는지' 알 수 있다.
    """

    def _all():
        with app.app_context():
            return [dict(row) for row in db.list_contacts()]

    return _all
