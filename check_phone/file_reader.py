import openpyxl
from openpyxl import Workbook


def get_values(file):
    wb = openpyxl.load_workbook(filename=file)
    sheet = wb.active
    return [row[0]._value for row in sheet.iter_rows()]