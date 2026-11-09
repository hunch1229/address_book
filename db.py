# 데이터베이스 관련 코드를 모아 둔 파일
# - DB 연결 열기/닫기
# - 테이블을 만드는 초기화 명령 (flask --app app init-db)
# 파이썬에 기본으로 들어 있는 sqlite3 모듈만 사용한다. (추가 설치 필요 없음)

import sqlite3

import click
from flask import current_app, g


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


def list_contacts():
    """모든 연락처를 이름 가나다순으로 돌려준다."""
    # 한글은 유니코드 순서가 가나다순이라 ORDER BY name 으로 정렬된다.
    # COLLATE NOCASE: 영어 이름은 대소문자 구분 없이 정렬 (Kim, kim 을 같이 취급)
    # 이름이 같으면 먼저 등록한 연락처(id가 작은 것)가 위로 온다.
    return get_db().execute(
        "SELECT id, name, phone, email, address, memo, created_at"
        " FROM contacts"
        " ORDER BY name COLLATE NOCASE, id"
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


@click.command("init-db")
def init_db_command():
    """터미널 명령 'flask --app app init-db' 로 실행되는 함수."""
    init_db()
    click.echo(f"데이터베이스를 준비했습니다: {current_app.config['DATABASE']}")


def init_app(app):
    """app.py 의 create_app() 에서 호출해 DB 기능을 앱에 등록한다."""
    # 요청이 끝날 때마다 close_db 를 자동으로 실행하도록 등록
    app.teardown_appcontext(close_db)
    # flask 명령에 init-db 를 추가
    app.cli.add_command(init_db_command)
