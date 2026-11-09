# 데이터베이스 관련 코드를 모아 둔 파일
# - DB 연결 열기/닫기
# - 테이블을 만드는 초기화 명령 (flask --app app init-db)
# 파이썬에 기본으로 들어 있는 sqlite3 모듈만 사용한다. (추가 설치 필요 없음)

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """현재 요청에서 사용할 DB 연결을 돌려준다.

    g 는 요청 하나가 처리되는 동안만 살아 있는 저장 공간이다.
    같은 요청 안에서 get_db()를 여러 번 불러도 연결은 한 번만 만든다.
    """
    if "db" not in g:
        # app.py 에서 설정한 DB 파일 경로로 연결한다. 파일이 없으면 새로 만들어진다.
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        # 조회 결과를 row["name"] 처럼 열 이름으로 꺼낼 수 있게 한다.
        # (기본값은 튜플이라 row[1] 처럼 번호로만 꺼낼 수 있다.)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """요청 처리가 끝나면 DB 연결을 닫는다. (Flask가 자동으로 호출)"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """schema.sql 을 실행해서 테이블을 만든다."""
    db = get_db()
    # 프로젝트 폴더의 schema.sql 파일을 읽어서 안에 있는 SQL을 모두 실행한다.
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


# ---------------------------------------------------------------
# 연락처 데이터 함수
# app.py 의 라우트는 SQL을 직접 쓰지 않고 아래 함수들을 호출한다.
# SQL에 값을 넣을 때는 반드시 ? 자리표시자(파라미터 바인딩)를 사용한다.
# ---------------------------------------------------------------


def _escape_like(text):
    """LIKE 검색에서 특별한 뜻을 가진 문자(%, _, \\)를 일반 글자로 바꾼다.

    LIKE 에서 % 는 '아무 글자 여러 개', _ 는 '아무 글자 한 개'라는 뜻이다.
    사용자가 검색창에 % 를 입력하면 모든 연락처가 나오는 문제를 막기 위해
    앞에 \\ 를 붙여 진짜 % 글자로 찾게 한다. (SQL의 ESCAPE '\\' 와 짝을 이룬다)
    """
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_contacts(q=""):
    """연락처 목록을 이름 가나다순으로 돌려준다.

    q(검색어)가 있으면 이름 또는 전화번호에 검색어가 들어간 연락처만 돌려준다.
    전화번호는 하이픈을 빼고 비교하므로 '01012345678', '1234-5678' 모두 찾을 수 있다.
    """
    # 한글은 유니코드 순서가 가나다순이라 ORDER BY name 으로 정렬된다.
    # COLLATE NOCASE: 영어 이름은 대소문자 구분 없이 정렬 (Kim, kim 을 같이 취급)
    # 이름이 같으면 먼저 등록한 연락처(id가 작은 것)가 위로 온다.
    if not q:
        return get_db().execute(
            "SELECT id, name, phone, email, address, memo, created_at"
            " FROM contacts"
            " ORDER BY name COLLATE NOCASE, id"
        ).fetchall()

    # 검색어 앞뒤에 % 를 붙여 '포함' 검색을 만든다. 예) 길동 → %길동%
    # % 는 SQL 문자열이 아니라 ? 에 넘길 '값' 쪽에 붙인다. (파라미터 바인딩 유지)
    name_pattern = "%" + _escape_like(q) + "%"
    # 전화번호용 검색어: 하이픈을 뺀다. 예) 010-1234 → 0101234
    phone_q = q.replace("-", "")
    phone_pattern = "%" + _escape_like(phone_q) + "%"

    # ? 자리에 순서대로 name_pattern, phone_q, phone_pattern 이 들어간다.
    # (? <> '' AND ...): 검색어가 '-' 뿐이라 phone_q 가 빈 문자열이면
    #  전화번호 조건이 '%%'(전부 일치)가 되지 않도록 전화번호 비교를 건너뛴다.
    return get_db().execute(
        "SELECT id, name, phone, email, address, memo, created_at"
        " FROM contacts"
        " WHERE name LIKE ? ESCAPE '\\'"
        "    OR (? <> '' AND REPLACE(phone, '-', '') LIKE ? ESCAPE '\\')"
        " ORDER BY name COLLATE NOCASE, id",
        (name_pattern, phone_q, phone_pattern),
    ).fetchall()


def create_contact(name, phone, email=None, address=None, memo=None):
    """새 연락처를 저장하고, 새로 붙은 id를 돌려준다."""
    db = get_db()
    # 값은 SQL 문자열에 직접 넣지 않고 ? 자리에 순서대로 전달한다.
    # sqlite3 가 값을 안전하게 처리해 주므로 SQL 인젝션을 막을 수 있다.
    cursor = db.execute(
        "INSERT INTO contacts (name, phone, email, address, memo)"
        " VALUES (?, ?, ?, ?, ?)",
        (name, phone, email, address, memo),
    )
    # commit 을 해야 변경 내용이 DB 파일에 실제로 저장된다.
    db.commit()
    return cursor.lastrowid


def get_contact(contact_id):
    """id 로 연락처 하나를 찾아 돌려준다. 없으면 None."""
    return get_db().execute(
        "SELECT id, name, phone, email, address, memo, created_at"
        " FROM contacts"
        " WHERE id = ?",
        (contact_id,),  # 값이 하나여도 튜플로 넘긴다. (쉼표 필수!)
    ).fetchone()


def update_contact(contact_id, name, phone, email=None, address=None, memo=None):
    """연락처 하나를 수정한다. 실제로 바뀐 행 수(0 또는 1)를 돌려준다."""
    db = get_db()
    # WHERE id = ? 가 없으면 모든 연락처가 같은 값으로 덮어써진다. 절대 빼지 않는다.
    cursor = db.execute(
        "UPDATE contacts"
        " SET name = ?, phone = ?, email = ?, address = ?, memo = ?"
        " WHERE id = ?",
        (name, phone, email, address, memo, contact_id),
    )
    db.commit()
    # rowcount: 이 SQL로 바뀐 행의 수. 0이면 그 id의 연락처가 없었다는 뜻이다.
    return cursor.rowcount


def delete_contact(contact_id):
    """연락처 하나를 삭제한다. 실제로 지운 행 수(0 또는 1)를 돌려준다."""
    db = get_db()
    # WHERE id = ? 가 없으면 테이블의 모든 연락처가 지워진다. 절대 빼지 않는다.
    cursor = db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    db.commit()
    return cursor.rowcount


@click.command("init-db")
@with_appcontext  # 명령을 어떤 방식으로 실행해도 current_app, g 를 쓸 수 있게 한다.
def init_db_command():
    """터미널 명령 'flask --app app init-db' 로 실행되는 함수.

    앱이 시작될 때 테이블을 자동으로 만들므로 꼭 실행할 필요는 없다.
    실행해도 CREATE TABLE IF NOT EXISTS 라서 기존 데이터는 지워지지 않는다.
    """
    init_db()
    click.echo(f"데이터베이스를 준비했습니다: {current_app.config['DATABASE']}")


def init_app(app):
    """app.py 의 create_app() 에서 호출해 DB 기능을 앱에 등록한다."""
    # 요청이 끝날 때마다 close_db 를 자동으로 실행하도록 등록
    app.teardown_appcontext(close_db)
    # flask 명령에 init-db 를 추가
    app.cli.add_command(init_db_command)
