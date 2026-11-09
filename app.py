# 주소록 웹 애플리케이션의 시작 파일
# Flask 앱을 만들고, 주소(URL)마다 어떤 화면을 보여 줄지 정한다.

import os

from flask import Flask, flash, redirect, render_template, request, url_for

import db


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
        if request.method == "POST":
            # 폼에서 보낸 값을 꺼내고 앞뒤 공백을 지운다.
            form = {
                key: request.form.get(key, "").strip()
                for key in ("name", "phone", "email", "address", "memo")
            }

            # 필수 항목 검사 (형식 검사는 6단계에서 추가)
            errors = []
            if not form["name"]:
                errors.append("이름을 입력하세요.")
            if not form["phone"]:
                errors.append("전화번호를 입력하세요.")

            if errors:
                # 오류가 있으면 저장하지 않고, 입력한 값을 그대로 채운 폼을 다시 보여 준다.
                return render_template("add.html", form=form, errors=errors), 400

            # 선택 항목이 비어 있으면 빈 문자열("") 대신 NULL(None)로 저장한다.
            db.create_contact(
                name=form["name"],
                phone=form["phone"],
                email=form["email"] or None,
                address=form["address"] or None,
                memo=form["memo"] or None,
            )
            # 다음 화면에서 한 번 보여 줄 안내 메시지를 저장해 둔다.
            flash("연락처가 등록되었습니다.")
            # 저장한 뒤에는 목록 화면으로 이동시킨다. (PRG 패턴)
            # 이렇게 하면 새로고침해도 같은 연락처가 두 번 저장되지 않는다.
            return redirect(url_for("index"))

        # GET 요청: 빈 폼을 보여 준다.
        return render_template("add.html", form={}, errors=[])

    return app


# "python app.py" 로 직접 실행했을 때만 아래 코드가 동작한다.
# (flask 명령으로 실행할 때는 flask가 create_app()을 알아서 찾아 호출한다.)
if __name__ == "__main__":
    # debug=True: 코드를 고치면 서버가 자동으로 다시 시작되고,
    # 오류가 나면 브라우저에 자세한 오류 화면을 보여 준다. (개발할 때만 사용)
    create_app().run(debug=True)
