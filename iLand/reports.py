# -*- coding: utf-8 -*-

from utils import get_all_fields_from_feat
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph,
                                Spacer, Image, PageBreak, Table,
                                TableStyle,Flowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm,mm,inch
from reportlab.lib import utils
from reportlab.lib import colors
from django.core.files.storage import FileSystemStorage
from reportlab.platypus.flowables import HRFlowable
import tempfile

from iLand.models import Feature,Shapefile


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 10)
    canvas.setTitle('Report Agrisurvey')
    page_number_text = "pagina %d" % (doc.page)
    canvas.drawCentredString(
        0.75 * inch,
        0.75 * inch,
        page_number_text
    )
    canvas.restoreState()

class MCLine(Flowable):
    """
    Line flowable --- draws a line in a flowable
    http://two.pairlist.net/pipermail/reportlab-users/2005-February/003695.html
    """
    #----------------------------------------------------------------------
    def __init__(self, width, height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height
    #----------------------------------------------------------------------
    def __repr__(self):
        return "Line(w=%s)" % self.width
    #----------------------------------------------------------------------
    def draw(self):
        """
        draw the line
        """
        self.canv.line(0, self.height, self.width, self.height)

def report_singolo_platypus(catastale,lista_feature):
    tf = tempfile.NamedTemporaryFile()

    stile_tabella = TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ])

    doc = SimpleDocTemplate(tf.name,
                            pagesize=A4,
                            rightMargin=1 * cm,
                            leftMargin=1 * cm,
                            topMargin=2 * cm,
                            bottomMargin=2 * cm
                            )
    styles = getSampleStyleSheet()
    Story = []
    # inizio la generazione dell'oggetto del report
    P0 = Paragraph("<b>Report vincoli</b><br/><font size=12><i>reteVISTA</i></font>",
                   styles['Heading1'])
    P1 = Paragraph('''<font size=8>Richiedente:<br/></font>
        	                  <br/>
        	                  <u><font size=10 color=red>Codice: </font></u>
        	               ''' , styles['Normal'])
    data = [[P0, ''],
            [P1, '']]
    t = Table(data, 2 * [9.5 * cm], 2 * [1.7 * cm])
    t.setStyle(TableStyle([('GRID', (0, 0), (1, -2), 1, colors.grey),
                           ('BOX', (0, 0), (1, -1), 2, colors.black),
                           ('SPAN', (1, -1), (-1, -1))]))
    Story.append(t)
    Story.append(Spacer(2 * cm, 2 * cm))


    particella_results = Feature.objects.filter(shapefile__filename__istartswith=catastale,pk__in=lista_feature)
    vincoli = Shapefile.objects.filter(tipologia='vincoli')

    line = MCLine(500)


    for particella in particella_results: #ciclo sulle particelle
        # metto una linea
        Story.append(line)
        # scrivo i dati della particella
        Story.append(Paragraph(
            "Dato catastale: <br/>" + get_all_fields_from_feat(particella),
            styles['Heading2']))
        particella.geom_polygon.transform('3004')
        for vincolo in vincoli: #ciclo per ogni vincolo
            vincolo_features = Feature.objects.filter(shapefile=vincolo)
            # vincolo_features = Feature.objects.filter(id=501)#per sviluppo

            # scrivo il nome del vincolo
            Story.append(Spacer(0.5 * cm, 0.5 * cm))
            Story.append(Paragraph(
                "<b>Vincolo: "+vincolo.filename+'</b>',
                styles['Normal']))
            for vinc_feat in vincolo_features: #ciclo per ogni feature
                vinc_feat.geom_polygon.transform('3004')
                #controllo se si intersecano
                if particella.geom_polygon.intersects(vinc_feat.geom_polygon):
                    if vinc_feat.geom_polygon.valid and particella.geom_polygon.valid:
                        intersezione = particella.geom_polygon.intersection(vinc_feat.geom_polygon)
                        sovrapposizione = round(particella.geom_polygon.area / intersezione.area *100,0)
                        ptext = get_all_fields_from_feat(vinc_feat)
                        Story.append(Paragraph(ptext, styles["Bullet"]))
                        ptext = '<bullet>&bull;</bullet> sovrapposizione del '
                        ptext += str(sovrapposizione)
                        ptext += '%'
                        Story.append(Paragraph(ptext, styles["Bullet"]))

            Story.append(Spacer(1 * cm, 1 * cm))
        Story.append(Spacer(2 * cm, 2 * cm))

    doc.build(
        Story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )
    fs = FileSystemStorage("/tmp")
    with open(tf.name) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        return response

    return response





