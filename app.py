from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime
import os

app = Flask(__name__)

OUTPUT_DIR = "recibos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # ======================
        # DATOS CLIENTE
        # ======================
        cliente = request.form["cliente"]
        cedula = request.form["cedula"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]
        numero_recibo = request.form["numero_recibo"]
        comision_servicio = float(request.form["comision"])

        # ======================
        # PRODUCTOS (LISTAS)
        # ======================
        nombres = request.form.getlist("producto[]")
        cantidades = request.form.getlist("cantidad[]")
        precios = request.form.getlist("precio[]")

        productos = []
        subtotal = 0

        for n, c, p in zip(nombres, cantidades, precios):
            c = int(c)
            p = float(p)
            total = c * p
            subtotal += total
            productos.append([n, c, p, total])

        total_pagar = subtotal + comision_servicio

        # ======================
        # PDF
        # ======================
        archivo_pdf = f"{OUTPUT_DIR}/recibo_{numero_recibo}.pdf"

        doc = SimpleDocTemplate(
            archivo_pdf,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        styles = getSampleStyleSheet()

        subtitulo_style = ParagraphStyle(
            "Subtitulo",
            parent=styles["Heading3"],
            spaceAfter=6
        )

        producto_style = ParagraphStyle(
            "Producto",
            parent=styles["Normal"],
            alignment=TA_CENTER
        )

        elementos = []

        # ======================
        # ENCABEZADO
        # ======================
        logo = ""
        if os.path.exists("logo.png"):
            logo = Image("logo.png", 3.5*cm, 3.5*cm)
            logo.hAlign = "RIGHT"

        encabezado = Paragraph(
            f"<b>RECIBO DE VENTA</b><br/>"
            f"Recibo Nº: {numero_recibo}<br/>"
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["Normal"]
        )

        tabla_encabezado = Table(
            [[encabezado, logo]],
            colWidths=[12*cm, 4*cm]
        )

        tabla_encabezado.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ALIGN", (1,0), (1,0), "RIGHT"),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ]))

        elementos.append(tabla_encabezado)
        elementos.append(Spacer(1, 10))

        # ======================
        # CLIENTE
        # ======================
        elementos.append(Paragraph("DATOS DEL CLIENTE", subtitulo_style))
        elementos.append(Paragraph(f"<b>Nombre:</b> {cliente}", styles["Normal"]))
        elementos.append(Paragraph(f"<b>Cédula/RUC:</b> {cedula}", styles["Normal"]))
        elementos.append(Paragraph(f"<b>Teléfono:</b> {telefono}", styles["Normal"]))
        elementos.append(Paragraph(f"<b>Dirección:</b> {direccion}", styles["Normal"]))
        elementos.append(Spacer(1, 12))

        # ======================
        # TABLA PRODUCTOS
        # ======================
        tabla_datos = [[
            Paragraph("<b>Producto</b>", producto_style),
            Paragraph("<b>Cantidad</b>", producto_style),
            Paragraph("<b>Precio Unitario</b>", producto_style),
            Paragraph("<b>Total</b>", producto_style),
        ]]

        for p in productos:
            tabla_datos.append([
                Paragraph(p[0], producto_style),
                Paragraph(str(p[1]), producto_style),
                Paragraph(f"${p[2]:.2f}", producto_style),
                Paragraph(f"${p[3]:.2f}", producto_style),
            ])

        tabla = Table(tabla_datos, colWidths=[8*cm, 3*cm, 3.5*cm, 3.5*cm])

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#D1DD1D")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 12))

        # ======================
        # TOTALES
        # ======================
        elementos.append(Paragraph(f"<b>Subtotal:</b> ${subtotal:.2f}", styles["Normal"]))
        elementos.append(Paragraph(
            f"<b>Comisión de servicio:</b> ${comision_servicio:.2f}",
            styles["Normal"]
        ))
        elementos.append(Spacer(1, 6))
        elementos.append(Paragraph(
            f"<b>TOTAL A PAGAR: ${total_pagar:.2f}</b>",
            styles["Heading2"]
        ))
        elementos.append(Spacer(1, 14))

        # ======================
        # TÉRMINOS
        # ======================
        terminos = (
            "El tiempo estimado de entrega de los pedidos es de 22 a 30 días calendario, pudiendo extenderse hasta un máximo de 50 días por causas ajenas a nuestra gestión, tales como retrasos en aduanas o inconvenientes en el transporte internacional. En caso de pérdida del pedido durante el proceso de envío, Chiroptera Store se compromete a realizar las gestiones necesarias para la devolución del importe pagado o la reposición del producto, conforme a las políticas de las tiendas proveedoras. La empresa actúa exclusivamente como intermediaria en la compra, transporte y entrega de los productos seleccionados por el cliente, por lo que no asume responsabilidad sobre características como talla, color, calidad, diseño u otras especificaciones del artículo. Las tarifas aplicables son de USD 3.50 por libra; para pedidos superiores a USD 50.00, se aplicará una tarifa única de USD 10.00. Los pedidos que superen USD 400,00 estarán sujetos a costos adicionales por importación bajo modalidades especiales de transporte, determinados según las tarifas de la empresa transportista. La cobertura de entrega incluye las ciudades de Loja, Yantzaza, Panguintza, Zumbi y El Pangui; cualquier entrega fuera de estas zonas implicará cargos adicionales. Al realizar un pedido, el cliente declara conocer y aceptar estas condiciones."
        )

        elementos.append(Paragraph("TÉRMINOS Y CONDICIONES", subtitulo_style))
        elementos.append(Paragraph(terminos, styles["Normal"]))

        doc.build(elementos)

        return send_file(archivo_pdf, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run()
