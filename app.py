import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os

# データベースファイルのパス
DB_FILE = 'diary_data.db'

# ユーザー情報をリストで管理
USER_LIST = [
    {"username": "admin", "password": "0483679993109"},
    {"username": "tiger", "password": "tiger"},
    {"username": "oba", "password": "oba"},
    {"username": "yume", "password": "yume"},
    {"username": "haru", "password": "haru"},
    {"username": "guest", "password": "guest"},
    # 追加のユーザー情報をここに追加できます
]

# データベース接続とテーブルの作成
def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS diary')
    c.execute('''
        CREATE TABLE diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date TEXT,
            entry TEXT
        )
    ''')
    conn.commit()
    conn.close()

# テーブルの初期化
if not os.path.exists(DB_FILE):
    initialize_database()

# データの読み込み
def load_data():
    conn = sqlite3.connect(DB_FILE)
    data = pd.read_sql_query('SELECT * FROM diary', conn)
    conn.close()
    return data

# データの削除
def delete_entry(entry_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM diary WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()

# セッション状態の初期化
if 'username' not in st.session_state:
    st.session_state.username = None

if 'diary_data' not in st.session_state:
    st.session_state.diary_data = pd.DataFrame(columns=['id', 'username', 'date', 'entry'])

def login(username, password):
    return any(user['username'] == username and user['password'] == password for user in USER_LIST)

if st.session_state.username is None:
    st.title("ログイン")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    st.text('ページに来てくれてありがとう')
    st.text('全部のボタン2回ずつ押さないと反応しない、直せたら直すね！！')
    if st.button("ログイン"):
        if login(username, password):
            st.session_state.username = username
            st.session_state.diary_data = load_data()
            st.success("ログイン成功！")
        else:
            st.error("ユーザー名またはパスワードが間違っています")
else:
    st.title("つぶやきアプリ")

    st.header("つぶやきを記録")
    entry = st.text_area("内容を入力してね")

    if st.button("保存"):
        if entry:
            new_entry = pd.DataFrame({'username': [st.session_state.username],
                                      'date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                                      'entry': [entry]})
            conn = sqlite3.connect(DB_FILE)
            new_entry.to_sql('diary', conn, if_exists='append', index=False)
            conn.close()
            st.session_state.diary_data = load_data()
            st.success("データ保存されました！")
        else:
            st.error("データ内容が空です！")

    st.header("一覧")
    if not st.session_state.diary_data.empty:
        for idx, row in st.session_state.diary_data.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{row['date']} - {row['username']}: {row['entry']}")
            with col2:
                if row['username'] == st.session_state.username or st.session_state.username == 'admin':
                    if st.button("削除", key=f"delete_{row['id']}"):
                        delete_entry(row['id'])
                        st.session_state.diary_data = load_data()
    else:
        st.write("データがないよ")

    # adminユーザーのみCSVダウンロードが可能
    if st.session_state.username == 'admin':
        st.header("CSVファイルで保存できるよ")
        if not st.session_state.diary_data.empty:
            csv = st.session_state.diary_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="CSVとしてダウンロード",
                data=csv,
                file_name='diary_entries.csv',
                mime='text/csv',
            )

    if st.button("ログアウト"):
        st.session_state.username = None
        st.session_state.diary_data = pd.DataFrame(columns=['id', 'username', 'date', 'entry'])
        st.write("ログアウトしました。ばいばい。")
