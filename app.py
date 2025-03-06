from flask import Flask, session, url_for, render_template, flash, send_from_directory, jsonify ,request, redirect
import os
import requests
from datetime import datetime, timedelta
from functools import wraps
from models import DBManager
import json
import re

app = Flask(__name__)

app.secret_key = 'your-secret-key'  # 비밀 키 설정,

manager = DBManager()


# 파일 업로드 경로 설정
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
# 업로드 폴더가 없으면 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


### 홈페이지
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/some_protected_page')
def some_protected_page():
    if not session.get('userid'):  # 로그인되지 않은 상태라면
        flash('로그인 해주세요!', 'warning')  # 플래시 메시지 추가
        return redirect(url_for('login'))  # 로그인 페이지로 리디렉션
    # 로그인된 사용자라면, 해당 페이지를 보여줌
    return render_template('some_protected_page.html')


# 회원가입
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        userid = request.form['userid']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender = request.form['gender']
        email = request.form['email']
        birthday = request.form['birthday']
        reg_number = request.form['total_regnumber']
        #암호가 일치하는지 확인
        if password != confirm_password:
            flash('암호가 일치하지 않습니다', 'error')
            return render_template('register.html')
        #암호에 숫자가 2개이상 있는지 확인
        if len(re.findall(r'\d', password)) < 2:
            flash('비밀번호는 숫자 2개 이상 포함해야 합니다.', 'error')
            return render_template('register.html')
        #암호에 특수문자가 1개이상 있는지 확인
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('비밀번호는 특수문자 1개 이상 포함해야 합니다.', 'error')
            return render_template('register.html')
        #회원과 아이디가 중복되는지 확인
        if manager.duplicate_users(userid):
            flash('이미 존재하는 아이디 입니다.', 'error')
            return render_template('register.html')
        
        #회원 이메일과 중복여부
        if manager.duplicate_email(email):
            flash('이미 등록된 이메일 입니다.', 'error')
            return render_template('register.html')
        
        # 생년월일이 올바른 날짜 형식인지 확인
        try:
            # 'YYYY-MM-DD' 형식으로 변환
            birthday = datetime.strptime(birthday, "%Y-%m-%d")
        except ValueError:
            flash('잘못된 날짜 형식입니다. 생년월일을 다시 확인해주세요.', 'error')
            return render_template('register.html')

        # 나이 계산 (현재 날짜와 비교)
        today = datetime.today()
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

        # 만 18세 이하인 경우 가입 불가
        if age < 18:
            flash('만 18세 이상만 회원가입이 가능합니다.', 'error')
            return render_template('register.html')

        if manager.register_users(userid, username, password, email, birthday, reg_number, gender):
            flash('회원가입 신청이 완료되었습니다.', 'success')
            return redirect(url_for('index'))
        
        flash('회원가입에 실패했습니다.', 'error')
        return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form['userid']
        password = request.form['password']
        
        # 사용자 정보 확인
        user = manager.get_user_by_id(id)  # DB에서 사용자 정보를 가져옴
        admin = manager.get_admin_by_id(id) # DB에서 관리자 정보를 가져옴 

        if user:  # user가 None이 아닐 경우에만 진행
            if id and password:
                if user['password'] == password:  # 아이디와 비밀번호가 일치하면
                    session['userid'] = id  # 세션에 사용자 아이디 저장
                    session['username'] = user['username']  # 세션에 이름(username) 저장
                    manager.update_last_login(id) #로그인 성공 후 마지막 로그인 갱신
                    if user['security_status'] == 1:  # 승인된 사용자만 로그인 가능
                        flash('비밀번호 변경일이 90일 지났습니다. 비밀번호 변경을 권장합니다!', 'warning')  # 비밀번호 변경 권장 알림
                    if user['status'] == 'user' : #일반회원일경우
                        # 여기를 수정 - userid 파라미터 제거
                        return redirect(url_for('user_dashboard')) # 회원 페이지로 이동
                    else :
                        return render_template('delete_user.html', userid=session['userid']) # 탈퇴한 계정
                else:
                    flash('아이디 또는 비밀번호가 일치하지 않습니다.', 'error')  # 로그인 실패 시 메시지
                    return redirect(url_for('login'))  # 로그인 폼 다시 렌더링          
            else:
                flash("아이디와 비밀번호를 모두 입력해 주세요.", 'error') # 아이디나 비밀번호를 입력하지 않았을 경우
                return redirect(url_for('login'))  # 로그인 폼 다시 렌더링
        elif admin:
            if id and password: 
                if admin['password'] == password: #아이디와 비밀번호가 일치하면
                    session['adminid'] = id #세션에 관리자 아이디 저장
                    session['adminname'] = admin['adminname'] #세션에 관리자이름 저장
                    manager.update_admin_last_login(id) # 로그인 성공 후 관리자 마지막 로그인 갱신
                    print(session['adminid'])
                    return redirect(url_for('admin_dashboard')) #관리자 페이지로 이동
        else:  # 존재하지 않는 사용자
            flash("존재하지 않는 아이디입니다.", 'error')
            return redirect(url_for('login'))  # 로그인 폼 다시 렌더링

    return render_template('login.html')  # GET 요청 시 로그인 폼 보여주기

### 로그인 기능
## 로그인 필수 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'userid' not in session:  # 'userid'가 세션에 없다면
            flash('로그인 후 이용 가능합니다.', 'warning')  
            return redirect('/login')  # 로그인 페이지로 리디렉션
        return f(*args, **kwargs)
    return decorated_function

## 관리자 권한 필수 데코레이터
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'adminid' not in session:  # 'adminid'가 세션에 없다면
            return redirect('/login')  # 로그인 페이지로 리디렉션
        
        # 관리자 정보 확인
        admin = manager.get_admin_by_id(session['adminid'])  # 세션의 관리자 ID로 확인
        if not admin:  # 관리자가 아니면
            return "접근 권한이 없습니다", 403  # 관리자만 접근 가능
        
        return f(*args, **kwargs)
    return decorated_function

# 이용약관 페이지
@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms_of_service.html')

# 개인정보 처리방침
@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')


#탈퇴회원 페이지
@app.route('/delete_user')
def delete_user():
    return render_template('delete_user.html')


## 로그아웃 라우트
@app.route('/logout')
def logout():
    # session.pop('user', None)  # 세션에서 사용자 정보 제거
    # session.pop('role', None)  # 세션에서 역할 정보 제거
    session.clear()
    return redirect('/')  # 로그아웃 후 로그인 페이지로 리디렉션

### 관리자 페이지
@app.route('/admin_dashboard')
@admin_required  # 관리자만 접근 가능
def admin_dashboard():
    adminid = session['adminid']
    admin = manager.get_admin_by_id(adminid)
    return render_template('admin_dashboard.html', admin=admin)  # 관리자 대시보드 렌더링


### 회원 페이지
##로그인 후 회원페이지
@app.route('/dashboard')
@login_required  # 로그인된 사용자만 접근 가능
def user_dashboard():
    print("현재 세션 상태:", session)
    userid = session['userid']
    user = manager.get_user_by_id(userid)
    return render_template('user_dashboard.html', user=user )


@app.route('/road')
def road():
    search_query = request.args.get("search_query", "")  # 변경: search -> search_query
    search_type = request.args.get("search_type", "all")  # 유지
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = DBManager()
    connect = db.connect()
    if connect is None:
        return "데이터베이스 연결에 실패했습니다."

    cursor = connect.cursor(dictionary=True)
    
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
    connect = db.connect()
    if connect is None:
        return "데이터베이스 연결에 실패했습니다."

    cursor = connect.cursor(dictionary=True)
    
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