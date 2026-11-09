# 주소록 웹 애플리케이션

## 프로젝트 목적
연락처(이름, 전화번호, 이메일, 주소, 메모)를 관리하는 웹 애플리케이션.
목록 보기, 등록, 수정, 삭제, 이름·전화번호 검색 기능을 제공한다.
Python Flask와 SQLite(별도 DB 서버 없이 파일 하나)로 만든다.
대학 4학년 학생이 따라 할 수 있도록 파일 수는 적게, 구조는 실무형으로 유지한다.
사용자용 설치·실행 안내는 README.md 에 있다.

## 폴더 구조
```
address_book/
├── app.py               # 앱 생성(create_app), 라우트, 입력 검증(validate_contact)
├── db.py                # DB 연결/종료, init-db 명령, 연락처 CRUD·검색 함수
├── schema.sql           # contacts 테이블 정의
├── templates/
│   ├── base.html        # 공통 틀 (상단 바, flash 메시지, style.css 연결)
│   ├── index.html       # 목록 + 검색
│   ├── form.html        # 등록·수정 공용 폼
│   └── 404.html         # 404 안내
├── static/style.css     # 화면 디자인 (외부 라이브러리 없음, 640px 이하 반응형)
├── tests/
│   ├── conftest.py      # fixture: 테스트마다 tmp_path 임시 DB 사용
│   └── test_app.py      # pytest 테스트
├── pytest.ini           # pytest 설정 (pythonpath = ., testpaths = tests)
├── instance/            # 실행 시 자동 생성, addressbook.db 저장 (git 제외)
├── screenshots/         # 실습 과정 캡처 이미지 (README에서 참조)
├── requirements.txt     # 의존 패키지 (pip freeze 결과)
├── README.md            # 사용자용 설치·실행·테스트 안내 (Mac/Windows)
└── CLAUDE.md
```

## 라우트
| 주소 | 메서드 | 함수 |
|---|---|---|
| `/` (`?q=검색어`) | GET | `index` |
| `/add` | GET, POST | `add_contact` |
| `/edit/<int:contact_id>` | GET, POST | `edit_contact` |
| `/delete/<int:contact_id>` | POST | `delete_contact` |

## 명령
```bash
# 가상환경 켜기
source .venv/bin/activate          # Mac
.venv\Scripts\Activate.ps1         # Windows PowerShell

pip install -r requirements.txt    # 패키지 설치 (처음 한 번)
flask --app app init-db            # DB 테이블 생성 (처음 한 번, 다시 실행해도 데이터 유지)
flask --app app run --debug        # 개발 서버 실행 → http://127.0.0.1:5000
pytest -v                          # 테스트 실행 (실제 DB는 건드리지 않음)
```

## 코딩 규칙
- 주석은 한글로 작성한다. 템플릿 안의 설명은 브라우저로 보내지지 않는 Jinja 주석 `{# #}` 을 쓴다.
- SQL은 반드시 파라미터 바인딩(`?` 자리표시자)을 사용한다. f-string, `+`, `%`, `.format()`으로 SQL 문자열을 만들지 않는다.
  - 좋은 예: `db.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))`
  - 나쁜 예: `db.execute(f"SELECT * FROM contacts WHERE id = {contact_id}")`
  - LIKE 검색은 `%` 를 값 쪽에 붙여 `?` 로 넘긴다.
  - `executescript()` 는 schema.sql 전용. 사용자 입력에 절대 쓰지 않는다.
- UPDATE, DELETE 문에는 반드시 `WHERE id = ?` 를 쓴다.
- 라우트 함수(app.py)에 SQL을 직접 쓰지 않고 db.py의 함수를 호출한다.
- 데이터를 바꾸는 요청(등록·수정·삭제)은 POST로만 받고, 처리 후 목록으로 리다이렉트한다.
- 입력 검증은 서버(`validate_contact`)에서 한다. 브라우저의 `required` 등은 보조 수단이다.
- 템플릿에서 `|safe` 를 쓰지 않는다. 인라인 JavaScript에 사용자 값을 넣지 않는다.
- 기능을 바꾸면 tests/test_app.py 에 테스트를 추가하고 `pytest` 가 모두 통과하는지 확인한다.
