# @author Justin Chu (justinchuby@cmu.edu)
# @since 2016-06-23
# 


import os
import json
from nameparser import HumanName


QUESTIONS_MAP = {
    'Hrs Per Week 9': 'Q-01',
    'Interest in student learning': 'Q-02',
    'Explain course requirements': 'Q-03',
    'Clear learning goals': 'Q-04',
    'Feedback to students': 'Q-05',
    'Importance of subject': 'Q-06',
    'Explains subject matter': 'Q-07',
    'Show respect for students': 'Q-08',
    'Overall teaching': 'Q-09',
    'Overall course': 'Q-10',
}


def open_file(path):
    with open(path, "rt") as f:
        return f.read()


def write_file(path, contents):
    with open(path, "wt") as f:
        f.write(contents)


class Course(dict):
    def __init__(self, d, mini_q=True):
        self['year'] = d.get('year')
        self['department'] = d.get('department')
        self['courseid'] = d.get('courseid')
        self['co_taught'] = d.get('co_taught')
        self['section'] = d.get('section')
        self['responses'] = d.get('responses')
        self['resp_rate'] = d.get('resp_rate')
        self['name'] = d.get('name')
        self['enrollment'] = d.get('enrollment')
        self['semester'] = d.get('semester')
        self['questions'] = d.get('questions')
        if mini_q:
            self['questions'] = minimize_questions(self['questions'])


class Instructor(dict):
    def __init__(self, name):
        self['name'] = name
        humanName = HumanName(name)
        self['first_name'] = humanName.first
        self['last_name'] = humanName.last
        # self.andrewid = ""
        self['courses'] = []


def load_fces(paths):
    data = []
    for path in paths:
        file = open_file(path)
        data += json.loads(file)
    return data


def catogorize_by_instructor(data):
    instructorsDict = {}
    for fce in data:
        if 'instructor' in fce and len(fce['instructor']) > 2:
            name = HumanName(fce['instructor'])
            name.capitalize()
            instructor = "{} {}".format(name.first, name.last).strip()
            if len(instructor) > 2:
                course = Course(fce)
                if instructor in instructorsDict:
                    instructorsDict[instructor]['courses'].append(course)
                else:
                    instructorsDict[instructor] = Instructor(str(name))
                    instructorsDict[instructor]['courses'].append(course)
    return instructorsDict


def minimize_questions(questions):
    global QUESTIONS_MAP
    if questions is not None:
        for key, question in questions.items():
            body = question['body']
            if body in QUESTIONS_MAP:
                questions[key]['body'] = QUESTIONS_MAP[body]
    return questions


def main(inpaths, outpath):
    data = load_fces(inpaths)
    data = catogorize_by_instructor(data)
    if not outpath.endswith('.json'):
        outpath += '.json'
    write_file(outpath, json.dumps(data, indent=2, sort_keys=True))
