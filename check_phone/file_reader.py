import openpyxl


def get_values(file):
    wb = openpyxl.load_workbook(filename=file)
    sheet = wb.active
    phone = 0
    phones = []
    lines = {}
    for row in sheet.iter_rows():
        l = ""
        for i in range(len(row)):
            if i == 0:
                phone = row[0]._value
                phones.append(row[0]._value)
            else:
                l = l + str(row[i]._value) + ';'
        lines[phone] = l[:-1]
    return phones, lines