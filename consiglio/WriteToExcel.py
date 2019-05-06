#!/usr/bin/python
# -*- coding: utf-8 -*-

import StringIO
import xlsxwriter
from django.utils.translation import ugettext


def WriteToExcel(appezzamento, bilanci):
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)

    soglia_intervento = appezzamento.cap_idrica - appezzamento.ris_fac_util

    worksheet_s = workbook.add_worksheet("Report")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
       'align': 'center'
    })
    title_text = u"{0} {1}".format(ugettext("Report per appezzamento: "), appezzamento.nome)
    worksheet_s.merge_range('A1:P1', title_text, title)
    #add rows header
    worksheet_s.write(1, 0, ugettext("data"), header)
    worksheet_s.write(1, 1, ugettext("pioggia"), header)
    worksheet_s.write(1, 2, ugettext("Kc"), header)
    worksheet_s.write(1, 3, ugettext("Et0"), header)
    worksheet_s.write(1, 4, ugettext("EtC"), header)
    worksheet_s.write(1, 5, ugettext("P - Ep"), header)
    worksheet_s.write(1, 6, ugettext("L"), header)
    worksheet_s.write(1, 7, ugettext("lambda"), header)
    worksheet_s.write(1, 8, ugettext("a"), header)
    worksheet_s.write(1, 9, ugettext("A > U"), header)
    worksheet_s.write(1, 10, ugettext("A(mm)"), header)
    worksheet_s.write(1, 11, ugettext("Irrigazione"), header)
    worksheet_s.write(1, 12, ugettext("Dose(mm)"), header)
    worksheet_s.write(1, 13, ugettext("Dose antropica(mm)"), header)
    worksheet_s.write(1, 14, ugettext("Soglia intervento"), header)
    worksheet_s.write(1, 15, ugettext("Irr(mm)"), header)

    worksheet_s.set_column('A:A', 10)
    worksheet_s.set_column('L:L', 10)
    worksheet_s.set_column('M:M', 10)
    worksheet_s.set_column('N:N', 16)
    worksheet_s.set_column('O:O', 14)


    # Here we will adding the code to add data

    for idx, bilancio in enumerate(bilanci):
        row = 2 + idx
        worksheet_s.write(row, 0, bilancio.data_rif.strftime('%d/%m/%Y'), cell_center)
        worksheet_s.write_number(row, 1, bilancio.pioggia_cum, cell_center)
        worksheet_s.write_number(row, 2, bilancio.Kc, cell_center)
        worksheet_s.write_number(row, 3, bilancio.Et0, cell_center)
        worksheet_s.write_number(row, 4, bilancio.Etc, cell_center)
        worksheet_s.write_number(row, 5, bilancio.P_ep, cell_center)
        worksheet_s.write_number(row, 6, bilancio.L, cell_center)
        worksheet_s.write_number(row, 7, bilancio.Lambda, cell_center)
        worksheet_s.write_number(row, 8, bilancio.a, cell_center)
        worksheet_s.write_number(row, 9, bilancio.Au, cell_center)
        worksheet_s.write_number(row, 10, bilancio.A, cell_center)
        worksheet_s.write_number(row, 11, bilancio.Irrigazione, cell_center)
        worksheet_s.write_number(row, 12, bilancio.dose, cell_center)
        worksheet_s.write_number(row, 13, bilancio.dose_antropica, cell_center)
        worksheet_s.write_number(row, 14, soglia_intervento, cell_center)
        worksheet_s.write_number(row, 15, bilancio.Irr_mm, cell_center)




    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data