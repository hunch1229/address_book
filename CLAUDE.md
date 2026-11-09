# 주소록 웹 애플리케이션

## 프로젝트 목적
연락처(이름, 전화번호, 이메일, 주소, 메모)를 관리하는 웹 애플리케이션.
목록 보기, 등록, 수정, 삭제, 이름·전화번호 검색 기능을 제공한다.
Python Flask와 SQLite(별도 DB 서버 없이 파일 하나)로 만든다.
대학 4학년 학생이 따라 할 수 있도록 파일 수는 적게, 구조는 실무형으로 유지한다.

## 폴더 구조
```
address_book/
├── app.py               # 앱 생성(create_app), 라우트, 입력 검증
├── db.py                # DB 연결/종료, init-db 명령, 연락처 CRUD·검색 함수
├── schema.sql           # contacts 테이블 정의
├── templates/           # Jinja2 템플릿 (base.html, index.html, add.html)
├── static/              # style.css
├── tests/               # pytest 테스트 (test_app.py)
├── instance/            # 실행 시 자동 생성, addressbook.db 저장 (git 제외)
├── screenshots/         # 작업 과정 캡처 이미지
├── requirements.txt     # 의존 패키지 (pip freeze 결과)
└── CLAUDE.md
```

## 실행 명령
```bash
source .venv/bin/activate          # 가상환경 켜기
pip install -r requirements.txt    # 패키지 설치 (처음 한 번)
flask --app app init-db            # DB 테이블 생성 (처음 한 번)
flask --app app run --debug        # 개발 서버 실행 → http://127.0.0.1:5000
```

## 테스트 명령
```bash
pytest -v
```

## 코딩 규칙
- 주석은 한글로 작성한다.
- SQL은 반드시 파라미터 바인딩(`?` 자리표시자)을 사용한다. f-string, `+`, `%`, `.format()`으로 SQL 문자열을 만들지 않는다.
  - 좋은 예: `db.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))`
  - 나쁜 예: `db.execute(f"SELECT * FROM contacts WHERE id = {contact_id}")`
- 라우트 함수(app.py)에 SQL을 직접 쓰지 않고 db.py의 함수를 호출한다.
- 데이터를 바꾸는 요청(등록·수정·삭제)은 POST로만 받고, 처리 후 목록으로 리다이렉트한다.
- 입력 검증은 서버에서 한다. 브라우저의 `required`는 보조 수단이다.
