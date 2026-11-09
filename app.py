# 주소록 웹 애플리케이션의 시작 파일
# Flask 앱을 만들고, 주소(URL)마다 어떤 화면을 보여 줄지 정한다.

import os

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

import db

# 폼에서 받는 입력칸 이름 목록 (등록·수정 공통)
FORM_FIELDS = ("name", "phone", "email", "address", "memo")


def read_contact_form():
    """요청에서 연락처 입력값을 꺼내 검사한다.

    돌려주는 값: (form, errors)
    - form   : 앞뒤 공백을 지운 입력값 딕셔너리
    - errors : 오류 메시지 목록 (문제가 없으면 빈 목록)
    """
    form = {key: request.form.get(key, "").strip() for key in FORM_FIELDS}

    # 필수 항목 검사 (형식 검사는 6단계에서 추가)
    errors = []
    if not form["name"]:
        errors.append("이름을 입력하세요.")
    if not form["phone"]:
        errors.append("전화번호를 입력하세요.")
    return form, errors


def to_db_values(form):
    """입력값을 DB에 넣을 형태로 바꾼다.

    선택 항목(이메일, 주소, 메모)이 비어 있으면 빈 문자열("") 대신 NULL(None)로 저장한다.
    """
    return {
        "name": form["name"],
        "phone": form["phone"],
        "email": form["email"] or None,
        "address": form["address"] or None,
        "memo": form["memo"] or None,
    }


def create_app(test_config=None):
    """Flask 앱을 만들어 돌려주는 함수 (앱 팩토리 패턴).

    앱을 함수 안에서 만들어 두면, 나중에 테스트할 때
    test_config 로 테스트용 DB 경로를 넘겨 실제 데이터와 섞이지 않게 할 수 있다.
    """
    # instance_relative_config=True: instance/ 폴더를 앱 전용 데이터 폴더로 쓴다.
    app = Flask(__name__, instance_relative_config=True)

    # 기본 설정
    app.config.update(
        # DB 파일은 instance/addressbook.db
        # app.instance_path 는 프로젝트 폴더 안의 instance/ 의 전체 경로다.
        DATABASE=os.path.join(app.instance_path, "addressbook.db"),
        # flash 메시지를 쓰려면 비밀키가 필요하다.
        # 실제 서비스에서는 환경변수 SECRET_KEY 에 긴 무작위 값을 넣어 쓴다.
        # 환경변수가 없으면 개발용 기본값을 쓴다.
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
    )

    # 테스트할 때 넘겨준 설정이 있으면 기본 설정을 덮어쓴다.
    if test_config is not None:
        app.config.update(test_config)

    # instance/ 폴더가 없으면 만든다. (이미 있으면 그냥 넘어간다)
    os.makedirs(app.instance_path, exist_ok=True)

    # db.py 의 DB 연결 정리 기능과 init-db 명령을 앱에 등록한다.
    db.init_app(app)

    # 404 오류(없는 주소, 없는 연락처)가 나면 기본 영어 화면 대신 404.html 을 보여 준다.
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    # "/" 주소: 연락처 목록 화면
    @app.route("/")
    def index():
        contacts = db.list_contacts()
        # 템플릿에 contacts 라는 이름으로 목록을 넘겨준다.
        return render_template("index.html", contacts=contacts)

    # "/add" 주소: 연락처 등록 화면
    # GET  = 빈 입력 폼을 보여 준다.
    # POST = 폼에서 보낸 값을 저장한다.
    @app.route("/add", methods=["GET", "POST"])
    def add_contact():
        # 등록 화면과 수정 화면은 form.html 을 같이 쓰고, 제목과 보낼 주소만 다르다.
        page = {"page_title": "새 연락처 등록", "action_url": url_for("add_contact")}

        if request.method == "POST":
            form, errors = read_contact_form()
            if errors:
                # 오류가 있으면 저장하지 않고, 입력한 값을 그대로 채운 폼을 다시 보여 준다.
                return render_template("form.html", form=form, errors=errors, **page), 400

            db.create_contact(**to_db_values(form))
            # 다음 화면에서 한 번 보여 줄 안내 메시지를 저장해 둔다.
            flash("연락처가 등록되었습니다.")
            # 저장한 뒤에는 목록 화면으로 이동시킨다. (PRG 패턴)
            # 이렇게 하면 새로고침해도 같은 연락처가 두 번 저장되지 않는다.
            return redirect(url_for("index"))

        # GET 요청: 빈 폼을 보여 준다.
        return render_template("form.html", form={}, errors=[], **page)

    # "/edit/3" 같은 주소: 3번 연락처 수정 화면
    # <int:contact_id>: 주소의 숫자 부분을 정수로 받는다. 숫자가 아니면 자동으로 404.
    @app.route("/edit/<int:contact_id>", methods=["GET", "POST"])
    def edit_contact(contact_id):
        contact = db.get_contact(contact_id)
        if contact is None:
            # 없는 id 면 404 화면을 보여 주고 함수를 끝낸다.
            abort(404)

        page = {
            "page_title": "연락처 수정",
            "action_url": url_for("edit_contact", contact_id=contact_id),
        }

        if request.method == "POST":
            form, errors = read_contact_form()
            if errors:
                return render_template("form.html", form=form, errors=errors, **page), 400

            db.update_contact(contact_id, **to_db_values(form))
            flash("수정되었습니다.")
            return redirect(url_for("index"))

        # GET 요청: DB에 저장된 기존 값을 채운 폼을 보여 준다.
        # dict(contact): sqlite3.Row 를 딕셔너리로 바꿔 form.get() 을 쓸 수 있게 한다.
        return render_template("form.html", form=dict(contact), errors=[], **page)

    # "/delete/3" 같은 주소: 3번 연락처 삭제
    # methods=["POST"]: POST 요청만 받는다. 주소창에 입력하거나 링크를 눌러서(GET)
    # 접근하면 405(허용되지 않은 방식) 오류가 나서 실수로 지워지는 일이 없다.
    @app.route("/delete/<int:contact_id>", methods=["POST"])
    def delete_contact(contact_id):
        # 지운 행이 0개면 원래 없던 id 이므로 404
        if db.delete_contact(contact_id) == 0:
            abort(404)
        flash("삭제되었습니다.")
        return redirect(url_for("index"))

    return app


# "python app.py" 로 직접 실행했을 때만 아래 코드가 동작한다.
# (flask 명령으로 실행할 때는 flask가 create_app()을 알아서 찾아 호출한다.)
if __name__ == "__main__":
    # debug=True: 코드를 고치면 서버가 자동으로 다시 시작되고,
    # 오류가 나면 브라우저에 자세한 오류 화면을 보여 준다. (개발할 때만 사용)
    create_app().run(debug=True)
