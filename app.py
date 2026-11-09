# 주소록 웹 애플리케이션의 시작 파일
# Flask 앱을 만들고, 주소(URL)마다 어떤 화면을 보여 줄지 정한다.

from flask import Flask, render_template


def create_app():
    """Flask 앱을 만들어 돌려주는 함수 (앱 팩토리 패턴).

    앱을 함수 안에서 만들어 두면, 나중에 테스트할 때
    실제 DB 대신 테스트용 설정으로 앱을 따로 만들 수 있다.
    """
    app = Flask(__name__)

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
