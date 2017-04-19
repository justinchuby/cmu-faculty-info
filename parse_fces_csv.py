# @author Justin Chu (justinchuby@cmu.edu)
# @since 2016-06-23
# 
# parse_table() adapted from course-api by ScottyLabs. The MIT License, Copyright (c) 2014 ScottyLabs


import json
import re
import os
import cmu_course_api


def open_file(path):
    with open(path, "rt") as f:
        return f.read()


def write_file(path, contents):
    with open(path, "wt") as f:
        f.write(contents)


QUESTIONS_MAP = {
    'hrs per week': 'Q-01',
    'interest in student learning': 'Q-02',
    'explain course requirements': 'Q-03',
    'clear learning goals': 'Q-04',
    'feedback to students': 'Q-05',
    'instructor provides feedback to students': 'Q-05',
    'importance of subject': 'Q-06',
    'explains subject matter': 'Q-07',
    'show respect for students': 'Q-08',
    'overall teaching': 'Q-09',
    'overall course': 'Q-10',
}


def minimize_questions(questions):
    global QUESTIONS_MAP
    if questions is not None:
        for key, question in questions.items():
            body = question['body']
            body_lower = body.lower()
            if body_lower in QUESTIONS_MAP:
                questions[key]['body'] = QUESTIONS_MAP[body_lower]
            elif 'hrs per week' in body_lower:
                questions[key]['body'] = 'Q-01'
    return questions


#
# @brief      Normalizes the FCE data from it's original format. # #
#
# @param      data  [{}]: The output of parse_table(). Array of data which #
#                   represents FCE data by section. # #
#
# @return     [{}]: Normalize array of data which represents FCE data. #
#
def normalize_fce(data, min_questions=True):
    KEY_MAP = {
        'course id': 'courseid',
        'course name': 'name',
        'dept': 'department',
        'enrollment': 'enrollment',
        'instructor': 'instructor',
        'resp. rate %': 'resp_rate',
        'responses': 'responses',
        'section': 'section',
        'semester': 'semester',
        'type': 'type',
        'year': 'year',
        'questions': 'questions'
    }
    newData = []
    for doc in data:
# TODO: Need None value for non-exist fields?
        newDoc = {}
        newDoc['co_taught'] = False

        for key, value in doc.items():
            key_lower = key.lower()
            if key_lower in KEY_MAP:
                newDoc[KEY_MAP[key_lower]] = value
            else:
                newDoc[key_lower] = value
        # See if the course is co-taught by this instructor
        try:
            if 'co-taught' in newDoc['instructor']:
                newDoc['instructor'] = newDoc['instructor'].replace('(co-taught)', '').strip()
                newDoc['co_taught'] = True
        except KeyError:
            pass

        if 'questions' in newDoc:
            questions = newDoc['questions']
            newQuestions = {}
            for key, value in questions.items():
                match = re.search('(\d+):(.*)', key)
                if match:
                    questionNum = match.group(1)
                    questionBody = match.group(2).strip()
                    newQuestions[questionNum] = {'body': questionBody,
                                                 'value': value}
                # This drops questions without a leading number.
            if min_questions:
                newQuestions = minimize_questions(newQuestions)
            newDoc['questions'] = newQuestions
        newData.append(newDoc)
    return newData


# @deprecated Use cmu_course_api.parse_fces() instead. Use when cmu_course_api
#             is not availible.
#
# @function parse_table
#
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
        if cells[0] == '' or 'Year of' in cells[5]:
            continue

        # Columns are not consistent in a table - update them when
        # new labels are found.
        if len(cells) > 0 and cells[0] == 'Semester':
            columns = [lbl.strip() for lbl in row if lbl.strip()]
            question_start = next((i for i, col in enumerate(columns)
                                   if col[0].isdigit()), len(columns))
        else:
            try:
                if cells[len(columns)] != '':
                    # Fix the csv by combining the name
                    cells[3] = cells[3].strip() + ', ' + cells.pop(4).strip()
            except IndexError:
                pass
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
                        elif columns[index] != 'Section':
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


def get_fce(path, min_questions=True):
    data = cmu_course_api.parse_fces(path)
    result = normalize_fce(data, min_questions)
    return result


def main(indir, outdir, index="fce"):
    assert(os.path.isdir(indir) and os.path.isdir(outdir))
    files = os.listdir(indir)
    csvList = []
    for i in range(len(files)):
        if files[i].endswith('.csv'):
            csvList.append(files[i])
    for file in csvList:
        print(file)
        inpath = os.path.join(indir, file)
        outpath_json = os.path.join(outdir, re.sub('\.csv$', '.json', file))
        outpath_es = os.path.join(outdir, re.sub('\.csv$', '_es.json', file))
        fces = get_fce(inpath, min_questions=True)
        output_json = json.dumps(fces, indent=2, sort_keys=True)
        output_es = generate_es_command(fces, index, "fce")
        write_file(outpath_json, output_json)
        write_file(outpath_es, output_es)


def hash_fce_doc(fce_doc):
    import hashlib
    hashdict = dict()
    hashdict['instructor'] = fce_doc.get('instructor')
    hashdict['semester'] = fce_doc.get('semester')
    hashdict['year'] = fce_doc.get('year')
    hashdict['courseid'] = fce_doc.get('courseid')
    hashdict['section'] = fce_doc.get('section')
    ID = hashlib.md5(str(sorted(hashdict.items())).encode('utf-8')).hexdigest()[:10]
    return ID


def generate_es_command(fces, index, typ):
    output = ""
    for doc in fces:
        ID = hash_fce_doc(doc)
        output += '{ "index" : { "_index" : "%s", "_type" : "%s", "_id" : "%s" } }\n' % (index, typ, ID)
        output += str(json.dumps(doc)) + "\n"
    return output

