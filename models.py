import mysql.connector

class DBManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    # 데이터베이스 연결
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="10.0.66.11",  # DB 서버 주소
                user="sejong",  # 사용자
                password="1234",  # 비밀번호
                database="smart_city",  # 데이터베이스 이름
                charset="utf8mb4"  # 문자셋
            )
            self.cursor = self.connection.cursor(dictionary=True)  # dictionary=True로 쿼리 결과를 딕셔너리 형태로 반환
            return self.connection  # 연결된 커넥션 반환
        except mysql.connector.Error as error:
            print(f"데이터베이스 연결 실패 : {error}")
            return None  # 연결 실패 시 None 반환
    
    # 데이터베이스 연결 해제
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

    # 선택한 회원 정보 가져오기
    def get_user_by_id(self, id):
        try:
            self.connect()
            sql = "SELECT * FROM users WHERE userid = %s"
            value = (id,)
            self.cursor.execute(sql, value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"회원 정보 가져오기 연결 실패: {error}")
            return None 
        finally:
            self.disconnect()

    # 회원 마지막 로그인 시간 업데이트
    def update_last_login(self, id):
        try:
            self.connect()
            sql = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE userid = %s"
            value = (id,)
            self.cursor.execute(sql, value)
            self.connection.commit()
        except Exception as error:
            print(f"로그인 시간 갱신 실패: {error}")
            raise
        finally:
            self.disconnect()
    
    # 선택한 관리자 정보 가져오기
    def get_admin_by_id(self, id):
        try:
            self.connect()
            sql = "SELECT * FROM admins WHERE adminid = %s"
            value = (id,)
            self.cursor.execute(sql, value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"관리자 정보 가져오기 실패: {error}")
            return None 
        finally:
            self.disconnect()

    # 관리자 마지막 로그인 시간 업데이트
    def update_admin_last_login(self, id):
        try:
            self.connect()
            sql = "UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE adminid = %s"
            value = (id,)
            self.cursor.execute(sql, value)
            self.connection.commit()
        except Exception as error:
            print(f"로그인 시간 갱신 실패: {error}")
            raise
        finally:
            self.disconnect()

    # 중복아이디 확인
    def duplicate_users(self, userid):
        try:
            self.connect()
            sql = 'SELECT * FROM users WHERE userid = %s'
            self.cursor.execute(sql, (userid,))
            result = self.cursor.fetchone()
            return result is not None
        except mysql.connector.Error as error:
            print(f"중복아이디 확인 실패: {error}")
            return False
        finally:
            self.disconnect()
    
    # 이메일 중복 확인
    def duplicate_email(self, email):
        try:
            self.connect()
            sql = 'SELECT * FROM users WHERE email = %s'
            self.cursor.execute(sql, (email,))
            result = self.cursor.fetchone()
            return result is not None
        except mysql.connector.Error as error:
            print(f"이메일 중복 확인 실패: {error}")
            return False
        finally:
            self.disconnect()
