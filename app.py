from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kararlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            yil TEXT NOT NULL,
            no TEXT NOT NULL,
            madde TEXT,
            anahtar_kelime TEXT,
            karar TEXT,
            ilgili_dokuman TEXT,
            degistirilen_karar TEXT,
            guncel_karar TEXT,
            olusturma_tarihi TEXT,
            guncelleme_tarihi TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ekle", methods=["GET", "POST"])
def ekle():
    if request.method == "POST":
        yil = request.form["yil"]
        no = request.form["no"]
        madde = request.form["madde"]
        anahtar_kelime = request.form["anahtar_kelime"]
        karar = request.form["karar"]
        ilgili_dokuman = request.form["ilgili_dokuman"]
        degistirilen_karar = request.form["degistirilen_karar"]
        guncel_karar = request.form["guncel_karar"]

        now = datetime.now().strftime("%d.%m.%Y %H:%M")

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO kararlar
            (yil, no, madde, anahtar_kelime, karar, ilgili_dokuman,
             degistirilen_karar, guncel_karar, olusturma_tarihi, guncelleme_tarihi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            yil, no, madde, anahtar_kelime, karar, ilgili_dokuman,
            degistirilen_karar, guncel_karar, now, now
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("liste"))

    return render_template("ekle.html")


@app.route("/liste", methods=["GET"])
def liste():
    arama = request.args.get("arama", "")
    yil = request.args.get("yil", "")
    madde = request.args.get("madde", "")

    conn = get_db_connection()

    query = """
        SELECT * FROM kararlar
        WHERE 1=1
    """
    params = []

    if arama:
        query += """
            AND (
                anahtar_kelime LIKE ?
                OR karar LIKE ?
                OR guncel_karar LIKE ?
                OR degistirilen_karar LIKE ?
                OR ilgili_dokuman LIKE ?
                OR no LIKE ?
                OR madde LIKE ?
            )
        """
        like_value = f"%{arama}%"
        params.extend([like_value] * 7)

    if yil:
        query += " AND yil LIKE ?"
        params.append(f"%{yil}%")

    if madde:
        query += " AND madde LIKE ?"
        params.append(f"%{madde}%")

    query += " ORDER BY id DESC"

    kararlar = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("liste.html", kararlar=kararlar, arama=arama, yil=yil, madde=madde)


@app.route("/guncelle/<int:id>", methods=["GET", "POST"])
def guncelle(id):
    conn = get_db_connection()
    karar_kaydi = conn.execute("SELECT * FROM kararlar WHERE id = ?", (id,)).fetchone()

    if karar_kaydi is None:
        conn.close()
        return "Kayıt bulunamadı."

    if request.method == "POST":
        yil = request.form["yil"]
        no = request.form["no"]
        madde = request.form["madde"]
        anahtar_kelime = request.form["anahtar_kelime"]
        karar = request.form["karar"]
        ilgili_dokuman = request.form["ilgili_dokuman"]
        degistirilen_karar = request.form["degistirilen_karar"]
        guncel_karar = request.form["guncel_karar"]

        now = datetime.now().strftime("%d.%m.%Y %H:%M")

        conn.execute("""
            UPDATE kararlar
            SET yil = ?,
                no = ?,
                madde = ?,
                anahtar_kelime = ?,
                karar = ?,
                ilgili_dokuman = ?,
                degistirilen_karar = ?,
                guncel_karar = ?,
                guncelleme_tarihi = ?
            WHERE id = ?
        """, (
            yil, no, madde, anahtar_kelime, karar,
            ilgili_dokuman, degistirilen_karar, guncel_karar,
            now, id
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("liste"))

    conn.close()
    return render_template("guncelle.html", karar=karar_kaydi)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
@app.route("/sil/<int:id>", methods=["POST"])
def sil(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM kararlar WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("liste"))