# 주소록 앱 자동 테스트
# 실행: pytest -v
# fixture(app, client, add, all_contacts)는 tests/conftest.py 에 있다.

import re


def names_on_page(response):
    """응답 HTML의 목록 표에서 이름 칸(class="name")의 글자만 뽑아 리스트로 돌려준다."""
    html = response.get_data(as_text=True)
    return re.findall(r'<td class="name"[^>]*>(.*?)</td>', html)


# ---------------------------------------------------------------
# 1. 목록 화면
# ---------------------------------------------------------------


def test_목록_화면_정상_응답(client):
    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "연락처 목록" in html
    # 처음에는 DB가 비어 있으므로 안내 문구가 보여야 한다.
    assert "아직 등록된 연락처가 없습니다" in html


# ---------------------------------------------------------------
# 2. 등록
# ---------------------------------------------------------------


def test_등록하면_목록에_나타남(client, add, all_contacts):
    response = add("홍길동", "010-1234-5678", email="hong@example.com", address="서울")

    # 저장에 성공하면 목록("/")으로 이동(302)한다.
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # 목록 화면에 이름과 안내 메시지가 보인다.
    page = client.get("/")
    html = page.get_data(as_text=True)
    assert names_on_page(page) == ["홍길동"]
    assert "010-1234-5678" in html
    assert "hong@example.com" in html
    assert "연락처가 등록되었습니다" in html

    # DB에도 실제로 1건 저장되었다.
    rows = all_contacts()
    assert len(rows) == 1
    assert rows[0]["name"] == "홍길동"
    assert rows[0]["memo"] is None  # 비워 둔 선택 항목은 NULL 로 저장


# ---------------------------------------------------------------
# 3. 수정
# ---------------------------------------------------------------


def test_수정하면_값이_바뀜(client, add, all_contacts):
    add("홍길동", "010-1234-5678")
    add("김철수", "010-3333-4444")
    hong_id = next(r["id"] for r in all_contacts() if r["name"] == "홍길동")

    # 수정 화면에는 기존 값이 채워져 있다.
    edit_page = client.get(f"/edit/{hong_id}")
    assert edit_page.status_code == 200
    assert 'value="홍길동"' in edit_page.get_data(as_text=True)

    response = client.post(
        f"/edit/{hong_id}",
        data={"name": "홍길순", "phone": "010-9999-8888", "email": "soon@example.com"},
    )
    assert response.status_code == 302

    page = client.get("/")
    assert "수정되었습니다" in page.get_data(as_text=True)
    assert "홍길순" in names_on_page(page)
    assert "홍길동" not in names_on_page(page)

    rows = {r["id"]: r for r in all_contacts()}
    assert rows[hong_id]["name"] == "홍길순"
    assert rows[hong_id]["phone"] == "010-9999-8888"
    assert rows[hong_id]["email"] == "soon@example.com"
    # WHERE id = ? 덕분에 다른 연락처는 그대로다.
    assert sorted(r["name"] for r in rows.values()) == ["김철수", "홍길순"]


def test_없는_연락처_수정은_404(client):
    assert client.get("/edit/999").status_code == 404
    assert client.post("/edit/999", data={"name": "a", "phone": "1"}).status_code == 404


# ---------------------------------------------------------------
# 4. 삭제
# ---------------------------------------------------------------


def test_삭제하면_목록에서_사라짐(client, add, all_contacts):
    add("홍길동", "010-1234-5678")
    add("김철수", "010-3333-4444")
    hong_id = next(r["id"] for r in all_contacts() if r["name"] == "홍길동")

    response = client.post(f"/delete/{hong_id}")
    assert response.status_code == 302

    page = client.get("/")
    assert "삭제되었습니다" in page.get_data(as_text=True)
    assert names_on_page(page) == ["김철수"]
    assert [r["name"] for r in all_contacts()] == ["김철수"]


def test_삭제는_POST만_허용(client, add, all_contacts):
    add("홍길동", "010-1234-5678")
    hong_id = all_contacts()[0]["id"]

    # 주소창 입력이나 링크(GET)로는 지워지지 않는다.
    assert client.get(f"/delete/{hong_id}").status_code == 405
    assert len(all_contacts()) == 1

    # 없는 id 삭제는 404
    assert client.post("/delete/999").status_code == 404


# ---------------------------------------------------------------
# 5. 검색
# ---------------------------------------------------------------


def test_이름_검색(client, add):
    add("홍길동", "010-1234-5678")
    add("홍길순", "010-2222-3333")
    add("김철수", "02-123-4567")

    page = client.get("/?q=홍")
    assert names_on_page(page) == ["홍길동", "홍길순"]
    assert "검색 결과: 2건" in page.get_data(as_text=True)

    # 이름 일부로도 찾는다.
    assert names_on_page(client.get("/?q=길순")) == ["홍길순"]


def test_전화번호_검색_하이픈_무시(client, add):
    add("홍길동", "010-1234-5678")
    add("김철수", "02-123-4567")

    assert names_on_page(client.get("/?q=01012345678")) == ["홍길동"]
    assert names_on_page(client.get("/?q=1234-5678")) == ["홍길동"]


def test_검색_결과_없음(client, add):
    add("홍길동", "010-1234-5678")

    page = client.get("/?q=없는사람")
    assert names_on_page(page) == []
    assert "검색 결과가 없습니다" in page.get_data(as_text=True)


# ---------------------------------------------------------------
# 6. 입력 검증
# ---------------------------------------------------------------


def test_이름이_비면_저장되지_않음(client, add, all_contacts):
    # 공백만 입력한 것도 빈 이름으로 본다.
    for blank in ["", "   "]:
        response = add(blank, "010-1234-5678")
        assert response.status_code == 400
        assert "이름을 입력하세요" in response.get_data(as_text=True)

    assert all_contacts() == []


def test_전화번호_형식이_틀리면_저장되지_않음(client, add, all_contacts):
    for bad_phone in ["010-abcd-1234", "010 1234 5678", "010--1234", "-0101234", "０１０-１２３４"]:
        response = add("홍길동", bad_phone)
        assert response.status_code == 400, bad_phone
        assert "숫자와 하이픈(-)만" in response.get_data(as_text=True)

    assert all_contacts() == []


def test_검증_실패하면_입력값이_폼에_남음(add):
    response = add("", "010-abcd", email="hong@", address="서울시", memo="남은 메모")
    html = response.get_data(as_text=True)

    assert 'value="010-abcd"' in html
    assert 'value="hong@"' in html
    assert 'value="서울시"' in html
    assert "남은 메모" in html


def test_수정할_때도_검증(client, add, all_contacts):
    add("홍길동", "010-1234-5678")
    hong_id = all_contacts()[0]["id"]

    response = client.post(f"/edit/{hong_id}", data={"name": "", "phone": "전화"})
    assert response.status_code == 400
    # 원래 값이 그대로 남아 있다.
    assert all_contacts()[0]["name"] == "홍길동"


# ---------------------------------------------------------------
# 7. 보안: SQL 인젝션, XSS
# ---------------------------------------------------------------


def test_SQL_인젝션_검색어로_전체가_나오지_않음(client, add):
    add("홍길동", "010-1234-5678")
    add("김철수", "010-3333-4444")

    for attack in ["' OR '1'='1", "%' OR 1=1 --", "%", "_"]:
        page = client.get("/", query_string={"q": attack})
        assert page.status_code == 200
        assert names_on_page(page) == [], attack


def test_SQL_인젝션_입력값은_글자로만_저장됨(add, all_contacts):
    add("김철수", "010-3333-4444")
    add("x'); DELETE FROM contacts; --", "010-1111-2222")

    # DELETE 문이 실행되지 않아 두 건 모두 남아 있다.
    names = [r["name"] for r in all_contacts()]
    assert "김철수" in names
    assert "x'); DELETE FROM contacts; --" in names


def test_XSS_스크립트가_실행되지_않게_이스케이프됨(client, add):
    add("<script>alert(1)</script>", "010-1234-5678")

    html = client.get("/").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
