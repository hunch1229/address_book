# 주소록 웹 애플리케이션의 시작 파일
# Flask 앱을 만들고, 주소(URL)마다 어떤 화면을 보여 줄지 정한다.

import os

from flask import Flask, render_template

import db


def create_app(test_config=None):
    """Flask 앱을 만들어 돌려주는 함수 (앱 팩토리 패턴).

    앱을 함수 안에서 만들어 두면, 나중에 테스트할 때
    test_config 로 테스트용 DB 경로를 넘겨 실제 데이터와 섞이지 않게 할 수 있다.
    """
    # instance_relative_config=True: instance/ 폴더를 앱 전용 데이터 폴더로 쓴다.
    app = Flask(__name__, instance_relative_config=True)

    # 기본 설정: DB 파일은 instance/addressbook.db
    # app.instance_path 는 프로젝트 폴더 안의 instance/ 의 전체 경로다.
    app.config["DATABASE"] = os.path.join(app.instance_path, "addressbook.db")

    # 테스트할 때 넘겨준 설정이 있으면 기본 설정을 덮어쓴다.
    if test_config is not None:
        app.config.update(test_config)

    # instance/ 폴더가 없으면 만든다. (이미 있으면 그냥 넘어간다)
    os.makedirs(app.instance_path, exist_ok=True)

    # db.py 의 DB 연결 정리 기능과 init-db 명령을 앱에 등록한다.
    db.init_app(app)

    # "/" 주소로 들어오면 연락처 목록 화면을 보여 준다.
    @app.route("/")
    def index():
        # templates/index.html 을 찾아 HTML로 바꿔서 브라우저에 보낸다.
        return render_template("index.html")

    return app


# "python app.py" 로 직접 실행했을 때만 아래 코드가 동작한다.
# (flask 명령으로 실행할 때는 flask가 create_app()을 알아서 찾아 호출한다.)
if __name__ == "__main__":
    # debug=True: 코드를 고치면 서버가 자동으로 다시 시작되고,
    # 오류가 나면 브라우저에 자세한 오류 화면을 보여 준다. (개발할 때만 사용)
    create_app().run(debug=True)
