from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "your_secret_key"  

db_config = {
    "host": "localhost",
    "user": "root",  
    "password": "", 
    "database": "crud_baju" 
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            return conn
    except Error as e:
        flash(f"Kesalahan koneksi: {e}", "danger")
    return None

def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            conn.commit()
            if fetch:
                return cursor.fetchall()
            return True
    except Error as e:
        flash(f"Terjadi kesalahan: {e}", "danger")
        return None
    finally:
        conn.close()

@app.route("/")
def index():
    baju = execute_query("SELECT * FROM baju", fetch=True)
    return render_template("index.html", baju=baju or [])

@app.route("/add", methods=["GET", "POST"])
def add_baju():
    if request.method == "POST":
        nama_baju = request.form["nama_baju"]
        ukuran = request.form["ukuran"]
        warna = request.form["warna"]
        harga = request.form["harga"]

        if not (nama_baju and ukuran and warna and harga):
            flash("Semua kolom harus diisi!", "danger")
            return redirect(url_for("add_baju"))

        query = "INSERT INTO baju (nama_baju, ukuran, warna, harga) VALUES (%s, %s, %s, %s)"
        params = (nama_baju, ukuran, warna, harga)

        if execute_query(query, params):
            flash("Baju berhasil ditambahkan!", "success")
            return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_baju(id):
    baju = execute_query("SELECT * FROM baju WHERE id = %s", (id,), fetch=True)
    if not baju:
        flash("Data baju tidak ditemukan.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        nama_baju = request.form["nama_baju"]
        ukuran = request.form["ukuran"]
        warna = request.form["warna"]
        harga = request.form["harga"]

        if not (nama_baju and ukuran and warna and harga):
            flash("Semua kolom harus diisi!", "danger")
            return redirect(url_for("edit_baju", id=id))

        query = "UPDATE baju SET nama_baju = %s, ukuran = %s, warna = %s, harga = %s WHERE id = %s"
        params = (nama_baju, ukuran, warna, harga, id)

        if execute_query(query, params):
            flash("Baju berhasil diperbarui!", "success")
            return redirect(url_for("index"))

    return render_template("edit.html", baju=baju[0])

@app.route("/delete/<int:id>", methods=["POST"])
def delete_baju(id):
    query = "DELETE FROM baju WHERE id = %s"
    if execute_query(query, (id,)):
        flash("Baju berhasil dihapus!", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
