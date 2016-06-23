import json
import csv
import copy


def open_file(path):
    with open(path, "rt") as f:
        return f.read()


def write_file(path, contents):
    with open(path, "wt") as f:
        f.write(contents)


def open_csv(path):
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        return [row for row in reader]

# def fix_csv(fceCsv):
#     newLines = []
#     for line in fceCsv.splitlines():
#         if line == '':
#             continue
#         if line.count(',') == 21:
#             line = line.replace(',', '/', 3).replace('/', ',', 2)
#     return '\n'.join(newLines)

def normalize_fce(data):
    KEY_MAP = {
        'Resp. Rate %': 'resp_rate',
        'Course Name': 'name',
        'Year': 'year',
        'Responses': 'responses',
        'Enrollment': 'enrollment',
        'Questions': 'questions'
    }
    newData = []
    for elem in data:
        _elem = {}
        for key, value in elem.items():
            if key in KEY_MAP:
                _elem[KEY_MAP[key]] = 




def parse_table(table):
    rows = table
    columns = []
    result = []
    question_start = 0

    for row in rows:
        cells = row
        if 'Year of' in cells[5]:
            continue
            
        if len(cells) > 0 and cells[0] == 'Semester':
            # Columns are not consistent in a table - update them when
            # new labels are found.
            columns = [lbl.strip() for lbl in row if lbl.strip()]
            question_start = next((i for i, col in enumerate(columns)
                                   if col[0].isdigit()), len(columns))
        else:
            # Remove empty cells
            cells = cells[:len(columns)]

            # Build object to represent this section
            obj = {}
            questions = {}
            for index, cell in enumerate(cells):
                # Parse cell value
                value = cell
                if not value:
                    continue

                value = value.strip()

                if index < question_start:
                    if value.isdigit():
                        if columns[index] == 'Course ID':
                            if len(value) == 4:
                                value = '0' + value
                            value = value[:2] + '-' + value[2:]
                        else:
                            value = int(value)
                    elif index == question_start - 1:
                        try:
                            value = float(value)
                        except:
                            value = float(value.strip('%')) / 100.0
                    obj[columns[index]] = value
                else:
                    if value:
                        value = float(value)
                    questions[columns[index]] = value

            obj['Questions'] = questions
            result.append(obj)

    return result


def get_fce(path):
    data = open_csv(path)
    result = parse_table(data)
    return result


def test_fixCsv():
    s = """
Spring,2016,JOSEPH RUDMAN, Dietrich College of Humanities and Social Sciences,73270,WRITING FOR ECONOMST,B,Lect,7,19,37%,5.00,3.71,3.71,3.86,4.14,3.86,3.43,3.43,3.43,3.00

Spring,2016,JOACHIM GROEGER, Dietrich College of Humanities and Social Sciences,73274,ECONOMETRICS I,1,Lect,12,20,60%,10.00,4.33,3.08,3.00,3.17,4.08,2.92,4.58,3.58,2.25


Spring,2016,GASPER, J.  (co-taught), Dietrich College of Humanities and Social Sciences,73327,ADVTOPMACROREALBUSCY,W,Lect,4,5,80%,6.50,4.50,4.50,4.50,4.50,4.50,4.50,5.00,4.75,4.75

Spring,2016,KYDLAND, F.  (co-taught), Dietrich College of Humanities and Social Sciences,73327,ADVTOPMACROREALBUSCY,W,Lect,4,5,80%,7.25,4.50,4.50,4.50,4.50,4.50,4.75,5.00,4.75,4.50
"""

    # print(fixCsv(s))

