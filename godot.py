# -*- coding: utf-8 -*-

"""Open Godot projects.

Synopsis: <trigger> <filter>"""

import os
import re
from shutil import which

from albertv0 import ProcAction, Item, iconLookup

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Godot Projects"
__version__ = "1.0"
__trigger__ = "godot "
__author__ = "Patrick Wuttke"
__dependencies__ = []

if which("godot") is None:
    raise Exception("'godot' is not in $PATH.")

iconPath = iconLookup('godot')
project_path_regex = re.compile('^(?:"projects\\/[^"]*"|projects\\/\\S*)\\s*=\\s*"(?P<path>[^"]*)"$')
project_name_regex = re.compile('^config\\/name\\s*=\\s*"(?P<value>[^"]*)"$')
project_icon_regex = re.compile('^config\\/icon\\s*=\\s*"(?P<value>[^"]*)"$')
projects_file = os.path.join(os.environ['HOME'], '.config/godot/editor_settings-3.tres')

mtime = 0
projects = []


def updateProjects():
    global mtime
    try:
        new_mtime = os.path.getmtime(projects_file)
    except Exception as e:
        warning("Could not get mtime of file: " + projects_file + str(e))
    if mtime != new_mtime:
        mtime = new_mtime
        genProjectList()

def genProjectList():
    global projects

    projects = []
    with open(projects_file, 'r') as fp:
        for line in fp:
            match = project_path_regex.match(line.rstrip())
            if match:
                project_path = match.group('path')
                projects.append(parseProject(project_path))

def parseProject(project_path):
    project = {
        "name": os.path.basename(project_path),
        "path": project_path,
        "icon": iconPath
    }
    try:
        with open(os.path.join(project_path, "project.godot"), "r") as fp:
            for line in fp:
                sline = line.rstrip()
                match_name = project_name_regex.match(sline)
                if match_name:
                    project["name"] = match_name.group("value")
                    continue
                match_icon = project_icon_regex.match(sline)
                if match_icon:
                    project["icon"] = match_icon.group("value")
    except Exception as e:
        print(e)
    if project["icon"].startswith("res://"):
        project["icon"] = os.path.join(project_path, project["icon"][6:])
    return project

def handleQuery(query):
    if not query.isTriggered:
        return
    
    search = query.string.lower()
    found_name = []
    found_path = []

    updateProjects()

    for project in projects:
        if search in project["name"].lower():
            found_name.append(project)
        elif search in project["path"].lower():
            found_path.append(project)
    
    results = []
    for project in found_name + found_path:
        search_regex = re.compile("(%s)" % re.escape(query.string), re.IGNORECASE)
        
        results.append(
            Item(
                id="godot_%s" % project["path"],
                icon=project["icon"],
                text=search_regex.sub("<u>\\1</u>", project["name"]),
                subtext=search_regex.sub("<u>\\1</u>", project["path"]),
                completion=query.rawString,
                actions=[
                    ProcAction(text="Open Editor", commandline=['godot', '--path', project['path'], '--editor']),
                    ProcAction(text="Run Project", commandline=['godot', '--path', project['path']])
                ]
            )
        )
    return results
