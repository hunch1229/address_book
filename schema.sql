-- 주소록 데이터베이스 테이블 정의
-- "flask --app app init-db" 명령을 실행하면 이 파일의 SQL이 실행된다.

-- IF NOT EXISTS: 테이블이 이미 있으면 건너뛴다.
-- 그래서 초기화 명령을 여러 번 실행해도 저장된 연락처가 지워지지 않는다.
CREATE TABLE IF NOT EXISTS contacts (
    -- 연락처 번호. 새 행을 넣을 때마다 1, 2, 3 ... 자동으로 붙는다.
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 이름 (필수): NOT NULL 이라 값 없이 저장하면 DB가 거부한다.
    name        TEXT    NOT NULL,
    -- 전화번호 (필수)
    phone       TEXT    NOT NULL,
    -- 이메일, 주소, 메모 (선택): 비워 둘 수 있다.
    email       TEXT,
    address     TEXT,
    memo        TEXT,
    -- 등록 시각: 값을 주지 않으면 저장하는 순간의 한국 시간(컴퓨터 시간대)이 들어간다.
    -- 예) 2026-11-09 14:30:00
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
