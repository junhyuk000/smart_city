# C:\Users\facec\Desktop\smart_city\app.py
from flask import Flask, session, url_for, render_template, flash, before_render_template, send_from_directory, jsonify, request, redirect, Response
import os
import requests
from datetime import datetime, timedelta
from functools import wraps
from models import DBManager
from markupsafe import Markup
import json
import re
# import threading
# import license_plate
# import cv2
# import motorcycle

from api import handle_request  # api.py에서 handle_request 함수 불러오기
## sy branch
app = Flask(__name__)



app.secret_key = 'your-secret-key'  # 비밀 키 설정, 실제 애플리케이션에서는 더 안전한 방법으로 설정해야 함if __name__ == '__main__':
road_url = "http://10.0.66.14:5000/stream"
manager = DBManager()

# led센서 테스트
# @app.route('/test')
# def test():
#     return render_template('ledtest.html')

# led센서 테스트2
# @app.route('/led_control', methods=['GET'])
# def control_led():
#     command = request.args.get('command')
#     if command:
#         # 여기에서 MIT 인벤터에 명령을 전달하는 코드 필요
#         print(f"Received command: {command}")
#         return "Command Received"
#     return "No Command", 400


# 파일 업로드 경로 설정
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
# 업로드 폴더가 없으면 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Flask서버 실행시 보안상태 업데이트
@app.before_request
def update_security_status_on_start():
    if not hasattr(app, "has_run"):
        manager.user_update_security_status()
        app.has_run = True  # 실행 여부 저장

# 전역 변수로 데이터 저장
received_data = {"message": "No data received"}

@app.route('/api', methods=['GET', 'POST'])
def handle_request():
    global received_data

    if request.method == "POST":
        if request.is_json:
            received_data = request.get_json()
            return jsonify({"status": "success", "message": "JSON data received", "data": received_data})

        if not request.form:
            return jsonify({"status": "error", "message": "No data received"}), 400

        raw_data_list = list(request.form.keys())
        if not raw_data_list:
            return jsonify({"status": "error", "message": "Empty form data"}), 400

        raw_data = raw_data_list[0]
        data_dict = {}

        pairs = raw_data.split("|")
        for pair in pairs:
            key_value = pair.strip().split(":")
            if len(key_value) == 2:
                key, value = key_value[0].strip(), key_value[1].strip()
                data_dict[key] = value

        received_data = data_dict
        print(f"📩 변환된 데이터: {received_data}")  # 터미널에서 확인
        manager.save_sensor_data(received_data)

        return jsonify(received_data)

    # GET 요청 시 현재 데이터를 반환
    return jsonify(received_data)

# 아두이노 LED on/off 제어
command_cache = {
    "arduino1": {"target": "arduino1", "cmd": None},
    "arduino2": {"target": "arduino2", "cmd": None}
}

@app.route('/LedControl')
def LedControl():
    """웹 페이지에서 현재 명령을 확인하는 HTML 페이지 렌더링"""
    return render_template("api/LedControl.html", command_cache=command_cache)

@app.route('/command', methods=['GET'])
def command():
    """
    아두이노 또는 앱 인벤터에서 현재 명령을 가져가는 엔드포인트.
    아두이노가 한 번 요청하면 이후 값이 None으로 초기화됨.
    예: http://<server-ip>:5010/command?target=arduino1
    """
    target = request.args.get('target')
    
    if target not in command_cache:
        return jsonify({"status": "error", "message": "Invalid target"}), 400

    response = jsonify(command_cache[target])

    # **아두이노가 가져간 후 명령 초기화 (중복 방지)**
    command_cache[target]["cmd"] = None

    return response

@app.route('/set_command', methods=['GET'])
def set_command():
    """
    웹에서 명령을 설정하는 엔드포인트.
    예: http://<server-ip>:5010/set_command?target=arduino1&cmd=LED_ON
    """
    target = request.args.get('target')
    cmd = request.args.get('cmd')

    if target not in command_cache:
        return jsonify({"status": "error", "message": "Invalid target"}), 400

    # 웹 명령을 `_WEB` 접미어 추가하여 처리
    if cmd in ["LED_ON", "LED_OFF", "AUTO_MODE"]:
        cmd = f"{cmd}_WEB"

    # 기존 명령과 동일하면 다시 보내지 않음 (중복 방지)
    if command_cache[target]["cmd"] == cmd:
        return jsonify({"status": "no_change", "command": cmd})

    # 새로운 명령 저장
    command_cache[target]["cmd"] = cmd
    return jsonify({"status": "ok", "command": cmd})



### 홈페이지
@app.route('/')
def index():
    return render_template('public/index.html')

### 소개 페이지 (로그인 없이 접속 가능)
@app.route('/about')
def about():
    return render_template('user/about.html')

### 회원가입 페이지등록 
#회원가입
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['username']
        user_id = request.form['userid']
        password = request.form['password']
        address= request.form['address']
        gender = request.form['gender']
        email = request.form['email']
        birthday = request.form['birthday']
        reg_number = request.form['total_regnumber']
        
        #회원과 아이디가 중복되는지 확인
        if manager.duplicate_users(user_id):
            flash('이미 존재하는 아이디 입니다.', 'error')
            return render_template('public/register.html')
        
        #회원 이메일과 중복여부
        if manager.duplicate_email(email):
            flash('이미 등록된 이메일 입니다.', 'error')
            return render_template('public/register.html')
        
        if manager.duplicate_reg_number(reg_number):
            flash('이미 등록된 주민번호 입니다.', 'error')
            return render_template('public/register.html')


        if manager.register_users(user_id, user_name, password, email, address, birthday, reg_number, gender):
            flash('회원가입 신청이 완료되었습니다.', 'success')
            return redirect(url_for('index'))
        
        flash('회원가입에 실패했습니다.', 'error')
        return redirect(url_for('register'))
    return render_template('public/register.html')

# 이용약관 페이지
@app.route('/register/terms_of_service')
def terms_of_service():
    return render_template('public/terms_of_service.html')

# 개인정보 처리방침
@app.route('/register/privacy_policy')
def privacy_policy():
    return render_template('public/privacy_policy.html')


### 로그인 기능
## 로그인 필수 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'admin_id' not in session :  # 'user_id' 또는 'admin_id'가 세션에 없다면
            return redirect('/login')  # 로그인 페이지로 리디렉션
        return f(*args, **kwargs)
    return decorated_function

## 관리자 권한 필수 데코레이터
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:  # 'adminid'가 세션에 없다면
            return redirect('/login')  # 로그인 페이지로 리디렉션
        
        # 관리자 정보 확인
        admin = manager.get_admin_by_id(session['admin_id'])  # 세션의 관리자 ID로 확인
        if not admin:  # 관리자가 아니면
            return "접근 권한이 없습니다", 403  # 관리자만 접근 가능
        
        return f(*args, **kwargs)
    return decorated_function

### 로그인 정보 가져오기
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form['userid']
        password = request.form['password']
        
        # 사용자 정보 확인
        user = manager.get_user_by_info(id)  # DB에서 사용자 정보를 가져옴
        admin = manager.get_admin_by_info(id) # DB에서 관리자 정보를 가져옴 

        if user:  # user가 None이 아닐 경우에만 진행
            if id and password:
                if user['password'] == password:  # 아이디와 비밀번호가 일치하면
                    session['user_id'] = id  # 세션에 사용자 아이디 저장
                    session['user_name'] = user['user_name']  # 세션에 이름(username) 저장
                    manager.update_last_login(id) #로그인 성공 후 마지막 로그인 갱신
                    if user['status'] == 'user' : #일반회원일경우
                        if user['security_status'] == 1 : #보안이 위험일때 경고알림
                            message = Markup('암호를 변경한지 90일 지났습니다.<br>암호를 변경하시길 권장합니다.')#Markup과 <br>태그로 flash메세지 줄나눔
                            flash(message, 'warning')
                        return redirect(url_for('user_dashboard')) # 회원 페이지로 이동
                    else :
                        session.clear() # 세션을 초기화
                        flash('회원 탈퇴된 계정입니다. 관리자 이메일로 문의하세요', 'error')
                        return redirect('login') # 탈퇴한 계정
                else:
                    flash('아이디 또는 비밀번호가 일치하지 않습니다.', 'error')  # 로그인 실패 시 메시지
                    return redirect(url_for('login'))  # 로그인 폼 다시 렌더링          
                
        elif admin:
            if id and password: 
                if admin['password'] == password: #아이디와 비밀번호가 일치하면
                    session['admin_id'] = id #세션에 관리자 아이디 저장
                    session['admin_name'] = admin['admin_name'] #세션에 관리자이름 저장
                    manager.update_admin_last_login(id) # 로그인 성공 후 관리자 마지막 로그인 갱신
                    return redirect(url_for('admin_dashboard')) #관리자 페이지로 이동
                else: 
                    flash('아이디 또는 비밀번호가 일치하지 않습니다.', 'error')  # 로그인 실패 시 메시지
                    return redirect(url_for('login'))  # 로그인 폼 다시 렌더링 
                
        else:  # 존재하지 않는 사용자
            flash("존재하지 않는 아이디입니다.", 'error')
            return redirect(url_for('login'))  # 로그인 폼 다시 렌더링

    return render_template('public/login.html')  # GET 요청 시 로그인 폼 보여주기

@app.route('/need_login')
def need_login():
    flash('로그인이 필요합니다. 로그인해주세요', 'error')
    return redirect(url_for('login'))

### 회원 페이지
##로그인 후 회원페이지
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    # 현재 로그인한 사용자 정보 가져오기
    user_id = session.get('user_id')
    user = manager.get_user_by_info(user_id)
    
    # user 객체를 템플릿에 전달
    return render_template('user/dashboard.html', user=user)

##회원 정보 수정 
@app.route('/user/dashboard/update_profile', methods=['GET', 'POST'])
@login_required
def user_update_profile():
    userid = session['user_id']  # 세션에서 사용자 아이디 가져오기
    user = manager.get_user_by_info(userid)  # 회원 정보 가져오기

    if request.method == 'POST':
        print(userid)
        # 폼에서 입력한 값 받아오기
        email = request.form['email'] if request.form['email'] else user.email
        password = request.form['password'] if request.form['password'] else None
        confirm_password = request.form['confirm_password'] if request.form['confirm_password'] else None
        address = request.form['address'] if request.form['address'] else user.address
        username = request.form['username'] if request.form['username'] else user.user_name

        password_change = False  # 비밀번호 변경 여부
        # 비밀번호가 입력되었으면 확인
        if password:
            if password != confirm_password:
                flash('비밀번호와 비밀번호 확인이 일치하지 않습니다.', 'error')
                return redirect(request.url)  # 현재 페이지로 리디렉션

            # 비밀번호 강도 체크 추가 (필요시)
            # 예시: 비밀번호 길이, 숫자 포함 여부 등
           
            if password == user['password'] : 
                flash('현재 비밀번호와 동일한 비밀번호로 변경할 수 없습니다.', 'warning')
                return redirect(request.url) #현재 페이지로 리디렉션
            # 비밀번호 업데이트
            else:
                password_change = True  # 비밀번호 변경 여부 True로 설정
                manager.update_user_password(userid, password)
                session.clear()
                flash('비밀번호를 변경하였습니다', 'success')
                return redirect(url_for('login'))  # 로그인 페이지로 리디렉션
            
        if email == user['email'] and address == user['address'] and username == user['user_name'] :
            if password_change :
                manager.update_user_info(userid, username, email, address)
                session['user_name'] = username
                flash('회원 정보가 성공적으로 수정되었습니다.', 'success')
                return redirect(url_for('user_dashboard'))
            else:
                flash('수정된 정보가 없습니다.', 'warning')
                return redirect(request.url)
        else:
            manager.update_user_info(userid, username, email, address)
            session['user_name'] = username
            flash('회원 정보가 성공적으로 수정되었습니다.', 'success')
            return redirect(url_for('user_dashboard'))

    return render_template('user/update_profile.html', user=user)

##로그인 후 소개페이지
@app.route('/user/dashboard/about')
@login_required
def user_dashboard_about():
    return render_template('user/about.html')

##회원 페이지 CCTV보기
#로그인 후 도로CCTV 페이지
@app.route('/user/dashboard/road', methods=['GET'])
@login_required
def user_dashboard_road_cctv():
    search_query = request.args.get("search_query", "").strip()
    search_type = request.args.get("search_type", "all")  # 기본값은 'all'
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # search_type이 'all'이면 search_query를 빈 문자열로 설정
    if search_type == "all":
        search_query = ""

    # SQL 쿼리 및 파라미터 가져오기
    sql, values = manager.get_road_cctv_query(search_query, search_type, per_page, offset)
    count_sql, count_values = manager.get_road_cctv_count_query(search_query, search_type)

    # 검색된 가로등 목록 가져오기
    street_lights = manager.execute_query(sql, values)
    # 전체 CCTV 개수 카운트
    total_posts = manager.execute_count_query(count_sql, count_values)

    # 페이지네이션 계산
    total_pages = (total_posts + per_page - 1) // per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    return render_template(
        "user/road_cctv.html",
        street_lights=street_lights,
        search_query=search_query,
        search_type=search_type,
        page=page,
        total_posts=total_posts,
        per_page=per_page,
        total_pages=total_pages,
        prev_page=prev_page,
        next_page=next_page,
    )

#로그인 후 인도CCTV 페이지
@app.route('/user/dashboard/sidewalk', methods=['GET'])
@login_required
def user_dashboard_sidewalk_cctv():
    search_query = request.args.get("search_query", "").strip()
    search_type = request.args.get("search_type", "all")  # 기본값은 'all'
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    if search_type == "all":
        search_query = ""
    # SQL 쿼리 및 파라미터 가져오기
    sql, values = manager.get_sidewalk_cctv_query(search_query, search_type, per_page, offset)
    count_sql, count_values = manager.get_sidewalk_cctv_count_query(search_query, search_type)

    # 검색된 가로등 목록 가져오기
    street_lights = manager.execute_query(sql, values)

    # 전체 CCTV 개수 카운트
    total_posts = manager.execute_count_query(count_sql, count_values)

    # 페이지네이션 계산
    total_pages = (total_posts + per_page - 1) // per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    return render_template(
        "user/sidewalk_cctv.html",
        street_lights=street_lights,
        search_query=search_query,
        search_type=search_type,
        page=page,
        total_posts=total_posts,
        per_page=per_page,
        total_pages=total_pages,
        prev_page=prev_page,
        next_page=next_page,
    )

#회원용 CCTV 상세 보기
@app.route('/user_dashboard/cctv/<int:street_light_id>')
@login_required
def user_dashboard_cctv(street_light_id):
    camera = manager.get_camera_by_info(street_light_id)
    return render_template('user/view_cctv.html', camera=camera)


#회원용 문의하기
@app.route('/user/inquiries', methods=['GET','POST'])
@login_required
def user_dashboard_inquiries():
    userid = session['user_id']
    if request.method == 'GET':
        return render_template("user/inquiries.html")
    
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename if file else None
        # 파일이 있으면 저장
        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        inquiry_reason = request.form['inquiry_type']
        detail_reason = request.form.get('message')
        manager.add_inquire_user(userid, filename, inquiry_reason, detail_reason)
        flash("문의하기가 관리자에게 전달되었습니다.", 'success')
        return redirect(url_for('user_dashboard'))
    
#회원 문의된 정보 보기
@app.route('/user/inquiries_view', methods=['GET','POST'])
@login_required
def user_dashboard_inquiries_view():
    if request.method == 'GET':
        posts = manager.get_posts_info()
        return render_template('user/inquiries_view.html', posts=posts)
    
    if request.method == 'POST':
        inquiries_id = request.form.get('inquiries_id')
        posts = manager.get_inquiry_by_info(inquiries_id)
        return render_template('user/inquiry_detail.html', posts=posts)


#회원탈퇴
@app.route('/user_dashboard/delete_user', methods=['GET','POST'])
@login_required
def user_dashboard_delete_user():
    userid = session['user_id']
    if request.method == 'GET':
        user = manager.get_user_by_id(userid)
        return render_template('user/delete_page.html', user =user)
    
    if request.method == 'POST':
        user = manager.get_user_by_id(userid)
        reason = request.form['reason']
        detail_reason = request.form['detail_reason']
        manager.update_user_status(userid)
        manager.save_deleted_user(userid, reason, detail_reason)
        flash("회원탈퇴가 완료되었습니다.", 'success')
        return redirect(url_for('index'))
    
#탈퇴회원 로그인 후 dashboard페이지
@app.route('/delete_user_dashboard')
@login_required
def delete_user():
    return render_template('delete_user_dashboard.html')

#아이디/비밀번호찾기
@app.route('/index/search_account', methods=['GET', 'POST'])
def search_account():
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        username = request.form.get('username')
        regnumber = request.form.get('regnumber')
        userid = None  # 기본값 설정

        if search_type == "id":
            userid = manager.get_user_id_by_name_regnumber(username, regnumber)
            return render_template('public/search_account.html', userid=userid, search_type=search_type )

        elif search_type == "password":
            userid = request.form.get('userid')
            password_data = manager.get_user_password_by_id_name_regnumber(userid, username, regnumber)
            password = None  # 기본값 설정

            if password_data: 
                raw_password = password_data['password']  # 딕셔너리에서 비밀번호 값 가져오기
                password = raw_password[:4] + '*' * (len(raw_password) - 4)  # 앞 4자리만 표시, 나머지는 '*'
            return render_template('public/search_account.html', password = password, userid=userid, search_type=search_type)
    return render_template('public/search_account.html')

#계정찾기 이후 새비밀번호 업데이트
@app.route('/index/search_account/edit_password/<userid>', methods=['GET','POST'])
def edit_password(userid):
    user = manager.get_user_by_info(userid)
    if request.method == 'POST': 
        password = request.form['new_password']
        success = manager.update_user_password(userid, password)
        return jsonify({"success": success})
    return render_template('public/edit_password.html', user=user)
    

## 로그아웃 라우트
@app.route('/logout')
def logout():
    # session.pop('user', None)  # 세션에서 사용자 정보 제거
    # session.pop('role', None)  # 세션에서 역할 정보 제거
    session.clear()
    return redirect('/')  # 로그아웃 후 로그인 페이지로 리디렉션



### 관리자 페이지
## HOME
@app.route('/admin_dashboard')
@admin_required  # 관리자만 접근 가능
def admin_dashboard():
    return render_template('admin/dashboard.html')  # 관리자 대시보드 렌더링


# CCTV보기
# 도로용 CCTV 목록 보기(관리자)
@app.route('/admin/road_cctv', methods=['GET'])
@admin_required
def admin_road_cctv():
    search_query = request.args.get("search_query", "").strip()
    search_type = request.args.get("search_type", "all")  # 기본값은 'all'
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # search_type이 'all'이면 search_query를 빈 문자열로 설정
    if search_type == "all":
        search_query = ""

    # SQL 쿼리 및 파라미터 가져오기
    sql, values = manager.get_road_cctv_query(search_query, search_type, per_page, offset)
    count_sql, count_values = manager.get_road_cctv_count_query(search_query, search_type)

    # 검색된 가로등 목록 가져오기
    street_lights = manager.execute_query(sql, values)
    # 전체 CCTV 개수 카운트
    total_posts = manager.execute_count_query(count_sql, count_values)

    # 페이지네이션 계산
    total_pages = (total_posts + per_page - 1) // per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    return render_template(
        "admin/road_cctv.html",
        street_lights=street_lights,
        search_query=search_query,
        search_type=search_type,
        page=page,
        total_posts=total_posts,
        per_page=per_page,
        total_pages=total_pages,
        prev_page=prev_page,
        next_page=next_page,
    )
    
# 인도용 CCTV 목록 보기(관리자)
@app.route('/admin/sidewalk_cctv', methods=['GET'])
@admin_required
def admin_sidewalk_cctv():
    search_query = request.args.get("search_query", "").strip()
    search_type = request.args.get("search_type", "all")  # 기본값은 'all'
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    if search_type == "all":
        search_query = ""
    # SQL 쿼리 및 파라미터 가져오기
    sql, values = manager.get_sidewalk_cctv_query(search_query, search_type, per_page, offset)
    count_sql, count_values = manager.get_sidewalk_cctv_count_query(search_query, search_type)

    # 검색된 가로등 목록 가져오기
    street_lights = manager.execute_query(sql, values)

    # 전체 CCTV 개수 카운트
    total_posts = manager.execute_count_query(count_sql, count_values)

    # 페이지네이션 계산
    total_pages = (total_posts + per_page - 1) // per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    return render_template(
        "admin/sidewalk_cctv.html",
        street_lights=street_lights,
        search_query=search_query,
        search_type=search_type,
        page=page,
        total_posts=total_posts,
        per_page=per_page,
        total_pages=total_pages,
        prev_page=prev_page,
        next_page=next_page,
    )

# 관리자 CCTV상세보기
# @app.route('/admin/cctv/<int:street_light_id>')
# @admin_required
# def admin_dashboard_cctv(street_light_id):
#     camera = manager.get_camera_by_info(street_light_id)
#     # sensor = sidewalk_sensor
#     return render_template('view_cctv.html', camera=camera)

## 가로등
# 전체 가로등 조회
@app.route('/admin/lamp_cctv', methods=['GET'])
@admin_required
def admin_lamp_check():
    page = request.args.get("page", 1, type=int)
    search_type = request.args.get("search_type", "all")
    search_query = request.args.get("search_query", "").strip()
    per_page = 10

    # 매니저에서 데이터 조회
    lamp_cctv, total_posts = manager.get_paginated_lamps(
        per_page=per_page,
        offset=(page-1)*per_page,
        search_type=search_type,
        search_query=search_query
    )

    # 페이지 계산
    total_pages = (total_posts + per_page - 1) // per_page
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)

    return render_template(
        "admin/lamp_check.html",
        lamp_cctv=lamp_cctv,
        page=page,
        total_posts=total_posts,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page,
        search_type=search_type,
        search_query=search_query
    )

# 고장난 가로등 조회
@app.route('/admin/broken_light', methods=['GET'])
@admin_required
def admin_broken_light_check():
    # 데이터베이스 연결
    manager.connect()
    
    try:
        page = request.args.get("page", 1, type=int)
        search_type = request.args.get("search_type", "all")
        search_query = request.args.get("search_query", "").strip()
        per_page = 10
        
        # 페이지 첫 진입 시 기본값 설정
        if not search_type and not search_query:
            search_type = "all"
            search_query = ""
        
        # 고장난 가로등 데이터 조회
        lamp_cctv, total_posts = manager.get_malfunctioning_lamps( 
            per_page=per_page,
            offset=(page-1)*per_page,
            search_type=search_type,
            search_query=search_query,
            status='malfunction'  # 고장난 가로등만 필터링
        )
        
        # 페이지 계산
        total_pages = max(1, (total_posts + per_page - 1) // per_page)
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        
        prev_page = page - 1 if page > 1 else None
        next_page = page + 1 if page < total_pages else None
        
        return render_template(
            "admin/broken_light.html",
            lamp_cctv=lamp_cctv,
            page=page,
            total_posts=total_posts,
            total_pages=total_pages,
            start_page=start_page,
            end_page=end_page,
            prev_page=prev_page,
            next_page=next_page,
            search_type=search_type,
            search_query=search_query
        )

    finally:
        # 데이터베이스 연결 해제
        manager.disconnect()
                            


##불법단속
#자동차(도로) 단속 보드
@app.route('/admin/road_car_board', methods=['GET'])
@admin_required
def admin_road_car_board():
    search_query = request.args.get("search_query", "").strip()
    search_type = request.args.get("search_type", "all")  # 기본값은 'all'
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # search_type이 'all'이면 search_query를 빈 문자열로 설정
    if search_type == "all":
        search_query = ""

    # SQL 쿼리 및 파라미터 가져오기
    sql, values = manager.get_road_cctv_query(search_query, search_type, per_page, offset)
    count_sql, count_values = manager.get_road_cctv_count_query(search_query, search_type)

    # 검색된 가로등 목록 가져오기
    street_lights = manager.execute_query(sql, values)
    # 전체 CCTV 개수 카운트
    total_posts = manager.execute_count_query(count_sql, count_values)

    # 페이지네이션 계산
    total_pages = (total_posts + per_page - 1) // per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    return render_template(
        "admin/road_car_board.html",
        street_lights=street_lights,
        search_query=search_query,
        search_type=search_type,
        page=page,
        total_posts=total_posts,
        per_page=per_page,
        total_pages=total_pages,
        prev_page=prev_page,
        next_page=next_page,
    )

#자동차(도로) 단속 카메라
@app.route("/admin/load_car")
@admin_required
def admin_load_car():
    adminid =session.get('admin_id')
    return render_template("admin/road_car.html", stream_url=road_url, adminid=adminid)

#오토바이(인도) 단속 보드
@app.route('/admin/sidewalk_motorcycle_board', methods=['GET'])
@admin_required
def admin_sidewalk_motorcycle_board():
    search_query = request.args.get("search_query", "").strip()
    search_type = request.args.get("search_type", "all")  # 기본값은 'all'
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    if search_type == "all":
        search_query = ""
    # SQL 쿼리 및 파라미터 가져오기
    sql, values = manager.get_sidewalk_cctv_query(search_query, search_type, per_page, offset)
    count_sql, count_values = manager.get_sidewalk_cctv_count_query(search_query, search_type)

    # 검색된 가로등 목록 가져오기
    street_lights = manager.execute_query(sql, values)

    # 전체 CCTV 개수 카운트
    total_posts = manager.execute_count_query(count_sql, count_values)

    # 페이지네이션 계산
    total_pages = (total_posts + per_page - 1) // per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    return render_template(
        "admin/sidewalk_motorcycle_board.html",
        street_lights=street_lights,
        search_query=search_query,
        search_type=search_type,
        page=page,
        total_posts=total_posts,
        per_page=per_page,
        total_pages=total_pages,
        prev_page=prev_page,
        next_page=next_page,
    )



#오토바이(인도) 단속
@app.route("/admin/sidewalk_motorcycle")
@admin_required
def admin_sidewalk_motorcycle():
    adminid = session.get('admin_id')
    return render_template("admin/sidewalk_motorcycle.html", adminid=adminid)


# # YOLO 분석된 영상 스트리밍
# @app.route("/processed_video_feed")
# def processed_video_feed():
#     """YOLOv8로 감지된 영상 스트리밍"""
#     def generate():
#         while True:
#             with license_plate.lock:
#                 if license_plate.frame is None:
#                     continue
#                 img = license_plate.frame.copy()

#             results = license_plate.model(img)
#             for result in results:
#                 boxes = result.boxes.xyxy.cpu().numpy()
#                 for box in boxes:
#                     x1, y1, x2, y2 = map(int, box)
#                     cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             results = license_plate.model(img)
#             for result in results:
#                 boxes = result.boxes.xyxy.cpu().numpy()
#                 for box in boxes:
#                     x1, y1, x2, y2 = map(int, box)
#                     cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

#             _, jpeg = cv2.imencode('.jpg', img)
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
#             _, jpeg = cv2.imencode('.jpg', img)
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

#     return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
#     return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# # OCR 결과 API
# @app.route("/ocr_result", methods=["GET"])
# def get_ocr_result():
#     """OCR 결과 반환 API"""
#     response_data = {"license_plate": license_plate.ocr_result, "alert_message": license_plate.alert_message}

#     if license_plate.alert_message:  # 알람 메시지가 있을 때만 초기화
#         license_plate.alert_message = ""  # 메시지를 한 번만 표시하도록 초기화
#     if license_plate.alert_message:  # 알람 메시지가 있을 때만 초기화
#         license_plate.alert_message = ""  # 메시지를 한 번만 표시하도록 초기화
    
#     return jsonify(response_data)
#     return jsonify(response_data)



# # ✅ ESP32-CAM에서 감지된 오토바이 영상 제공
# @app.route("/video_feed")
# def video_feed():
#     """ESP32-CAM 스트리밍"""
#     return Response(motorcycle.get_video_frame(), mimetype="multipart/x-mixed-replace; boundary=frame")



# # ✅ 오토바이 감지 상태 API
# @app.route("/alert_status", methods=["GET"])
# def alert_status():
#     """오토바이 감지 상태 반환"""
#     return jsonify(motorcycle.get_alert_status())


##관리자 페이지에서 문의정보 보기
#문의된 정보 보기
@app.route('/admin/inquiries_view', methods=['GET'])
@admin_required
def admin_inquiries_view():
    per_page = 10  # 한 페이지당 보여줄 개수
    page = request.args.get('page', 1, type=int)  # 현재 페이지 (기본값 1)
    offset = (page - 1) * per_page  # 오프셋 계산
    search_type = request.args.get('search_type')
    search_query = request.args.get('search_query')

    posts, total = manager.get_paginated_inquiries(per_page, offset, search_type, search_query)

    return render_template(
        'admin/inquiries_view.html',
        posts=posts,
        total=total,
        per_page=per_page,
        current_page=page
    )
        

## 답변상태 변환하기 
@app.route('/update_status_member/<userid>', methods=['POST'])
@admin_required
def update_answer_status(userid):
    enquired_at_str = request.form['enquired_at']
    enquired_at = datetime.strptime(enquired_at_str, '%Y-%m-%d %H:%M:%S')
    manager.update_answer_status(userid,enquired_at)
    if userid != '비회원':
        return redirect(url_for('admin_list_posts_member'))
    else :
        return redirect(url_for('admin_list_posts_nonmember'))

#회원 문의사항 상세정보보기
@app.route('/admin_view_posts_member/<userid>', methods=['POST'])
@admin_required
def admin_view_posts_member(userid):
    enquired_at_str = request.form['enquired_at']
    enquired_at = datetime.strptime(enquired_at_str, '%Y-%m-%d %H:%M:%S')

    # 단일 post 객체를 가져옵니다.
    post = manager.get_enquired_post_by_id(userid, enquired_at)

    # 'posts'로 단일 객체를 전달
    return render_template("admin/view_posts_member.html", posts=post)

# 답변 하기
@app.route('/admin/answer-inquiry', methods=['POST'])
@admin_required
def admin_answer_inquiry():
    try:
        # request.form.get() 대신 request.form[]를 사용하여 필수 필드 확인
        inquiry_id = request.form['inquiry_id']
        user_id = request.form['user_id']  # 필수 필드로 변경
        admin_id = session.get('admin_id')
        
        if not admin_id:
            flash('관리자 세션이 만료되었습니다.', 'error')
            return redirect(url_for('admin_login'))
        
        answer_content = request.form['answer_content']
        answer_time = datetime.now()
        enquired_at = datetime.now()

        db = DBManager()
        db.connect()

        # 기존 답변 확인 및 처리 로직
        db.cursor.execute(
            "SELECT * FROM inquiry_answers WHERE inquiry_id = %s", 
            (inquiry_id,)
        )
        existing_answer = db.cursor.fetchone()

        if existing_answer:
            # 기존 답변 업데이트
            db.cursor.execute("""
                UPDATE inquiry_answers 
                SET answer_content = %s,
                    answer_time = %s,
                    admin_id = %s,
                    enquired_at = %s
                WHERE inquiry_id = %s
            """, (answer_content, answer_time, admin_id, enquired_at, inquiry_id))
        else:
            # 새로운 답변 삽입
            db.cursor.execute("""
                INSERT INTO inquiry_answers 
                (inquiry_id, user_id, admin_id, answer_content, enquired_at, answer_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (inquiry_id, user_id, admin_id, answer_content, enquired_at, answer_time))

        # 문의 상태 업데이트
        db.cursor.execute(
            "UPDATE inquiries SET answer_status = 'completed' WHERE inquiries_id = %s", 
            (inquiry_id,)
        )

        db.connection.commit()
        db.disconnect()

        flash('답변이 성공적으로 저장되었습니다.', 'success')
        return redirect(url_for('admin_inquiries_view'))

    except KeyError as e:
        # 필수 필드 누락 시 처리
        flash(f'필수 데이터가 누락되었습니다: {str(e)}', 'error')
        return redirect(url_for('admin_inquiries_view'))
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        if 'db' in locals():
            db.disconnect()
        flash(f'답변 저장 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_inquiries_view'))

# 답변 수정하기 
@app.route('/admin/update-inquiry-answer', methods=['POST'])
@admin_required
def update_inquiry_answer():
    try:
        inquiry_id = request.form.get('inquiry_id')
        user_id = request.form.get('user_id')  # 추가
        answer_content = request.form.get('answer_content')
        answer_time = datetime.now()
        admin_id = session.get('admin_id')

        db = DBManager()
        db.connect()

        # 기존 답변 확인
        db.cursor.execute(
            "SELECT * FROM inquiry_answers WHERE inquiry_id = %s", 
            (inquiry_id,)
        )
        existing_answer = db.cursor.fetchone()

        if existing_answer:
            # 기존 답변 업데이트
            db.cursor.execute("""
                UPDATE inquiry_answers 
                SET answer_content = %s,
                    answer_time = %s,
                    admin_id = %s
                WHERE inquiry_id = %s
            """, (answer_content, answer_time, admin_id, inquiry_id))
        else:
            # 새로운 답변 삽입
            db.cursor.execute("""
                INSERT INTO inquiry_answers 
                (inquiry_id, user_id, admin_id, answer_content, enquired_at, answer_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (inquiry_id, user_id, admin_id, answer_content, answer_time, answer_time))

        # 문의 상태 업데이트
        db.cursor.execute(
            "UPDATE inquiries SET answer_status = 'completed' WHERE inquiries_id = %s", 
            (inquiry_id,)
        )

        db.connection.commit()
        db.disconnect()

        flash('답변이 성공적으로 저장되었습니다.', 'success')
        return redirect(url_for('admin_inquiries_view'))

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        if 'db' in locals():
            db.disconnect()
        flash('답변 저장 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_inquiries_view'))
    
    try:
        # 테이블 구조에 맞게 컬럼명을 수정합니다.
        query = """
            SELECT inquiries_id, user_id, inquiry_reason, detail_reason, inquiry_time
            FROM inquiries
            WHERE answer_status = 'pending'
        """
        count_query = "SELECT COUNT(*) as total FROM inquiries WHERE answer_status = 'pending'"
        params = []
    
        if search_type and search_query:
            query += f" AND {search_type} LIKE %s"
            count_query += f" AND {search_type} LIKE %s"
            params.append(f"%{search_query}%")
        
        query += " ORDER BY inquiry_time DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
    
        db.cursor.execute(query, tuple(params))
        posts = db.cursor.fetchall()
    
        # 검색 조건이 있을 경우, count_query에 적용할 파라미터는 검색 조건만 사용
        count_params = (params[0],) if (search_type and search_query) else ()
        db.cursor.execute(count_query, count_params)
        total = db.cursor.fetchone()['total']
    
    except Exception as e:
        print("데이터베이스 오류:", e)
        posts = []
        total = 0
    finally:
        db.disconnect()
    
    return render_template(
        'admin/inquiries_pending.html',
        posts=posts,
        total=total,
        per_page=per_page,
        current_page=page
    )

# 문의된 정보 보기 (미답변만)
@app.route('/admin/inquiries_pending', methods=['GET'])
def admin_inquiries_pending():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    per_page = 10  # 한 페이지당 보여줄 개수
    page = request.args.get('page', 1, type=int)  # 현재 페이지 (기본값 1)
    offset = (page - 1) * per_page  # 오프셋 계산
    search_type = request.args.get('search_type')
    search_query = request.args.get('search_query')
    
    db = DBManager()
    db.connect()
    
    try:
        # 테이블 구조에 맞게 컬럼명을 수정합니다.
        query = """
            SELECT inquiries_id, user_id, inquiry_reason, detail_reason, inquiry_time
            FROM inquiries
            WHERE answer_status = 'pending'
        """
        count_query = "SELECT COUNT(*) as total FROM inquiries WHERE answer_status = 'pending'"
        params = []
    
        if search_type and search_query:
            query += f" AND {search_type} LIKE %s"
            count_query += f" AND {search_type} LIKE %s"
            params.append(f"%{search_query}%")
        
        query += " ORDER BY inquiry_time DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
    
        db.cursor.execute(query, tuple(params))
        posts = db.cursor.fetchall()
    
        # 검색 조건이 있을 경우, count_query에 적용할 파라미터는 검색 조건만 사용
        count_params = (params[0],) if (search_type and search_query) else ()
        db.cursor.execute(count_query, count_params)
        total = db.cursor.fetchone()['total']
    
    except Exception as e:
        print("데이터베이스 오류:", e)
        posts = []
        total = 0
    finally:
        db.disconnect()
    
    return render_template(
        'admin/inquiries_pending.html',
        posts=posts,
        total=total,
        per_page=per_page,
        current_page=page
    )
        
#이미지파일 가져오기
@app.route('/capture_file/<filename>')
def capture_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 고장난 가로등 보기
@app.route('/admin/broken_light')
def admin_broken_light():
    return render_template('admin/broken_light.html')

# 설치된 가로등 등록
@app.route('/admin/street_light_register', methods=['GET', 'POST'])
def street_light_register():
    db_manager = DBManager()  # DBManager 인스턴스 생성
    db_manager.connect()  # DB 연결

    if request.method == 'POST':
        try:
            location = request.form.get('location')
            purpose = request.form.get('purpose')
            other_purpose = request.form.get('other_purpose', '').strip()
            tilt_status = request.form.get('tilt_status', 'normal')
            light_status = request.form.get('light_status', 'off')
            installation_date_str = request.form.get('installation_date')

            installation_date = datetime.strptime(installation_date_str, '%Y-%m-%d')

            if purpose == "기타" and other_purpose:
                purpose = f"기타: {other_purpose}"

            cursor = db_manager.cursor  # DB 커서 가져오기

            if cursor:  # 커서가 존재하면 DB 작업
                try:
                    sql = """
                    INSERT INTO street_lights 
                    (location, purpose, installation_date, tilt_status, light_status) 
                    VALUES 
                    (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (location, purpose, installation_date, tilt_status, light_status))
                    db_manager.connection.commit()  # 커밋
                    flash('가로등이 성공적으로 등록되었습니다.', 'success')

                except Exception as e:
                    flash(f'가로등 등록 중 오류가 발생했습니다: {str(e)}', 'error')
                    return redirect(url_for('street_light_register'))

            db_manager.disconnect()  # DB 연결 종료
            return redirect(url_for('admin_lamp_check'))

        except Exception as e:
            flash(f'가로등 등록 중 오류가 발생했습니다: {str(e)}', 'error')
            db_manager.disconnect()  # DB 연결 종료
            return redirect(url_for('street_light_register'))

    return render_template('admin/street_light_register.html')
    
    
# 철거된 가로등 삭제
@app.route('/admin/street_light_delete')
def street_light_delete():
    return render_template('admin/street_light_delete.html')

@app.route('/api/decommissioned-streetlights', methods=['GET'])
def search_decommissioned_streetlights():
    criteria = request.args.get('criteria')
    value = request.args.get('value')
    
    db = DBManager()
    db.connect()
    
    try:
        query = """
            SELECT street_light_id as id, location, 
                   DATE_FORMAT(installation_date, '%Y-%m-%d') as installation_date,
                   DATE_FORMAT(registered_at, '%Y-%m-%d') as decommissionDate
            FROM street_lights
            WHERE 
        """
        
        if criteria == 'id':
            query += "street_light_id LIKE %s"
            search_param = f"%{value}%"
        elif criteria == 'location':
            query += "location LIKE %s"
            search_param = f"%{value}%"
        else:
            return jsonify([])
            
        db.cursor.execute(query, (search_param,))
        results = db.cursor.fetchall()
        
        return jsonify(results)
    
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")
        return jsonify([])
    
    finally:
        db.disconnect()

@app.route('/api/decommissioned-streetlights/<int:id>', methods=['DELETE'])
def delete_streetlight(id):
    db = DBManager()
    db.connect()
    
    try:
        # 즉시 가로등 데이터 삭제 (로그 기록 없음)
        delete_query = "DELETE FROM street_lights WHERE street_light_id = %s"
        db.cursor.execute(delete_query, (id,))
        
        db.connection.commit()
        return jsonify({"success": True})
    
    except Exception as e:
        db.connection.rollback()
        print(f"삭제 중 오류 발생: {e}")
        return jsonify({"success": False, "message": str(e)})
    
    finally:
        db.disconnect()


@app.route('/admin/inquries_completed')
def admin_inquries_completed():
    return render_template('public/index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)