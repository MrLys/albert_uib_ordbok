# -*- coding: utf-8 -*-

"""This is a simple python template extension.

This extension should show the API in a comprehensible way. Use the module docstring to provide a \
description of the extension. The docstring should have three paragraphs: A brief description in \
the first line, an optional elaborate description of the plugin, and finally the synopsis of the \
extension.

Synopsis: <trigger> [delay|throw] <query>"""
from albert import *
import os
import requests
import json
import re
import pickle

__title__ = "UiB Dictionary lookup"
__version__ = "0.0.2"
__triggers__ = "bm "
__authors__ = "mrlys"
__py_deps__ = ["requests", "json", "re", "pickle"]
#__exec_deps__ =

iconPath = iconLookup("albert")
db_file = '.db'


# Can be omitted
def initialize():
    pass


# Can be omitted
def finalize():
    pass


def strrepl(m):
    g = m.group()
    return '"' + g[0:-1] + '":'


to_json_pattern = re.compile(r'\w+:')
to_query_pattern = re.compile(r' \(\w+\)')


def to_json(data):
    s = data.replace("\'", '"').replace('\n', " ")
    return json.loads(to_json_pattern.sub(strrepl, s))


def to_uib_query(query):
    return re.sub(to_query_pattern, '', query)


def handleQuery(query):
    if not query.isTriggered:
        return

    # Note that when storing a reference to query, e.g. in a closure, you must not use
    # query.isValid. Apart from the query beeing invalid anyway it will crash the appplication.
    # The Python type holds a pointer to the C++ type used for isValid(). The C++ type will be
    # deleted when the query is finished. Therfore getting isValid will result in a SEGFAULT.

    if not len(query.string) > 2:
        item = Item()
        item.icon = iconPath
        item.text = '%s' % query.string
        item.subtext = 'At least 3 characters'
        return [item]
    db = {}
    if os.path.exists(db_file):
        debug("db file exists")
        infile = open(db_file, 'rb')
        db = pickle.load(infile)
        infile.close()
        debug("db: " + str(db))
    info(query.string)
    info(query.rawString)
    info(query.trigger)
    info(str(query.isTriggered))
    info(str(query.isValid))

    critical(query.string)
    warning(query.string)
    debug(query.string)
    debug(query.string)

    results = []
    db_dict = {}
    if query.string in db:
        res = db[query.string]
    else:
        res = requests.get(
            'https://ordbok.uib.no/perl/lage_ordliste_liten_nr2000.cgi?spr=begge&query=%s' % query.string)
        json_result = to_json(res.text)
        info(json_result)
        data = json_result['suggestions']
        db[query.string] = data
    data = db[query.string]
    if data:
        for unit in data:
            item = Item(id=__title__,
                        icon=os.path.dirname(__file__) + "/uib_ordbok.png",
                        text='%s' % unit,
                        subtext="Suggestion",
                        completion=__triggers__ + '%s' % unit,
                        urgency=ItemBase.Notification,
                        actions=[UrlAction(
                            text='Open in web',
                            url='https://ordbok.uib.no/perl/ordbok.cgi?OPP=%s&ant_bokmaal=5&ant_nynorsk=5&begge=+&ordbok=begge' % to_uib_query(unit))])
            results.append(item)

    results.append(item)

    # Api v 0.2
    info(configLocation())
    info(cacheLocation())
    info(dataLocation())
    outfile = open(db_file, 'wb')
    pickle.dump(db, outfile)
    outfile.close()
    return results
