import pandas as pd
import psycopg2


def get_connection(db_params):
    return psycopg2.connect(**db_params)


def fetch_data(query, db_params, params=None):
    """Hàm hỗ trợ lấy dữ liệu và trả về Pandas DataFrame"""
    conn = get_connection(db_params)
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=columns)
        return df
    finally:
        conn.close()
