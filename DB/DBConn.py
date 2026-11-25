from pymysql import connect
from dotenv import load_dotenv
from pandas import read_sql_query
from pathlib import Path
import os

load_dotenv(Path(__file__).parent / ".env")
# Path(__file__) 현재 파일이 위치한 폴더 안
# Path(__file__).parent 현재 파일의 상위 폴더 안
# Path 객체에서는 / 연산자가 경로 이어 붙이기로 사용


def _Conn():
    return connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PWD"),
        database=os.getenv("DB_DATABASE"),
        charset=os.getenv("DB_CHARSET"),
    )


def LoadDB(strQuery):
    with _Conn() as conn:
        # DBConn.py를 임포트할때마다 연결하는걸 방지
        # 해당 함수를 호출하여 사용시에만 호출
        return read_sql_query(strQuery, conn)
