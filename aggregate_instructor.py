# @author Justin Chu (justinchuby@cmu.edu)
# @since 2016-06-23
# 



import json
import re
from nameparser import HumanName


def open_file(path):
    with open(path, "rt") as f:
        return f.read()


def write_file(path, contents):
    with open(path, "wt") as f:
        f.write(contents)


class Course(dict):
    def __init__(self, d):
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

    # def __repr__(self):
    #     return repr(self.__dict__)

    # def get(self, key, default=None):
    #     return self.__dict__.get(key, default)


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
        if 'instructor' in fce:
            name = HumanName(fce['instructor'])
            name.capitalize()
            instructor = "{} {}".format(name.first, name.last).strip()
            course = Course(fce)
            if instructor in instructorsDict:
                instructorsDict[instructor]['courses'].append(course)
            else:
                instructorsDict[instructor] = Instructor(str(name))
                instructorsDict[instructor]['courses'].append(course)
    return instructorsDict

