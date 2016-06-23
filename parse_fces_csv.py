import json
import csv
import re


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


#
# @brief      Normalizes the FCE data from it's original format. # #
#
# @param      data  [{}]: The output of parse_table(). Array of data which #
#                   represents FCE data by section. # #
#
# @return     [{}]: Normalize array of data which represents FCE data. #
#
def normalize_fce(data):
    KEY_MAP = {
        'Course ID': 'courseid',
        'Course Name': 'name',
        'Dept': 'department',
        'Enrollment': 'enrollment',
        'Instructor': 'instructor',
        'Resp. Rate %': 'resp_rate',
        'Responses': 'responses',
        'Section': 'section',
        'Semester': 'semester',
        'Type': 'type',
        'Year': 'year',
        'Questions': 'questions'
    }
    newData = []
    for doc in data:
        newDoc = {}
        for key, value in doc.items():
            if key in KEY_MAP:
                newDoc[KEY_MAP[key]] = value
            else:
                newDoc[key] = value
        if 'questions' in newDoc:
            questions = newDoc['questions']
            newQuestions = {}
            for key, value in questions.items():
                match = re.search('(\d+):', key)
                i = 100
                if match:
                    questionNum = match.group(1)
                    questionBody = re.sub('(\d+):', '', key).strip()
                else:
                    questionNum = str(i)
                    questionBody = key
                    i += 1
                newQuestions[questionNum] = {'body': questionBody,
                                             'value': value}
            newDoc['questions'] = newQuestions
        newData.append(newDoc)
    return newData


# @function parse_table
# @brief      Parses FCE data from a parsed CSV file.
#
# @param      table  2D list of the CSV file.
#
# @return     [{}]: Array of data which represents FCE data by section.
#
def parse_table(table):
    rows = table
    columns = []
    result = []
    question_start = 0

    for row in rows:
        cells = row

        # Skip cells containing "Year of". That's the summary of the year.
        if 'Year of' in cells[5]:
            continue

        # Columns are not consistent in a table - update them when
        # new labels are found.
        if len(cells) > 0 and cells[0] == 'Semester':
            columns = [lbl.strip() for lbl in row if lbl.strip()]
            question_start = next((i for i, col in enumerate(columns)
                                   if col[0].isdigit()), len(columns))
        else:
            # Fix the csv by combining the name.
            if len(cells) > len(columns):
                cells[3] = cells[3].strip() + ', ' + cells[4].pop().strip()

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
    result = normalize_fce(parse_table(data))
    return result


def test_fixCsv():
    s = """
Spring,2016,JOSEPH RUDMAN, Dietrich College of Humanities and Social Sciences,73270,WRITING FOR ECONOMST,B,Lect,7,19,37%,5.00,3.71,3.71,3.86,4.14,3.86,3.43,3.43,3.43,3.00

Spring,2016,JOACHIM GROEGER, Dietrich College of Humanities and Social Sciences,73274,ECONOMETRICS I,1,Lect,12,20,60%,10.00,4.33,3.08,3.00,3.17,4.08,2.92,4.58,3.58,2.25


Spring,2016,GASPER, J.  (co-taught), Dietrich College of Humanities and Social Sciences,73327,ADVTOPMACROREALBUSCY,W,Lect,4,5,80%,6.50,4.50,4.50,4.50,4.50,4.50,4.50,5.00,4.75,4.75

Spring,2016,KYDLAND, F.  (co-taught), Dietrich College of Humanities and Social Sciences,73327,ADVTOPMACROREALBUSCY,W,Lect,4,5,80%,7.25,4.50,4.50,4.50,4.50,4.50,4.75,5.00,4.75,4.50
"""

    # print(fixCsv(s))

