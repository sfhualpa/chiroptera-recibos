from flask import Flask, render_template, request, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generar", methods=["POST"])
def generar_pdf():
    cliente = request.form["cliente"]
    telefono = request.form["telefono"]
    direccion = request.form["direccion"]
    recibo = request.form["recibo"]
    comision = float(request.form["comision"])

    productos = []
    subtotal = 0

    nombres = request.form.getlist("producto[]")
    cantidades = request.form.getlist("cantidad[]")
    precios = request.form.getlist("precio[]")

    for n, c, p in zip(nombres, cantidades, precios):
        total = int(c) * float(p)
        subtotal += total
        productos.append([n, c, p, total])

    total_pagar = subtotal + comision

    os.makedirs("recibos", exist_ok=True)
    archivo = f"recibos/recibo_{recibo}.pdf"

    doc = SimpleDocTemplate(archivo, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    logo = Image("logo.png", 3.5*cm, 3.5*cm)

    encabezado = Table(
        [[
            Paragraph(
                f"<b>RECIBO DE VENTA</b><br/>Recibo Nº {recibo}<br/>{datetime.now().strftime('%d/%m/%Y')}",
                styles["Normal"]
            ),
            logo
        ]],
        colWidths=[12*cm, 4*cm]
    )

    elementos.append(encabezado)
    elementos.append(Spacer(1, 12))

    elementos.append(Paragraph(f"<b>Cliente:</b> {cliente}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Teléfono:</b> {telefono}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Dirección:</b> {direccion}", styles["Normal"]))
    elementos.append(Spacer(1, 10))

    tabla = [["Producto", "Cantidad", "Precio", "Total"]]
    for p in productos:
        tabla.append([p[0], p[1], f"${p[2]}", f"${p[3]:.2f}"])

    t = Table(tabla, colWidths=[7*cm, 3*cm, 3*cm, 3*cm])
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("BACKGROUND", (0,0), (-1,0), colors.lightblue)
    ]))

    elementos.append(t)
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph(f"<b>Total a pagar:</b> ${total_pagar:.2f}", styles["Heading2"]))

    doc.build(elementos)

    return send_file(archivo, as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
