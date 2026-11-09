# 주소록 (Address Book)

> 10주차 개선 내용은 [WEEK10.md](WEEK10.md) 참고

Python **Flask**와 **SQLite**로 만든 연락처 관리 웹 애플리케이션입니다.
별도의 DB 서버 없이 파일 하나(`instance/addressbook.db`)에 데이터를 저장하므로, 파이썬만 있으면 바로 실행할 수 있습니다.

파일 수는 적게, 구조는 실무에서 쓰는 방식(앱 팩토리, DB 모듈 분리, 템플릿 상속, 자동 테스트)으로 구성했습니다.

---

## 주요 기능

| 기능 | 설명 |
|---|---|
| 목록 보기 | 모든 연락처를 이름 가나다순 표로 표시 |
| 등록 | 이름·전화번호(필수), 이메일·주소·메모(선택) 입력 |
| 수정 | 기존 값이 채워진 폼에서 수정 |
| 삭제 | 확인 창("정말 삭제하시겠습니까?")을 거쳐 POST 방식으로만 삭제 |
| 검색 | 이름 또는 전화번호 일부로 검색. 전화번호는 하이픈 없이 입력해도 찾음 (`01012345678` → `010-1234-5678`) |
| 입력 검증 | 이름 30자 이하, 전화번호는 숫자와 하이픈만, 이메일 형식 검사. 틀린 칸 아래에 이유를 한글로 표시하고 입력값은 유지 |
| 안내 메시지 | 등록·수정·삭제 후 화면 위에 초록 상자로 결과 표시 |
| 반응형 화면 | 휴대폰처럼 좁은 화면에서는 표가 카드 모양으로 바뀜 |
| 보안 | SQL은 모두 파라미터 바인딩(`?`)으로 SQL 인젝션 차단, 템플릿 자동 이스케이프로 XSS 차단 |

### 화면 주소

| 주소 | 방식 | 화면 |
|---|---|---|
| `/` | GET | 목록 + 검색 (`/?q=검색어`) |
| `/add` | GET, POST | 새 연락처 등록 |
| `/edit/<id>` | GET, POST | 연락처 수정 |
| `/delete/<id>` | POST | 연락처 삭제 (화면 없음, 처리 후 목록으로 이동) |

---

## 폴더 구조

```
address_book/
├── app.py               # 앱 생성(create_app), 라우트(주소별 처리), 입력 검증
├── db.py                # DB 연결/종료, init-db 명령, 연락처 조회·등록·수정·삭제·검색 함수
├── schema.sql           # contacts 테이블 정의
├── templates/
│   ├── base.html        # 모든 페이지 공통 틀 (상단 바, 안내 메시지)
│   ├── index.html       # 목록 + 검색
│   ├── form.html        # 등록·수정 공용 입력 폼
│   └── 404.html         # 없는 페이지·연락처 안내
├── static/
│   └── style.css        # 화면 디자인 (외부 라이브러리 없음)
├── tests/
│   ├── conftest.py      # 테스트 준비 코드 (테스트 전용 임시 DB)
│   └── test_app.py      # 자동 테스트 18개
├── screenshots/         # 실습 과정 캡처
├── instance/            # 실행하면 자동 생성, addressbook.db 저장 (git 제외)
├── requirements.txt     # 필요한 패키지 목록
├── pytest.ini           # pytest 설정
├── .gitignore           # git 에 올리지 않을 파일 목록
├── CLAUDE.md            # Claude Code 용 프로젝트 안내·코딩 규칙
└── README.md            # 이 문서
```

### contacts 테이블

| 열 | 타입 | 설명 |
|---|---|---|
| `id` | INTEGER | 자동 증가 기본키 |
| `name` | TEXT | 이름 (필수) |
| `phone` | TEXT | 전화번호 (필수) |
| `email` | TEXT | 이메일 |
| `address` | TEXT | 주소 |
| `memo` | TEXT | 메모 |
| `created_at` | TEXT | 등록 시각 (자동 입력, 예: `2026-11-09 14:30:00`) |

---

## 설치 방법

> 아래 명령은 실제로 개발한 환경인 **Mac + zsh (VS Code 통합 터미널)** 기준입니다.
> Windows에서 다른 부분은 이 절 맨 끝의 [Windows에서 실행할 때](#windows에서-실행할-때)를 보세요.

### 0. 준비물

- **Python 3.10 이상** (개발 환경: Python 3.14)
- **Git** (커밋 작성자 이름·이메일 설정까지)
- 아래 명령은 모두 **프로젝트 폴더(`address_book`) 안에서** 실행합니다.
  VS Code에서 폴더를 열고 메뉴 **터미널 → 새 터미널**을 열면 바로 그 위치입니다.

```bash
python3 --version
git config --global user.name "내 이름"          # 처음 한 번
git config --global user.email "내이메일@example.com"   # 처음 한 번
git config user.email
```

**✅ 성공 확인**
- [ ] `python3 --version` 이 `Python 3.10` 이상을 출력한다.
- [ ] `git config user.email` 이 내 이메일을 출력한다. (빈 줄이면 커밋 작성자가 `이름@컴퓨터이름.local` 로 기록된다)

### 1. 프로젝트 받기

```bash
git clone <저장소 주소> address_book
cd address_book
```
(git을 쓰지 않는다면 압축 파일을 받아 풀고, 그 폴더로 이동하세요.)

**✅ 성공 확인**
- [ ] `ls` 를 입력하면 `app.py`, `db.py`, `requirements.txt` 가 보인다.

### 2. 가상환경 만들기 (처음 한 번)

가상환경은 이 프로젝트 전용 파이썬 패키지 보관함입니다. 다른 프로젝트와 패키지 버전이 섞이지 않게 해 줍니다.

```bash
python3 -m venv .venv
```

**✅ 성공 확인**
- [ ] 프로젝트 폴더에 `.venv` 폴더가 생겼다. (`ls -a` 로 확인)

### 3. 가상환경 켜기 (터미널을 새로 열 때마다)

```bash
source .venv/bin/activate
```

끌 때는 `deactivate` 를 입력합니다.

**✅ 성공 확인**
- [ ] 프롬프트 앞에 `(.venv)` 가 붙었다.
- [ ] `which python` 이 `.../address_book/.venv/bin/python` 을 출력한다.

### 4. 패키지 설치 (처음 한 번)

가상환경이 켜진 상태에서 실행합니다.

```bash
pip install -r requirements.txt
```

`requirements.txt` 에는 Flask, pytest와 함께 설치되는 패키지가 정확한 버전으로 적혀 있어, 누구나 같은 환경을 만들 수 있습니다.

**✅ 성공 확인**
- [ ] 마지막에 `Successfully installed ...` (또는 `Requirement already satisfied`) 가 나오고 `ERROR` 가 없다.
- [ ] `flask --version` 이 `Flask 3.1.3` 을 포함해 출력한다.

### Windows에서 실행할 때

나머지 명령(`pip`, `flask`, `pytest`)은 같고, 아래 두 가지만 다릅니다.

| 단계 | Mac (zsh) | Windows PowerShell |
|---|---|---|
| 가상환경 만들기 | `python3 -m venv .venv` | `py -m venv .venv` |
| 가상환경 켜기 | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |

- Python을 새로 설치할 때 [python.org](https://www.python.org/downloads/) 설치 화면에서 **"Add python.exe to PATH"** 를 꼭 체크하세요.
- PowerShell에서 "스크립트를 실행할 수 없으므로…" 오류가 나면 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 를 한 번 실행한 뒤 다시 켜 보세요.

---

## DB 준비 (따로 할 일 없음)

앱이 시작될 때 `instance/` 폴더와 `instance/addressbook.db` 파일, `contacts` 테이블이 **자동으로 만들어집니다.** 별도의 초기화 명령은 필요 없습니다.

- 테이블이 이미 있으면 그대로 두므로 **저장된 연락처는 지워지지 않습니다.** (`CREATE TABLE IF NOT EXISTS`)
- 데이터를 모두 지우고 처음부터 시작하려면 서버를 끄고 `instance/addressbook.db` 파일을 삭제한 뒤 다시 실행하세요.
- 예전 방식인 `flask --app app init-db` 도 남아 있지만, 실행하지 않아도 됩니다.

**✅ 성공 확인** (아래 "실행 방법"으로 서버를 처음 켠 뒤)
- [ ] `instance/addressbook.db` 파일이 생겼다.
- [ ] 첫 화면에 `no such table` 오류 없이 "아직 등록된 연락처가 없습니다" 가 보인다.

---

## 실행 방법

### 터미널 2개 쓰기

VS Code 터미널 패널의 **+** 버튼으로 터미널을 하나 더 열어, 역할을 나눠 씁니다.

| 터미널 | 용도 |
|---|---|
| **Claude용** | Claude Code 작업, `pytest`, `git` |
| **서버용** | 서버 실행·종료만 (켜 두면 그 터미널은 서버가 차지함) |

서버는 **학생이 서버용 터미널에서 직접** 실행합니다. Claude는 서버를 직접 띄우지 않고 실행 명령만 안내합니다. 두 곳에서 서버를 띄우면 같은 포트를 두고 충돌("Address already in use")이 나기 때문입니다. (규칙은 `CLAUDE.md` 에 있습니다)

### 서버 켜기 (서버용 터미널)

```bash
source .venv/bin/activate
flask --app app run --debug --port 5001
```

브라우저에서 **http://127.0.0.1:5001** 을 엽니다. 서버를 끌 때는 서버용 터미널에서 **Ctrl + C** 를 누릅니다.

- `--debug`: 코드를 고치면 서버가 자동으로 다시 시작되고, 오류가 나면 자세한 내용을 보여 줍니다. **개발할 때만** 사용하세요.
- `--port 5001`: Mac은 AirPlay 수신 모드가 5000번 포트를 쓰고 있어서, 5000번으로 켜면 403 오류나 "Address already in use" 가 납니다. 그래서 5001번을 씁니다.

**✅ 성공 확인**
- [ ] 서버용 터미널에 `Running on http://127.0.0.1:5001` 과 `Debugger is active!` 가 보인다.
- [ ] 브라우저에서 http://127.0.0.1:5001 을 열면 남색 상단 바의 "주소록" 목록 화면이 보인다.
- [ ] 서버용 터미널에 `"GET / HTTP/1.1" 200` 로그가 찍힌다.
- [ ] 연락처를 하나 등록하면 목록에 나타나고 "연락처가 등록되었습니다." 가 보인다.
- [ ] Ctrl + C 로 끄고 다시 켜도 등록한 연락처가 남아 있다.

> **"Address already in use" 가 나오면** 이미 5001번 포트를 쓰는 서버가 있다는 뜻입니다. 다른 터미널에 켜 둔 서버가 있는지 확인해 Ctrl + C 로 끄세요. 어디서 켰는지 모르겠다면 `lsof -i :5001` 로 프로세스 번호(PID)를 확인한 뒤 `kill PID번호` 로 끕니다.

---

## 테스트 방법

가상환경이 켜진 상태에서 **Claude용 터미널**에서 실행합니다. (서버를 켜 두지 않아도 됩니다)

```bash
pytest -v
```

짧게 보려면 `pytest -q` 를 쓰세요.

- 테스트는 매번 **테스트 전용 임시 DB**를 새로 만들어 사용하므로, 실제 `instance/addressbook.db` 의 데이터는 바뀌지 않습니다.
- 확인하는 내용: 목록 화면 응답, 등록·수정·삭제, 삭제는 POST만 허용, 없는 연락처는 404, 이름·전화번호 검색, 입력 검증(빈 이름, 잘못된 전화번호), SQL 인젝션(`' OR '1'='1`)·XSS(`<script>`) 차단, init-db 없이 첫 화면이 열리고 재시작해도 데이터가 남는지

**✅ 성공 확인**
- [ ] 마지막 줄에 `18 passed` 가 나오고 `failed` 나 `error` 가 없다.
- [ ] 테스트 후에도 브라우저에서 보던 기존 연락처가 그대로 있다.

---

## 참고: 공개 서버에 올리기 전에

이 프로젝트는 **내 컴퓨터에서 실습하는 용도**입니다. 인터넷에 공개하려면 최소한 다음을 처리해야 합니다.

- `--debug` 없이 실행 (debug 화면에서는 서버의 파이썬 코드를 실행할 수 있음)
- 환경변수 `SECRET_KEY` 에 긴 무작위 값 설정 (없으면 개발용 기본값 `"dev"` 사용)
  - Mac: `export SECRET_KEY="긴-무작위-문자열"`
  - Windows PowerShell: `$env:SECRET_KEY="긴-무작위-문자열"`
- CSRF 보호 추가 (예: Flask-WTF) — 지금은 다른 사이트가 삭제 요청을 몰래 보낼 수 있음
- 로그인 기능 추가 — 지금은 접속한 누구나 연락처를 보고 고칠 수 있음

---

## 실습 과정 캡처

![연결 확인](screenshots/00_연결확인_.png)

중요한 이유: Claude Code가 지금 연 프로젝트 폴더를 제대로 인식하는지 먼저 확인하고 시작했다.

![Plan 모드로 세운 개발 계획](screenshots/01_plan모드_계획.png)

중요한 이유: 바로 코드를 짜지 않고 Plan 모드로 기능, 화면, 개발 순서를 먼저 정리했다.

![계획한 폴더 구조](screenshots/01-2_plan폴더구조.png)

중요한 이유: 파일은 적게 쓰되 app.py는 웹 처리, db.py는 데이터 처리로 역할을 나누는 구조를 미리 정했다.

![명령 실행 승인 요청](screenshots/02-1_승인요청.png)

중요한 이유: Claude가 터미널 명령을 실행하기 전에 승인을 받아서, 무엇이 실행되는지 직접 보고 결정할 수 있었다.

![탐색기에서 본 프로젝트 골격](screenshots/02-2_탐색기.png)

중요한 이유: templates, static, tests 폴더와 .gitignore, CLAUDE.md까지 골격이 만들어진 것을 탐색기에서 확인했다.

![가상환경(.venv) 켜기](screenshots/02-3_venv.png)

중요한 이유: 가상환경을 켜서 프롬프트 앞에 (.venv)가 붙는 걸 확인했다. 이 프로젝트 패키지가 다른 프로젝트와 섞이지 않는다.

![python app.py 실행](screenshots/03-3_첫화면.png)

중요한 이유: python app.py로 실행해 Debug mode: on을 확인했다. 코드를 고치면 서버가 알아서 다시 시작된다.

![첫 화면 접속과 서버 로그](screenshots/03-4_서버로그.png)

중요한 이유: 브라우저로 접속하니 서버 로그에 GET / 200이 찍혀서 요청과 응답이 오가는 걸 눈으로 볼 수 있었다.

![개발 서버 실행과 첫 화면](screenshots/03-4_서버실행.png)

중요한 이유: base.html을 상속한 index.html이 "아직 등록된 연락처가 없습니다"를 띄우면서 첫 화면이 완성됐다.

![DB 검증 결과](screenshots/04-1_DB검증결과.png)

중요한 이유: 전화번호 없이 넣으면 NOT NULL 오류로 거부돼서, 앱뿐 아니라 DB에서도 필수값이 지켜진다는 걸 알았다.

![schema.sql과 생성된 DB 파일](screenshots/04-2_DB생성.png)

중요한 이유: init-db 명령 한 번으로 instance/addressbook.db가 생기고 schema.sql대로 contacts 테이블이 만들어졌다.

![연락처 등록과 목록](screenshots/05_등록목록.png)

중요한 이유: 연락처 3명을 등록하니 이름 가나다순으로 정렬되고 "연락처가 등록되었습니다" 메시지가 떴다.

![연락처 수정과 삭제](screenshots/06_수정삭제.png)

중요한 이유: 김해사의 번호를 수정하고 이바다를 삭제한 결과가 목록에 바로 반영됐다.

![보안 점검 - 점검 범위 밖 항목](screenshots/07-1_보안점검.png)

중요한 이유: CSRF, SECRET_KEY, debug 모드처럼 실제로 공개하기 전에 꼭 챙겨야 할 점을 알게 됐다.

![보안 점검 - 파라미터 바인딩](screenshots/07-1b_보안점검.png)

중요한 이유: 모든 SQL이 ? 파라미터 바인딩을 써서 SQL 인젝션이 막혀 있다는 걸 코드 줄 단위로 확인했다.

![SQL 인젝션 차단](screenshots/07-2_SQL인젝션차단.png)

중요한 이유: 검색창에 `' OR '1'='1`을 넣어도 결과가 0건이라, SQL 인젝션이 실제로 막히는 걸 확인했다.

![XSS 차단](screenshots/07-3_XSS차단.png)

중요한 이유: 이름에 `<script>alert(1)</script>`를 넣어도 실행되지 않고 글자로만 보여서 XSS가 막힌다는 걸 확인했다.

![디자인 적용 전](screenshots/8-1_디자인전.png)

중요한 이유: CSS를 넣기 전의 기본 HTML 화면으로, 디자인 후와 비교하려고 남겼다.

![디자인 적용 후](screenshots/08-2_디자인후.png)

중요한 이유: style.css 하나로 남색 상단 바, 줄무늬 표, 빨간 삭제 버튼을 적용하니 훨씬 보기 편해졌다.

![pytest 테스트 통과](screenshots/09_pytest통과.png)

중요한 이유: 테스트 16개가 모두 통과해서, 기능과 보안을 매번 손으로 확인하지 않고 명령 한 줄로 검사할 수 있게 됐다.

![커밋 이력](screenshots/10_커밋이력.png)

중요한 이유: 단계마다 커밋을 나눠 두어서 언제 무엇을 만들었는지 이력으로 따라가 볼 수 있다.

![최종 커밋 이력](screenshots/10-2_최종커밋이력.png)

중요한 이유: 캡처 설명까지 10개 커밋으로 마무리했고, 커밋하지 않은 변경 없이 깨끗한 상태로 프로젝트를 끝냈다.
