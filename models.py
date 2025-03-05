import mysql.connector 
from datetime import datetime
from flask import jsonify
import json
import requests
import re

class DBManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    # 데이터베이스 연결
    def connect(self):
        try:
            # MySQL 데이터베이스 연결
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
    def get_member_by_id(self, userid):
        try:
            self.connect()
            sql = "SELECT * FROM members WHERE userid = %s"
            value = (userid,)
            self.cursor.execute(sql,value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error :
            print(f"회원정보 가져오기 연결 실패: {error}")
            return None 
        finally:
            self.disconnect()
    

    ## 회원가입 유효성검사
    # 중복아이디 확인
    def duplicate_member(self, userid):
        try:
            self.connect()
            sql = 'SELECT * FROM members WHERE userid = %s'
            self.cursor.execute(sql, (userid,))
            result = self.cursor.fetchone()
            if result : 
                return True
            else :
                return False
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"회원가입 실패: {error}")
            return False
        finally:
            self.disconnect()
    
    # 삭제된 아이디와 중복여부 확인
    def duplicate_removed_member(self, userid):
        try:
            self.connect()
            sql = 'SELECT * FROM members WHERE userid = %s'
            self.cursor.execute(sql, (userid,))
            result = self.cursor.fetchone()
            if result : 
                return True
            else :
                return False
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"회원가입 실패: {error}")
            return False
        finally:
            self.disconnect()

    # 이메일 중복 확인
    def duplicate_email(self, email):
        try:
            self.connect()
            sql = 'SELECT * FROM members WHERE email = %s'
            self.cursor.execute(sql, (email,))
            return self.cursor.fetchone()    
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"회원가입 실패: {error}")
            return False
        finally:
            self.disconnect()
    
    #삭제된 회원중에서 이메일 중복 확인
    def duplicate_removed_email(self, email):
        try:
            self.connect()
            sql = 'SELECT * FROM removed_members WHERE email = %s'
            self.cursor.execute(sql, (email,))
            result = self.cursor.fetchone()
            if result : 
                return True
            else :
                return False
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"회원가입 실패: {error}")
            return False
        finally:
            self.disconnect()

    ## 회원가입 정보 처리
    #테이블에 가입한 회원 데이터 삽입
    def register_pending_member(self, userid, username, password, birthday, email, gender):
        try:
            self.connect()
            sql = """
                INSERT INTO members (userid, username, password, birthday, email, status, gender)
                VALUES (%s, %s, %s, %s, %s, 'pending', %s)
                """
            values = (userid, username, password, email, birthday, gender)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except Exception as error:
            print(f"회원 정보 저장 실패: {error}")
            return False
        finally:
            self.disconnect()
    
    #전체 가입자 수 카운트 
    def all_member_count(self):
        try:
            # 회원 수 카운트 쿼리 실행
            sql = "SELECT COUNT(*) AS member_count FROM members WHERE role != 'admin'"
            self.connect()  # 데이터베이스 연결
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result['member_count'] 
        except Exception as error:
            print(f"회원 수 조회 실패: {error}")
            return False
        finally:
            self.disconnect()
    
    #일반회원들 가져오기
    def get_all_members(self):
        try:
            self.connect()
            sql = "SELECT * FROM members WHERE role != 'admin'"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as error:
            print(f"가입승인 회원들 정보 가져오기 실패 : {error}")
            return False
        finally:
            self.disconnect()

    

    # 회원 마지막 로그인 시간 업데이트
    def update_last_login(self, userid):
        try:
            self.connect()
            sql = "UPDATE members SET last_login = CURDATE() WHERE userid = %s"
            value = (userid,)
            self.cursor.execute(sql, value)
            self.connection.commit()
        except Exception as error:
            print(f"로그인 시간 갱신 실패: {error}")
            raise
        finally:
            self.disconnect()


    # 데이터베이스(members)에서 회원지우기
    def delete_member(self, userid):
        try:
            self.connect()
            sql = "DELETE FROM members WHERE userid = %s"
            value = (userid, )
            self.cursor.execute(sql,value)
            self.connection.commit()
            print(f'{userid}님의 회원 삭제가 완료되었습니다.')
            return True
        except Exception as error:
            print(f"회원 탈퇴 실패 : {error}")
            return False
        finally : 
            self.disconnect()

  
    ## 로그인 후 문의한 내용 저장
    def add_enquire_member(self, userid, username, email, reason, notes, filename):
        try:
            self.connect()
            # equires에 CURDATE()를 명시적으로 설정
            sql = """
            INSERT INTO enquiries (userid, username, email, reason, notes, enquired_at, filename)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            """
            values = (userid,username,email,reason,notes, filename)
            self.cursor.execute(sql, values)
            self.connection.commit()
            print("문의 정보를 저장했습니다")
            return True
        except Exception as error:
            print(f"문의 정보를 저장 실패 : {error}")
            return False
        finally:
            self.disconnect()
    
    #회원 문의 정보 가져오기
    def get_enquired_posts_member(self):
        try:
            self.connect()
            sql="""
            SELECT * FROM enquiries WHERE userid != '비회원' 
            """
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as error:
            print(f"회원 문의 정보를 가져오기 실패 : {error}")
            return False
        finally:
            self.disconnect()
    
    
    # 문의 상태 업데이트 메서드(같은아이디로 반복해서 문의가 올수 있으므로 아이디,작성시간으로 구분해서 처리)
    def update_answer_status(self, userid, enquired_at):
        try: 
            self.connect()
            sql = "UPDATE enquiries SET answer_status = 'completion' WHERE userid = %s and enquired_at = %s"
            value = (userid,enquired_at)
            self.cursor.execute(sql,value)
            self.connection.commit()
            print("답변상태를 업데이트 했습니다.")
            return True
        except Exception as error:
            print(f"답변상태를 업데이트하는데 실패했습니다. : {error}")
            return False
        finally:
            self.disconnect()
    
    # 문의한 회원 정보 가져오기
    def get_enquired_post_by_id(self, userid, enquired_at):
        try:
            self.connect()
            sql="""
            SELECT * FROM enquiries WHERE userid = %s and enquired_at=%s
            """
            value=(userid,enquired_at)
            self.cursor.execute(sql,value)
            return self.cursor.fetchone()
        except Exception as error:
            print(f"회원 문의 정보 가져오기 실패 : {error}")
            return False
        finally:
            self.disconnect()
    

    #서비스 사용을 위한 검색 내역 데이터 테이블 만들기
    #검색한 내용을 저장할 데이터 삽입

    
    #서비스 사용을 위한 검색 내역 데이터값 저장
    
    def save_service_usage(self, userid, username, health_status_str, functionality_choices_str):
        try:
            self.connect()  # DB 연결
            sql = """
            INSERT INTO service_usage (userid, username, used_service_health_status,used_service_functionality, used_service_at)
            VALUES (%s, %s, %s, %s, now())
            """
            values = (userid, username, health_status_str, functionality_choices_str)

            # SQL 실행
            self.cursor.execute(sql, values)
            self.connection.commit()
            print("서비스 사용 정보가 성공적으로 저장되었습니다.")
        except Exception as error:
            print(f"서비스 사용 정보 저장 중 오류 발생: {error}")
        finally:
            self.disconnect()  # DB 연결 종료

    #서비스 최근 사용내역 정보 가져오기
    def get_service_usage_by_userid(self, userid):
        try:
            self.connect()  # DB 연결
            sql = """
            SELECT * FROM service_usage 
            WHERE userid = %s 
            ORDER BY used_service_at DESC
            """
            value = (userid,)
            self.cursor.execute(sql, value)
            return self.cursor.fetchall()  # 모든 데이터 가져오기
        except Exception as error:
            print(f"서비스 이용 내역 조회 중 오류 발생: {error}")
            return []
        finally:
            self.disconnect() 
    
    # 회원 정보 변경
    def update_member_info(self, userid, username, email, birthday):
        try:
            self.connect()  # DB 연결
            sql= """
            UPDATE members
            SET username = %s, email = %s, birthday = %s
            WHERE userid = %s
            """
            values = (username, email, birthday, userid)
            self.cursor.execute(sql, values)
            self.connection.commit()  # 모든 데이터 가져오기
            print("회원정보가 수정되었습니다.")
            return True
        except Exception as error:
            print(f"회원정보 수정을 실패했습니다 : {error}")
            return False
        finally:
            self.disconnect() 
    
    # 회원 비밀번호 변경
    def update_password(self, userid, password):
        try:
            self.connect()  # DB 연결
            sql= """
                UPDATE members
                SET password = %s
                WHERE userid = %s
                """
            values = (password, userid)
            self.cursor.execute(sql, values)
            self.connection.commit()  # 모든 데이터 가져오기
            print("회원 비밀번호가 수정되었습니다.")
            return True
        except Exception as error:
            print(f"회원 비밀번호 수정을 실패했습니다 : {error}")
            return False
        finally:
            self.disconnect() 


    #모든 데이터의 페이지 네이션
    def get_all_products(self):
        try :
            self.connect()
            sql = """
                SELECT raw_material_name, daily_intake_upper_limit, 
                cautionary_information, primary_functionality 
                FROM raw_material_data
                """
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as error:
            print(f"모든제품 데이터가져오기 실패 : {error}")
            return False
        finally:
            self.disconnect()
    
