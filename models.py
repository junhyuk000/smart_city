import mysql.connector 
from datetime import datetime, timedelta
from flask import jsonify
import json
import requests
import re

class DBManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    ## 데이터베이스 연결
    def connect(self): 
        try :
            self.connection = mysql.connector.connect(
                host = "10.0.66.32",
                user = "sejong",
                password="1234",
                database="smart_city",
                charset="utf8mb4"
            )
            self.cursor = self.connection.cursor(dictionary=True)
        
        except mysql.connector.Error as error :
            print(f"데이터베이스 연결 실패 : {error}")
    
    ## 데이터베이스 연결해제
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
    
    ## 서버가 실행될때 보안상태 업데이트
    #회원 보안상태 업데이트
    def user_update_security_status(self):
        try: 
            self.connect()
            sql = """
                  UPDATE users SET security_status = 1 
                  WHERE DATEDIFF(NOW(), password_last_updated) >= 90
                  """
            self.cursor.execute(sql,)
            self.connection.commit()
            print(f"회원 보안상태 업데이트 완료")
            return True
        except Exception as error:
            print(f"회원 보안상태 업데이트 대상 없음: {error}")
            return False
        finally:
            self.disconnect()    
    

    ### 회원가입 정보 처리
    #테이블에 가입한 회원 데이터 삽입
    def register_users(self, user_id, user_name, password, email, address, birthday, reg_number, gender):
        try:
            self.connect()
            sql = """
                  INSERT INTO users (user_id, user_name, password,  email, address, birthday, reg_number, gender)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                  """
            values = (user_id, user_name, password, email, address, birthday, reg_number, gender)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except Exception as error:
            print(f"회원 정보 저장 실패: {error}")
            return False
        finally:
            self.disconnect()

    ## 회원 or 관리자 로그인
    # 선택한 회원 아이디,이름 가져오기
    def get_user_by_id(self, id):
        try:
            self.connect()
            sql = "SELECT user_id,user_name FROM users WHERE user_id = %s"
            value = (id,)
            self.cursor.execute(sql,value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error :
            print(f"회원 정보 가져오기 연결 실패: {error}")
            return None 
        finally:
            self.disconnect()

    # 선택한 회원 모든정보 가져오기
    def get_user_by_info(self, id):
        try:
            self.connect()
            sql = "SELECT * FROM users WHERE user_id = %s"
            value = (id,)
            self.cursor.execute(sql,value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error :
            print(f"회원 정보 가져오기 연결 실패: {error}")
            return None 
        finally:
            self.disconnect()
    
    # 선택한 관리자 아이디/비밀번호 조회
    def get_admin_by_id(self, id):
        try:
            self.connect()
            sql = "SELECT admin_id,password FROM admins WHERE admin_id = %s"
            value = (id,)
            self.cursor.execute(sql,value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error :
            print(f"관리자 정보 가져오기 연결 실패: {error}")
            return None 
        finally:
            self.disconnect()

    #선택한 관리자 모든정보 가져오기
    def get_admin_by_info(self, id):
        try:
            self.connect()
            sql = "SELECT * FROM admins WHERE admin_id = %s"
            value = (id,)
            self.cursor.execute(sql,value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error :
            print(f"관리자 정보 가져오기 연결 실패: {error}")
            return None 
        finally:
            self.disconnect()
    
    #선택한 관리자 권한 가져오기
    def get_admin_role(self, id):
        try:
            self.connect()
            sql = "SELECT role FROM admins WHERE admin_id = %s"
            value = (id,)
            self.cursor.execute(sql,value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error :
            print(f"관리자 권한 가져오기 연결 실패: {error}")
            return None 
        finally:
            self.disconnect()




    # 회원 마지막 로그인 시간 업데이트
    def update_last_login(self, id):
        try:
            self.connect()
            sql = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s"
            value = (id,)
            self.cursor.execute(sql, value)
            self.connection.commit()
        except Exception as error:
            print(f"로그인 시간 갱신 실패: {error}")
            raise
        finally:
            self.disconnect()

    # 선택한 관리자 마지막로그인 업데이트
    def update_admin_last_login(self, id):
        try:
            self.connect()
            sql = "UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE admin_id = %s"
            value = (id,)
            self.cursor.execute(sql, value)
            self.connection.commit()
        except Exception as error:
            print(f"로그인 시간 갱신 실패: {error}")
            raise
        finally:
            self.disconnect()
    
    # 회원 비밀번호 변경
    def update_user_password(self, userid, password):
        try:
            self.connect()  # DB 연결
            sql= """
                UPDATE users
                SET password = %s, password_last_updated = CURRENT_TIMESTAMP, security_status = 0
                WHERE user_id = %s
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

    # 회원 정보 변경
    def update_user_info(self, userid, username, email, address):
        try:
            self.connect()  # DB 연결
            sql= """
            UPDATE users
            SET user_name=%s,
            email = %s,
            address = %s
            WHERE user_id = %s
            """
            values = (username, email, address, userid)
            self.cursor.execute(sql, values)
            self.connection.commit()  # 모든 데이터 가져오기
            print("회원정보가 수정되었습니다.")
            return True
        except Exception as error:
            print(f"회원정보 수정을 실패했습니다 : {error}")
            return False
        finally:
            self.disconnect() 

    ## 회원가입 유효성검사
    # 중복아이디 확인
    def duplicate_users(self, user_id):
        try:
            self.connect()
            sql = 'SELECT * FROM users WHERE user_id = %s'
            self.cursor.execute(sql, (user_id,))
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
            sql = 'SELECT * FROM users WHERE email = %s'
            self.cursor.execute(sql, (email,))
            return self.cursor.fetchone()    
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"회원가입 실패: {error}")
            return False
        finally:
            self.disconnect()

    # 주민등록번호 중복 확인
    def duplicate_reg_number(self, reg_number):
        try:
            self.connect()
            sql = 'SELECT * FROM users WHERE reg_number = %s'
            self.cursor.execute(sql, (reg_number,))
            return self.cursor.fetchone()    
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"회원가입 실패: {error}")
            return False
        finally:
            self.disconnect()

    
    # 비밀번호조회(계정 찾기)
    def get_user_password_by_id_name_regnumber(self, userid, username, regnumber):
        try:
            self.connect()
            sql = 'SELECT password FROM users WHERE user_id = %s and user_name = %s and reg_number = %s'
            values = (userid,username, regnumber)
            self.cursor.execute(sql, values)
            return self.cursor.fetchone()    
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"비밀번호 조회(계정 찾기) 실패 : {error}")
            return False
        finally:
            self.disconnect()
    
    # 아이디 조회(계정 찾기)
    def get_user_id_by_name_regnumber(self,username,regnumber):
        try:
            self.connect()
            sql = 'SELECT user_id FROM users WHERE user_name= %s and reg_number = %s'
            values = (username,regnumber)
            self.cursor.execute(sql, values)
            return self.cursor.fetchone()    
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"아이디 조회(계정 찾기) 실패: {error}")
            return False
        finally:
            self.disconnect()


    
    # 도로 CCTV 검색 및 페이지네이션
    def get_road_cctv_query(self, search_query, search_type, per_page, offset):
        if search_type == "street_light_id":
            sql = """
            SELECT s.*, c.cctv_ip 
            FROM street_lights s
            LEFT JOIN cameras c ON s.street_light_id = c.street_light_id
            WHERE s.street_light_id LIKE %s AND s.purpose = "도로"
            LIMIT %s OFFSET %s
            """
            values = (f"%{search_query}%", per_page, offset)

        elif search_type == "street_light_location":
            sql = """
            SELECT s.*, c.cctv_ip 
            FROM street_lights s
            LEFT JOIN cameras c ON s.street_light_id = c.street_light_id
            WHERE s.location LIKE %s AND s.purpose = "도로"
            LIMIT %s OFFSET %s
            """
            values = (f"%{search_query}%", per_page, offset)
        else:  # all 또는 기본값
            sql = """
            SELECT s.*, c.cctv_ip 
            FROM street_lights s
            LEFT JOIN cameras c ON s.street_light_id = c.street_light_id
            WHERE (s.location LIKE %s OR s.street_light_id LIKE %s) AND s.purpose = "도로"
            LIMIT %s OFFSET %s
            """
            values = (f"%{search_query}%", f"%{search_query}%", per_page, offset)
        
        return sql, values

    # 도로 CCTV 검색된 총 개수
    def get_road_cctv_count_query(self, search_query, search_type):
        if search_type == "street_light_id":
            sql = """
            SELECT COUNT(*) AS total FROM street_lights 
            WHERE street_light_id LIKE %s and purpose = "도로"
            """
            values = (f"%{search_query}%",)
        
        elif search_type == "street_light_location":
            sql = """
            SELECT COUNT(*) AS total FROM street_lights 
            WHERE location LIKE %s and purpose = "도로"
            """
            values = (f"%{search_query}%",)
        
        else:  # all 또는 기본값
            sql = """
            SELECT COUNT(*) AS total FROM street_lights 
            WHERE (location LIKE %s OR street_light_id LIKE %s) and purpose = "도로"
            """
            values = (f"%{search_query}%", f"%{search_query}%")
        
        return sql, values

    # 쿼리를 실행하고 결과를 반환
    def execute_query(self, sql, values):
        try :
            self.connect()
            self.cursor.execute(sql,values)
            return self.cursor.fetchall()
        except Exception as error:
            print(f"특정 가로등 정보 가져오기 실패 : {error}")
            return False
        finally:
            self.disconnect()
        
    
    # 카운트를 실행하고 결과를 반환
    def execute_count_query(self, count_sql, count_values):
        try :
            self.connect()
            self.cursor.execute(count_sql,count_values)
            return self.cursor.fetchone()["total"]
        except Exception as error:
            print(f"특정 가로등 개수 가져오기 실패 : {error}")
            return False
        finally:
            self.disconnect()
  
    # 인도용 CCTV 검색 및 페이지네이션
    def get_sidewalk_cctv_query(self, search_query, search_type, per_page, offset):
        if search_type == "street_light_id":
            sql = """
            SELECT s.*, c.cctv_ip 
            FROM street_lights s
            LEFT JOIN cameras c ON s.street_light_id = c.street_light_id
            WHERE s.street_light_id LIKE %s AND s.purpose = "인도"
            LIMIT %s OFFSET %s
            """
            values = (f"%{search_query}%", per_page, offset)

        elif search_type == "street_light_location":
            sql = """
            SELECT s.*, c.cctv_ip 
            FROM street_lights s
            LEFT JOIN cameras c ON s.street_light_id = c.street_light_id
            WHERE s.location LIKE %s AND s.purpose = "인도"
            LIMIT %s OFFSET %s
            """
            values = (f"%{search_query}%", per_page, offset)
        else:  # all 또는 기본값
            sql = """
            SELECT s.*, c.cctv_ip 
            FROM street_lights s
            LEFT JOIN cameras c ON s.street_light_id = c.street_light_id
            WHERE (s.location LIKE %s OR s.street_light_id LIKE %s) AND s.purpose = "인도"
            LIMIT %s OFFSET %s
            """
            values = (f"%{search_query}%", f"%{search_query}%", per_page, offset)
        
        return sql, values

    # 인도 CCTV 검색된 총 개수
    def get_sidewalk_cctv_count_query(self, search_query, search_type):
        if search_type == "street_light_id":
            sql = """
            SELECT COUNT(*) AS total FROM street_lights 
            WHERE street_light_id LIKE %s and purpose = "인도"
            """
            values = (f"%{search_query}%",)
        
        elif search_type == "street_light_location":
            sql = """
            SELECT COUNT(*) AS total FROM street_lights 
            WHERE location LIKE %s and purpose = "인도"
            """
            values = (f"%{search_query}%",)
        
        else:  # all 또는 기본값
            sql = """
            SELECT COUNT(*) AS total FROM street_lights 
            WHERE (location LIKE %s OR street_light_id LIKE %s) and purpose = "인도"
            """
            values = (f"%{search_query}%", f"%{search_query}%")
        
        return sql, values
    
    #선택된 가로등 정보 가져오기
    def get_streetlight_by_info(self,street_light_id:int):
        try:
            self.connect()
            sql = "SELECT * FROM street_lights WHERE street_light_id = %s"
            value = (street_light_id,)
            self.cursor.execute(sql, value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"가로등 정보 조회 중 오류 발생: {error}")
            return None
        finally:
            self.disconnect()

    # 카메라 정보 가져오기
    def get_camera_by_info(self,street_light_id:int):
        try:
            self.connect()
            sql = """
                SELECT *, s.location, s.purpose
                FROM cameras c
                JOIN street_lights s ON c.street_light_id = s.street_light_id
                WHERE c.street_light_id = %s
                """
            value = (street_light_id,)
            self.cursor.execute(sql, value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"카메라라 정보 조회 중 오류 발생: {error}")
            return None
        finally:
            self.disconnect()


    ## 로그인 후 문의한 내용 저장
    def add_inquire_user(self, userid, filename, inquiry_reason, detail_reason):
        try:
            self.connect()
            # equires에 CURDATE()를 명시적으로 설정
            sql = """
                INSERT INTO inquiries (user_id, capture_file, inquiry_reason, detail_reason)
                VALUES (%s, %s, %s, %s)
                """
            values = (userid, filename, inquiry_reason, detail_reason)
            self.cursor.execute(sql, values)
            self.connection.commit()
            print("문의 정보를 저장했습니다")
            return True
        except Exception as error:
            print(f"문의 정보를 저장 실패 : {error}")
            return False
        finally:
            self.disconnect()

    #문의 정보 + 유저네임 + 유저아이디 가져오기
    def get_posts_info(self):
        try:
            self.connect()
            sql="""
                SELECT *, u.user_id, u.user_name 
                FROM inquiries i
                JOIN users u ON i.user_id = u.user_id
                order by i.inquiries_id desc;
                """
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as error:
            print(f"회원 문의 정보를 가져오기 실패 : {error}")
            return False
        finally:
            self.disconnect()
    
    #선택된 문의 정보 가져오기
    def get_inquiry_by_info(self, inquiries_id):
        try:
            self.connect()
            sql="""
            SELECT * FROM inquiries where inquiries_id = %s
            """
            value=(inquiries_id,)
            self.cursor.execute(sql,value)
            return self.cursor.fetchone()
        except Exception as error:
            print(f"회원 문의 정보를 가져오기 실패 : {error}")
            return False
        finally:
            self.disconnect()
    
    #회원탈퇴 후 데이터 저장
    def update_user_status(self,userid):
        try: 
            self.connect()
            sql = "UPDATE users SET status = 'deleted' WHERE user_id = %s"
            value = (userid,)
            self.cursor.execute(sql,value)
            self.connection.commit()
            print("계정 상태를 탈퇴로 변경완료했습니다")
            return True
        except Exception as error:
            print(f"계정 상태를 탈퇴로 변경하는데 실패했습니다. : {error}")
            return False
        finally:
            self.disconnect()

    #탈퇴한 회원 사유 테이블에 저장
    def save_deleted_user(self, userid, reason, detail_reason):
        try:
            self.connect()
            sql = """
                  INSERT INTO deleted_users (user_id, reason, detail_reason)
                  VALUES (%s, %s, %s)
                  """
            values = (userid, reason, detail_reason)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except Exception as error:
            print(f"회원 정보 저장 실패: {error}")
            return False
        finally:
            self.disconnect()
    
    # 문의 상태 업데이트 (같은아이디로 반복해서 문의가 올수 있으므로 아이디,작성시간으로 구분해서 처리)
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
    
    ## 가로등 센서 데이터 DB저장
    #센서 테이블에 저장된 최근 가져오기 
    def get_latest_sensor_data(self, table_name, street_light_id):
        try:
            self.connect() 
            # ✅ 허용된 테이블 이름만 사용
            allowed_tables = ["road_sensors", "sidewalk_sensors"]
            if table_name not in allowed_tables:
                raise ValueError("❌ 허용되지 않은 테이블 이름입니다!")
            
            sql = """SELECT record_time FROM {} 
                    WHERE street_light_id = %s ORDER BY record_time DESC LIMIT 1
                  """.format(table_name)
            value = (street_light_id,)
            self.cursor.execute(sql,value)
            return self.cursor.fetchone()
        except Exception as error:
            print(f"센서 테이블 최근 데이터 가져오기 실패 : {error}")
            return False
        finally:
            self.disconnect()
            
    # 센서 데이터 DB저장
    def save_sensor_data(self, received_data):
        if "ID" not in received_data:
            print("🚨 ID 없음: 데이터 저장 안 함")
            return  
        else :
            street_light_id = int(received_data["ID"])
            street_light = self.get_streetlight_by_info(street_light_id)
            if not street_light or street_light_id != street_light['street_light_id']:
                print("❌ 유효하지 않은 센서 ID")
                return
            
        # 목적에 따라 테이블 선택
        table_name = "road_sensors" if street_light['purpose'] == '도로' else "sidewalk_sensors"

        # 최신 저장된 시간 가져오기
        latest_record_time = self.get_latest_sensor_data(table_name, street_light_id)
        current_time = datetime.now()

        if not latest_record_time:
            print("✅ 기존 데이터 없음. 새 데이터 저장")
        else:
            last_time = latest_record_time['record_time']
            time_diff = (current_time - last_time).total_seconds()

            if time_diff < 10 :
                print(f"⏳ {time_diff}초 경과 또는 값 변화 없음 → 데이터 저장 안 함")
                return

        # 데이터 저장
        try:
            self.connect()
            if table_name == "road_sensors":
                sql = f"""
                INSERT INTO {table_name} 
                (street_light_id, main_light_level, sub1_light_level_, sub2_light_level_, tilt_angle, temperature, humidity, perceived_temperature, switch_state, inspection)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    street_light_id,
                    int(received_data.get("MAIN LDR Value", 0)),
                    int(received_data.get("SUB1 LDR Value", 0)),
                    int(received_data.get("SUB2 LDR Value", 0)),
                    int(received_data.get("TILT Value", 0)),
                    received_data.get("Temperature", "0"),
                    received_data.get("Humidity", "0"),
                    received_data.get("Heat Index", "0"),
                    int(received_data.get("Switch State", 0)),
                    int(received_data.get("Check", 0)),
                )
            else:  # sidewalk_sensors
                sql = f"""
                INSERT INTO {table_name} 
                (street_light_id, main_light_level, sub1_light_level_, sub2_light_level_, tilt_angle, switch_state, inspection)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    street_light_id,
                    int(received_data.get("MAIN LDR Value", 0)),
                    int(received_data.get("SUB1 LDR Value", 0)),
                    int(received_data.get("SUB2 LDR Value", 0)),
                    int(received_data.get("TILT Value", 0)),
                    int(received_data.get("Switch State", 0)),
                    int(received_data.get("Check", 0)),
                )

            self.cursor.execute(sql, values)
            self.connection.commit()
            print(f"✅ 데이터 저장 완료 → {table_name} (ID: {street_light_id})")
            return True
        except Exception as error:
            print(f"❌ 센서 테이블 데이터 저장 실패: {error}")
            return False

        finally:
            self.disconnect()

    
    