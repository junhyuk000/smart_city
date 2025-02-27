from flask import Flask, url_for, render_template, send_from_directory, jsonify ,request, redirect, session,flash
from functools import wraps
import os
from datetime import datetime
from models import DBManager
import boto3
import io




app = Flask(__name__)
app.secret_key = 'your-secret-key234'
# app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static','uploads')

# 디렉토리 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



#
# 클래스 호출
manager = DBManager()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/uploads/<path:filename>')
def uploads_file(filename):
    return send_from_directory('static/uploads', filename)

@app.route('/index')
def index():
    posts = manager.get_all_posts()
    
    page = int(request.args.get('page', 1))  # 쿼리 파라미터에서 페이지 번호 가져오기
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = posts[start:end]
    # 총 페이지 수 계산
    total_pages = (len(posts) + per_page - 1) // per_page
    
    return render_template('index.html',posts=paginated_data, page=page, total_pages=total_pages)

@app.route('/post/<int:id>')
@login_required
def view_post(id):
    post = manager.get_post_by_id(id)
    views = manager.increment_hits(id)
    return render_template('view.html',post=post, views=views)

# 내용추가
# 파일업로드: method='POST' enctype="multipart/form-data" type='file accept= '.png,.jpg,.gif

@app.route('/post/add', methods=['GET', 'POST'])
def add_post():
    userid = session['id']
    username = session['name']
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        # 첨부파일 한 개
        file = request.files['file']
        filename = file.filename if file else None

        if file and filename:
            # 파일을 메모리에서 바로 S3로 업로드
            s3 = boto3.client('s3')
            bucket_name = 'usabucketmy'
            s3.upload_fileobj(file, bucket_name, filename)

        if manager.insert_post(title, content, filename, userid, username):
            return redirect(url_for('index'))
        return flash("게시글 추가 실패", 'error')
    return render_template('add.html')


@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['file']
        
        filename = file.filename if file else None
        
        if filename:
            s3 = boto3.client('s3')
            bucket_name = 'usabucketmy'
            s3.upload_fileobj(file, bucket_name, filename)
        
        # 게시글 정보를 업데이트
        if manager.update_post(id, title, content, filename):
            flash("업데이트 성공!", "success")
            return redirect(url_for('index'))  # 성공 시 메인 페이지로 리디렉션
        return flash("게시글 수정 실패,400", 'error')  # 실패 시 400 에러 반환

    # GET 요청: 게시글 정보를 가져와 폼에 표시
    post = manager.get_post_by_id(id)
    if post:
        return render_template('edit.html', post=post)  # 수정 페이지 렌더링
    return flash("게시글을 찾을 수 없습니다.404", 'error')

@app.route('/post/delete/<int:id>')
def delete_post(id):
    post = manager.get_post_by_id(id)
    if post:
        file = post.get('filename')
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            os.remove(file_path)
            flash("file삭제",'success')
            if manager.delete_post(id):
                flash("게시물 삭제 성공!","success")
                return redirect(url_for('index'))
            return f'<script>alert("파일 삭제 성공! 게시물 삭제 실패!");location.href="{url_for("register")}"</script>' # 스크립트로 alert알람창 띄우기
        else:
            if manager.delete_post(id):
                flash("게시물 삭제 성공!","success")
                return redirect(url_for('index'))
        flash("삭제실패",'error')
    
    return redirect(url_for('view'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('username')
        id = request.form.get('userid')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_ip = request.remote_addr

        if manager.duplicate_user(id):
            flash("중복된 아이디가 존재합니다.",'error')
            return redirect(url_for('register'))

        if password == confirm_password:
            manager.regsiter_user(name, id, password,user_ip)
            return redirect(url_for('login'))
        return flash("계정 등록 실패,400", "error")
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
@app.route('/')
def login():

    if request.method == 'POST':
        id = request.form.get('userid')
        password = request.form.get('password')
        user = manager.login_user(id, password)
        if user:
            session['id'] = id
            session['name'] = user['name']
            
            return f'<script>alert("로그인 성공!");location.href="{url_for("index")}"</script>'
        else:
            flash("로그인 실패!", 'error')
    return render_template('login.html')

### 세션 삭제
@app.route('/logout')
def delete_session_data():
    session.clear()
    flash("로그아웃 되었습니다.", "success")
    return render_template('login.html')

@app.route('/myinfo')
def myinfo():
    id = session['id']
    user = manager.get_user_by_id(id)
    return render_template('myinfo.html',user=user)

@app.route('/delete_user')
def delete_user():
    id = session['id']
    if manager.delete_user(id):
        session.clear()
        return f'<script>alert("회원탈퇴 성공!");location.href="{url_for("login")}"</script>' # 스크립트로 alert알람창 띄우기
    else:
        return f'<script>alert("회원탈퇴 실패!");location.href="{url_for("index")}"</script>'

@app.route('/edit_password', methods=['GET','POST'])
def edit_password():
    if request.method=='POST':
        id = request.form.get('userid')
        password = request.form.get('password')
        user = manager.get_user_by_id(id)
        if user['id'] == request.form.get('userid') and user['name'] == request.form.get('username'):
            if manager.get_user_edit_password(id, password):
                return f'<script>alert("비밀번호 변경 성공!");location.href="{url_for("login")}"</script>'
            return f'<script>alert("비밀번호 변경 실패!, 아이디 혹은 이름이 다릅니다.");location.href="{url_for("login")}"</script>'
        
    return render_template('edit_password.html')
        


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)