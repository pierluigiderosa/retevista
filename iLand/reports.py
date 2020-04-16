# -*- coding: utf-8 -*-
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm,mm,inch
from reportlab.lib import utils
from reportlab.lib import colors
from django.core.files.storage import FileSystemStorage
from reportlab.platypus.flowables import HRFlowable
import tempfile

from iLand.models import Feature


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

def report_singolo_platypus(catastale,lista_feature):
    foglio_results = Feature.objects.filter(shapefile__filename__startswith=catastale,pk__in=lista_feature)
