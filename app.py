from flask import Flask, session, url_for, render_template, flash, send_from_directory, jsonify ,request, redirect
import os
import requests
from datetime import datetime, timedelta
from functools import wraps
from models import DBManager
import json

app = Flask(__name__)



app.secret_key = 'your-secret-key'  # 비밀 키 설정, 실제 애플리케이션에서는 더 안전한 방법으로 설정해야 함if __name__ == '__main__':

manager = DBManager()


# 파일 업로드 경로 설정
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
# 업로드 폴더가 없으면 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


### 푸터에 들어갈 날짜데이터 (context_processor 사용)
@app.context_processor
def inject_full_date():
    weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    today_date = datetime.now()
    today = today_date.strftime("%Y년 %m월 %d일")
    weekday = weekdays[today_date.weekday()]
    full_date = f"{today} ({weekday})"
    return {"full_date": full_date}


### 홈페이지
@app.route('/')
def index():
    return render_template('index.html')


### 로그인 기능
## 로그인 필수 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')  # 로그인되지 않았다면 로그인 페이지로 리디렉션
        return f(*args, **kwargs)
    return decorated_function

## 관리자 권한 필수 데코레이터
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['role'] != 'admin':
            return "접근 권한이 없습니다", 403  # 관리자만 접근 가능
        return f(*args, **kwargs)
    return decorated_function


### 회원가입 페이지등록 
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        birthday = request.form['birthday']
        username = request.form['username']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        gender = request.form['gender']
        #암호가 일치하는지 확인
        if password != confirm_password:
            flash('암호가 일치하지 않습니다', 'error')
            return render_template('signup.html')
        #회원과 아이디가 중복되는지 확인
        if manager.duplicate_member(userid):
            flash('이미 존재하는 아이디 입니다.', 'error')
            return render_template('signup.html')
        #탈퇴 아이디와 중복확인
        if manager.duplicate_removed_member(userid):
            flash('이미 존재하는 아이디 입니다.','error')
            return render_template('signup.html')
        #회원가입 이메일 입력여부
        if not email:
            flash("이메일을 입력해주세요.", "danger")
            return render_template('signup.html')
        #회원 이메일과 중복여부
        if manager.duplicate_email(email):
            flash('이미 등록된 이메일 입니다.', 'error')
            return render_template('signup.html')
        #탈퇴 이메일과 중복여부 
        if manager.duplicate_removed_email(email):
            flash('이미 등록된 이메일 입니다.', 'error')
            return render_template('signup.html')
        # 생년월일이 올바른 날짜 형식인지 확인

        try:
            # 'YYYY-MM-DD' 형식으로 변환
            birthday = datetime.strptime(birthday, "%Y-%m-%d")
        except ValueError:
            flash('잘못된 날짜 형식입니다. 생년월일을 다시 확인해주세요.', 'error')
            return render_template('signup.html')

        # 나이 계산 (현재 날짜와 비교)
        today = datetime.today()
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

        # 만 18세 이하인 경우 가입 불가
        if age < 18:
            flash('만 18세 이상만 회원가입이 가능합니다.', 'error')
            return render_template('signup.html')

        if manager.register_pending_member(userid, username, password, email, birthday, gender):
            flash('회원가입 신청이 완료되었습니다. 관리자의 승인을 기다려 주세요.', 'success')
            return redirect(url_for('index'))
        flash('회원가입에 실패했습니다.', 'error')
        return redirect(url_for('register'))
    return render_template('signup.html')


## 로그인 정보 가져오기
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        
        # 사용자 정보 확인
        user = manager.get_member_by_id(userid)  # DB에서 사용자 정보를 가져옴

        if user:  # user가 None이 아닐 경우에만 진행
            if userid and password:
                if user['status'] == 'approved':  # 승인된 사용자만 로그인 가능
                    if user['password'] == password:  # 아이디와 비밀번호가 일치하면
                        session['user'] = userid  # 세션에 사용자 아이디 저장
                        session['role'] = user['role']  # 세션에 역할(role) 저장
                        session['username'] = user['username']  # 세션에 이름(username) 저장
                        if session['role'] == 'admin':
                            manager.update_last_login(userid) #로그인 성공 후 마지막 로그인 갱신
                            return redirect(url_for('admin_dashboard'))  # 관리자는 관리자 대시보드로
                        elif session['role'] == 'dormant_member':
                            return redirect(url_for('dormant_member_dashboard'))
                        else:
                            manager.update_last_login(userid) #로그인 성공 후 마지막 로그인 갱신
                            return redirect(url_for('dashboard'))  # 일반 사용자는 대시보드로
                    else:
                        flash('아이디 또는 비밀번호가 일치하지 않습니다.', 'error')  # 로그인 실패 시 메시지
                        return redirect(url_for('login'))  # 로그인 폼 다시 렌더링
                else:  # 승인되지 않은 사용자
                    flash('관리자의 가입승인이 필요합니다.', 'warning')  # 가입 승인 대기 중 메시지
                    return redirect(url_for('login'))  # 로그인 폼 다시 렌더링
            else:
                flash("아이디와 비밀번호를 모두 입력해 주세요.", 'error')
                return redirect(url_for('login'))  # 로그인 폼 다시 렌더링
        else:  # 존재하지 않는 사용자
            flash("존재하지 않는 아이디입니다.", 'error')
            return redirect(url_for('login'))  # 로그인 폼 다시 렌더링

    return render_template('login.html')  # GET 요청 시 로그인 폼 보여주기


@app.route('/road')
def road():
    search_query = request.args.get("search_query", "")  # 변경: search -> search_query
    search_type = request.args.get("search_type", "all")  # 유지
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = DBManager()
    conn = db.connect()
    if conn is None:
        return "데이터베이스 연결에 실패했습니다."

    cursor = conn.cursor(dictionary=True)
    
    # 검색 타입에 따른 SQL 쿼리 동적 생성
    if search_type == "street_light_id":
        sql = """
        SELECT * FROM road_cctv 
        WHERE street_light_id LIKE %s 
        LIMIT %s OFFSET %s
        """
        count_sql = """
        SELECT COUNT(*) AS total FROM road_cctv 
        WHERE street_light_id LIKE %s
        """
        params = (f"%{search_query}%", per_page, offset)
        count_params = (f"%{search_query}%",)
    elif search_type == "street_light_location":
        sql = """
        SELECT * FROM road_cctv 
        WHERE street_light_location LIKE %s 
        LIMIT %s OFFSET %s
        """
        count_sql = """
        SELECT COUNT(*) AS total FROM road_cctv 
        WHERE street_light_location LIKE %s
        """
        params = (f"%{search_query}%", per_page, offset)
        count_params = (f"%{search_query}%",)
    else:  # all 또는 기본값
        sql = """
        SELECT * FROM road_cctv 
        WHERE street_light_location LIKE %s OR street_light_id LIKE %s 
        LIMIT %s OFFSET %s
        """
        count_sql = """
        SELECT COUNT(*) AS total FROM road_cctv 
        WHERE street_light_location LIKE %s OR street_light_id LIKE %s
        """
        params = (f"%{search_query}%", f"%{search_query}%", per_page, offset)
        count_params = (f"%{search_query}%", f"%{search_query}%")

    # 쿼리 실행
    cursor.execute(sql, params)
    posts = cursor.fetchall()

    # 전체 게시물 수 카운트
    cursor.execute(count_sql, count_params)
    total_posts = cursor.fetchone()["total"]

    # 페이지네이션 계산
    total_pages = (total_posts + per_page - 1) // per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    db.disconnect()

    return render_template(
        "road.html", 
        posts=posts, 
        search_query=search_query, 
        search_type=search_type,
        page=page,
        total_posts=total_posts, 
        per_page=per_page, 
        total_pages=total_pages,
        prev_page=prev_page, 
        next_page=next_page
    )


# 인도용 CCTV 목록 페이지 (/india)
@app.route('/india')
def india():
    search_query = request.args.get("search_query", "")  # 변경: search -> search_query
    search_type = request.args.get("search_type", "all")  # 검색 타입 추가
    page = request.args.get("page", 1, type=int)  # 현재 페이지
    per_page = 10  # 한 페이지당 10개
    offset = (page - 1) * per_page  # 시작 오프셋

    db = DBManager()
    conn = db.connect()
    if conn is None:
        return "데이터베이스 연결에 실패했습니다."

    cursor = conn.cursor(dictionary=True)
    
    # 검색 타입에 따른 SQL 쿼리 동적 생성
    if search_type == "street_light_id":
        sql = """
        SELECT * FROM india_cctv 
        WHERE street_light_id LIKE %s 
        LIMIT %s OFFSET %s
        """
        count_sql = """
        SELECT COUNT(*) AS total FROM india_cctv 
        WHERE street_light_id LIKE %s
        """
        params = (f"%{search_query}%", per_page, offset)
        count_params = (f"%{search_query}%",)
    elif search_type == "street_light_location":
        sql = """
        SELECT * FROM india_cctv 
        WHERE street_light_location LIKE %s 
        LIMIT %s OFFSET %s
        """
        count_sql = """
        SELECT COUNT(*) AS total FROM india_cctv 
        WHERE street_light_location LIKE %s
        """
        params = (f"%{search_query}%", per_page, offset)
        count_params = (f"%{search_query}%",)
    else:  # all 또는 기본값
        sql = """
        SELECT * FROM india_cctv 
        WHERE street_light_location LIKE %s OR street_light_id LIKE %s 
        LIMIT %s OFFSET %s
        """
        count_sql = """
        SELECT COUNT(*) AS total FROM india_cctv 
        WHERE street_light_location LIKE %s OR street_light_id LIKE %s
        """
        params = (f"%{search_query}%", f"%{search_query}%", per_page, offset)
        count_params = (f"%{search_query}%", f"%{search_query}%")

    # 쿼리 실행
    cursor.execute(sql, params)
    posts = cursor.fetchall()

    # 전체 게시물 수 카운트
    cursor.execute(count_sql, count_params)
    total_posts = cursor.fetchone()["total"]

    # 페이지네이션 계산
    total_pages = (total_posts + per_page - 1) // per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    db.disconnect()

    return render_template(
        "india.html", 
        posts=posts, 
        search_query=search_query, 
        search_type=search_type,
        page=page,
        total_posts=total_posts, 
        per_page=per_page, 
        total_pages=total_pages,
        prev_page=prev_page, 
        next_page=next_page
    )


# 게시물 상세보기 (하나의 view_post 엔드포인트만 정의)
@app.route('/view_post/<post_id>')
def view_post(post_id):
    return render_template('view_post.html', post_id=post_id)

@app.route('/view_cctv/<post_id>')
def view_cctv(post_id):
    return render_template('view_cctv.html', post_id=post_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)