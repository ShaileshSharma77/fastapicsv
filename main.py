from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3
from io import TextIOWrapper

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def create_connection():
    conn = sqlite3.connect('users.db')
    return conn


def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            csv_filename TEXT NOT NULL
        )
    ''')
    conn.commit()


def insert_user(conn, name, age, csv_filename):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Users (name, age, csv_filename) VALUES (?, ?, ?)
    ''', (name, age, csv_filename))
    conn.commit()


def fetch_all_users(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users')
    return cursor.fetchall()


@app.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/uploadfile/")
async def create_upload_file(request: Request, file: UploadFile = File(...), name: str = Form(...), age: int = Form(...)):
    contents = await file.read()

    conn = create_connection()
    create_table(conn)

    # Parse CSV and extract Name and Age columns
    # Here, assuming that `name` and `age` are obtained from CSV data
    csv_filename = "UploadFile" 
    insert_user(conn, name, age, csv_filename)

    conn.close()

    return {"filename": file.filename, "name": name, "age": age}


@app.get("/users", response_class=HTMLResponse)
async def get_all_users(request: Request):
    conn = create_connection()
    users = fetch_all_users(conn)
    conn.close()

    return templates.TemplateResponse("users.html", {"request": request, "users": users})
