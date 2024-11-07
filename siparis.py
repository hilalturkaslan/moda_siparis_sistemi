from flask import Flask, render_template, request, redirect, url_for, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io


app = Flask(__name__)

fiyatlar = {
    "pantolon": 1350,
    "gomlek": 850,
    "ayakkabi": 1500,
    "tisort": 250,
    "corap": 150,
    "mont": 850
}

siparis_bilgisi = {}

@app.route('/')
def index():
    return render_template('siparis.html')

@app.route('/siparis', methods=['POST'])
def siparis():
    toplam_tutar = 0
    alinan_urunler = []

    for urun in ["pantolon", "gomlek", "ayakkabi"]:
        if request.form.get(urun) == "on":
            toplam_tutar += fiyatlar[urun]
            alinan_urunler.append(urun)

    for ekstra in ["tisort", "corap"]:
        if request.form.get(ekstra) == "on":
            toplam_tutar += fiyatlar[ekstra]
            alinan_urunler.append(ekstra)

    if request.form.get("mont") == "on":
        toplam_tutar += fiyatlar["mont"]
        alinan_urunler.append("mont")

    siparis_bilgisi['alinan_urunler'] = alinan_urunler
    siparis_bilgisi['toplam_tutar'] = toplam_tutar

    return redirect(url_for('siparis_onay'))

@app.route('/siparis_onay')
def siparis_onay():
    urun_fiyatlari = {urun.capitalize(): fiyatlar[urun] for urun in siparis_bilgisi['alinan_urunler']}
    return render_template('onay.html', 
                          urun_fiyatlari=urun_fiyatlari, 
                          toplam=siparis_bilgisi['toplam_tutar'])


@app.route('/pdf_indir')
def pdf_indir():
    pdf_data = io.BytesIO()
    c = canvas.Canvas(pdf_data, pagesize=letter)
    c.drawString(100, 750, "Siparis Özeti")
    c.drawString(100, 730, "Alinan Ürünler:")

    for index, urun in enumerate(siparis_bilgisi['alinan_urunler'], start=1):
        urun_fiyat = fiyatlar[urun]
        c.drawString(100, 730 - index * 20, f"- {urun.capitalize()} ({urun_fiyat} TL)")

    c.drawString(100, 730 - (len(siparis_bilgisi['alinan_urunler']) + 1) * 20, f"Toplam Tutar: {siparis_bilgisi['toplam_tutar']} TL")
    c.showPage()
    c.save()
    pdf_data.seek(0)

    return send_file(pdf_data, as_attachment=True, download_name="siparis_ozeti.pdf", mimetype='application/pdf')

if __name__ == '__main__':
     app.run(debug=True)