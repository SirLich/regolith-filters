import os
import re
import json
import sys
import requests
from datetime import datetime
import urllib.request
import shutil
from pathlib import Path

# TODO: Add this somewhere
# <div>Icons made by <a href="https://www.flaticon.com/authors/pixel-perfect" title="Pixel perfect">Pixel perfect</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QSizePolicy, QWidget, QPushButton, QHBoxLayout, QLabel, \
                                QVBoxLayout, QTabWidget, QScrollArea, QFrame, \
                                QLineEdit, QStackedWidget, QLineEdit, QComboBox

from PySide2.QtGui import QIcon, QFont, QTextLine, Qt
from PySide2.QtCore import QSize

IGNORED_FOLDERS = ["settings", "__pycache__", "images"]
FOLDER_INDENT = 10
FILE_INDENT = 13

path = os.path.join(os.getcwd(), "example.lang")
outpath = os.path.join(os.getcwd(), "out.json")
outpath2 = os.path.join(os.getcwd(), "out2.json")

# Interact with the configuration file (get/set values)
class ConfigManager():
    # Static Methods

    @staticmethod
    # Nasty method for code-compatibility. Some examples:
    # - en_US -> en-us
    # - en-us -> en_US
    # - de_DE -> de
    # - de -> de_DE
    # 
    # The thing to note here is that all "double" (fr_FR) languages are just single in PO.
    def convert_language_code(code):
        print(code)
        if "_" in code:
            out = code.replace("_", "-").lower()
            split = out.split("-")
            print(split)
            if len(split) > 1 and out[0] == out[1]:
                out = split[0]
            return out
        elif "-" in code:
            out = code.replace("-", "_")
            split = out.split("_")
            print(split)
            return split[0] + "_" + split[1].upper()
        else:
            return code + "_" + code.upper()
        

    @staticmethod
    def get_api_token():
        return str(ConfigManager.fetch_config().get("global_settings", {}).get("api_token", "No API token set. Use the edit button to set one."))
        
    @staticmethod
    def get_project_languages(project_name):
        languages = []
        path = os.path.join(ConfigManager.fetch_config().get("projects").get(project_name).get("path"), "texts")
        for lang_name in os.listdir(path):
            if lang_name.endswith(".lang"):
                languages.append(lang_name.replace(".lang", ""))
        return languages

    @staticmethod
    def get_com_mojang_folder():
        user = os.getlogin()
        return "C:\\Users\\{}\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\".format(user)

    @staticmethod
    def get_project_by_name(project_name):
        return ConfigManager.fetch_config().get("projects").get(project_name)

    @staticmethod
    def get_all_project_names():
        keys = list(ConfigManager.fetch_config().get("projects").keys())
        keys.sort()
        return keys

    @staticmethod
    def archive_file(path):
        now = str(datetime.now())[:19]
        now = now.replace(":","_")
        
        destination = os.path.join(os.getcwd(), "polang", "archive", os.path.basename(path) + "_" + "" + now + ".lang")        
        if(os.path.exists(path)):
            shutil.copy(path,destination)

    @staticmethod
    def fetch_config():
        with open(os.path.join(os.getcwd(), "polang", "config.json"), "r") as f:
            return json.load(f)
    
    @staticmethod
    def save_config(data):
        with open(os.path.join(os.getcwd(), "polang", "config.json"), 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def get_url(url):
        return ConfigManager.fetch_config().get("urls").get(url, "Invalid URL type")

    @staticmethod
    def create_config_if_missing():
        base = os.path.join(os.getcwd(), "polang")
        config_path = os.path.join(base, "config.json")
        Path(os.path.join(base, "archive")).mkdir(parents=True, exist_ok=True)

        if not os.path.exists(config_path):
            with open(config_path, 'w+') as f:
                data = {
                    "urls": {
                        "list_projects": "https://api.poeditor.com/v2/projects/list",
                        "export": "https://api.poeditor.com/v2/projects/upload",
                        "import": "https://api.poeditor.com/v2/projects/export",
                        "list_languages": "https://api.poeditor.com/v2/languages/list",
                        "add_language": "https://api.poeditor.com/v2/languages/add",
                        "add_project": "https://api.poeditor.com/v2/projects/add"
                    },
                    "global_settings": {
                        "api_token": "Please set your API token!"
                    },
                    "language_names": [
                        "en_US",
                        "en_GB",
                        "de_DE",
                        "es_ES",
                        "es_MX",
                        "fr_FR",
                        "fr_CA",
                        "it_IT",
                        "ja_JP",
                        "ko_KR",
                        "pt_BR",
                        "pt_PT",
                        "ru_RU",
                        "zh_CN",
                        "zh_TW",
                        "nl_NL",
                        "bg_BG",
                        "cs_CZ",
                        "da_DK",
                        "el_GR",
                        "fi_FI",
                        "hu_HU",
                        "id_ID",
                        "nb_NO",
                        "pl_PL",
                        "sk_SK",
                        "sv_SE",
                        "tr_TR",
                        "uk_UA"
                    ],
                    "projects": {
                    }
                }
                json.dump(data, f, indent=2)

    @staticmethod
    def generate_project_list():
        folder = ConfigManager.get_com_mojang_folder()
        data = ConfigManager.fetch_config()

        project_names = os.listdir(os.path.join(folder, "development_resource_packs"))
        project_names.sort()
        index = 1

        for name in project_names:
            print(name)
            if data["projects"].get(name) == None:
                data["projects"][name] = {
                    "index": index,
                    "type": "BP",
                    "primary_language": "en_US",
                    "id": "Please set an ID",
                    "name": name,
                    "path": os.path.join(folder, "development_resource_packs", name)
                }
                index += 1
        ConfigManager.save_config(data)
    
    @staticmethod
    def set_project_id(project_name, id):
        data = ConfigManager.fetch_config()
        data["projects"][project_name]["id"] = id
        ConfigManager.save_config(data)

    @staticmethod
    def set_api_token(token):
        data = ConfigManager.fetch_config()
        data["global_settings"]["api_token"] = token
        ConfigManager.save_config(data)


    @staticmethod
    def set_primary_language(project_name, language):
        data = ConfigManager.fetch_config()
        data["projects"][project_name]["primary_language"] = language
        ConfigManager.save_config(data)

    @staticmethod
    def get_all_language_names():
            data = ConfigManager.fetch_config()
            return data.get("language_names", ["No results!"])

    @staticmethod
    def get_project_field(project_name, field):
        return str(ConfigManager.fetch_config().get("projects", {}).get(project_name, {}).get(field, "Field could not be found"))

class QHLine(QFrame):
    """A horizontal line, intended for organizing widgets"""

    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class QVLine(QFrame):
    """A vertical line, intended for organizing widgets"""

    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

class QTitle(QLabel):
    """A large font-size text, intended to be used as titles"""

    def __init__(self, title):
        super(QTitle, self).__init__()
        self.setText(title)
        font = QFont("Helvetica")
        font.setPointSize(15)
        self.setFont(font)
        

class QTranslateTab(QWidget):
    """
    TabWidget page: The top level page where translations occur
    
    Additional pages are planned, but currently there is only a single, top-level page.
    """

    def __init__(self):
        super(QTranslateTab, self).__init__()
            
        translate_tab = QWidget()

        stacked_layout = QVBoxLayout()
        stacked_widget = QStackedWidget()
        stacked_layout.addWidget(stacked_widget)

        # Add widgets
        stacked_widget.addWidget(QTranslateAllProjectView(stacked_widget))

        for item in ConfigManager.get_all_project_names():
            project = ConfigManager.get_project_by_name(item)
            view = QTranslateProjectView(project, stacked_widget)
            view.setObjectName(project.get("name"))
            stacked_widget.addWidget(view)


        # End add widgets
        stacked_widget.setCurrentIndex(0)

        translate_tab.setLayout(stacked_layout)

        self.setLayout(stacked_layout)

class QIconButton(QPushButton):
    """"Simply wrapper for making icon-only buttons"""
    def __init__(self, icon_path, size=24, text=""):
        super(QIconButton, self).__init__(text)
        
        self.setIcon(QIcon(icon_path))
        self.styleSheet()
        # self.setIconSize(QSize(size,size))
        # self.setMaximumSize(size,size)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

class QProjectButton(QIconButton):
    def is_clicked(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.findChild(QTranslateProjectView, self.project.get("name")))

    def __init__(self, project, stacked_widget):
        super(QProjectButton, self).__init__('./images/menu.png', text=project.get("name"))
        
        self.stacked_widget = stacked_widget
        self.project = project
        self.clicked.connect(self.is_clicked)

# TODO: Rework this into a generic widget.
class QGeneralSettingsArea(QWidget):
    """Settings area, for all projects. Currently has option to set API token."""

    def set_editable(self):
        self.line.setDisabled(False)
        self.edit_button.setHidden(True)
        self.save_button.setHidden(False)
        self.cancel_button.setHidden(False)
    
    def save_edit(self):
        ConfigManager.set_api_token(self.line.text())
        self.project["id"] = self.line.text()
        self.line.setDisabled(True)
        self.edit_button.setHidden(False)
        self.save_button.setHidden(True)
        self.cancel_button.setHidden(True)

    def cancel_edit(self):
        self.line.setDisabled(True)
        self.line.setText(ConfigManager.get_api_token())
        self.edit_button.setHidden(False)
        self.save_button.setHidden(True)
        self.cancel_button.setHidden(True)

    def __init__(self):
        super(QGeneralSettingsArea, self).__init__()
        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        edit_row = QWidget()
        row = QHBoxLayout()
        row.setAlignment(QtCore.Qt.AlignLeft)
        self.line = QLineEdit(self)
        self.line.setDisabled(True)
        self.line.setText(ConfigManager.get_api_token())
        row.addWidget(QLabel("API Token: "))
        row.addWidget(self.line)

        self.edit_button = QIconButton('./images/edit.png', text="Edit")
        self.edit_button.clicked.connect(self.set_editable)

        self.save_button = QIconButton('./images/save.png', text="Save")
        self.save_button.clicked.connect(self.save_edit)
        self.save_button.setHidden(True)
        
        self.cancel_button = QIconButton('./images/cancel.png', text="Cancel")
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.cancel_button.setHidden(True)

        row.addWidget(self.edit_button)
        row.addWidget(self.save_button)
        row.addWidget(self.cancel_button)


        edit_row.setLayout(row)
        row.setContentsMargins(0,0,0,0)
        layout.addWidget(edit_row)

        self.setLayout(layout)

class QTranslateAllProjectView(QWidget):
    """The main view for the Translate tab. Shows all projects, and project-level settings."""
        
    def toggle_settings_view(self):
        self.settings_view.setHidden(not self.settings_view.isHidden())

    def __init__(self, stacked_widget):
        super(QTranslateAllProjectView, self).__init__()

        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        settings_box = QHBoxLayout()
        settings_box.setAlignment(QtCore.Qt.AlignLeft)
        settings_button = QIconButton('./images/settings.png', text="Global Settings")
        settings_button.clicked.connect(self.toggle_settings_view)
        settings_box.addWidget(settings_button)

        layout.addLayout(settings_box)

        self.settings_view = QGeneralSettingsArea()
        self.settings_view.setHidden(True)
        layout.addWidget(self.settings_view)

        layout.addWidget(scroll_area)

        project_widget_list = QWidget()
        project_box = QVBoxLayout()
        for item in ConfigManager.get_all_project_names():
            project = ConfigManager.get_project_by_name(item)
            slot = QHBoxLayout()
            slot.setAlignment(QtCore.Qt.AlignLeft)
            view_button = QProjectButton(project, stacked_widget)

            slot.addWidget(view_button)
            project_box.addLayout(slot)
        
        project_widget_list.setLayout(project_box)
        scroll_area.setWidget(project_widget_list)

        self.setLayout(layout)

class QTranslateProjectView(QWidget):
    """Translate tab view for a single project."""

    def add_project(self):
        url = ConfigManager.get_url("add_project")
        data = {
            'api_token': ConfigManager.get_api_token(),
            'name': self.project.get("name"),
            'description': 'Projected created automatically by Polang!'
        }

        response = requests.post(url, data=data)
        self.log_message(response.text)

        id = data.get("result", {}).get("project", {}).get("id", "ID Failed to set Automatically")

        self.id_form.setText(id)

    def add_language(self):
        url = ConfigManager.get_url("add_language")
        language = self.add_language_form.currentText()

        data = {
            'api_token': ConfigManager.get_api_token(),
            'id': self.project.get("id"),
            'language': ConfigManager.convert_language_code(language)
        }
        
        response = requests.post(url, data=data)
        self.log_message(response.text)

    def log_message(self, data):
        time_expression = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        self.text_log.setText(time_expression + "\n" + data + "\n\n" + self.text_log.text())
        self.text_log.adjustSize();

    def list_languages(self):
        url = ConfigManager.get_url("list_languages")

        data = {
            'api_token': ConfigManager.get_api_token(),
            'id': self.project.get("id"),
        }
        
        response = requests.post(url, data=data)
        self.log_message(response.text)

        languages = []
        
        for language in json.loads(response.text).get("result", {}).get("languages", []):
            languages.append(language.get("code"))
        
        return languages

    def list_projects(self):
        url = ConfigManager.get_url("list_projects")

        data = {
            'api_token': ConfigManager.get_api_token()
        }
        
        response = requests.post(url, data=data)
        self.log_message(response)

    def import_translations(self):
        url = ConfigManager.get_url("import")

        languages = self.list_languages()

        print(languages)
        for language in languages:

            print(language)
            data = {
                'api_token': ConfigManager.get_api_token(),
                'id': self.project.get("id"),
                'type': 'json',
                'language': language
            }

            print(data)
            response = requests.post(url, data=data)
            self.log_message(response.text)

            response_url = json.loads(response.text).get("result", {}).get("url", "")

            po_translations = {}

            print(response_url)
            try:
                with urllib.request.urlopen(response_url) as f:
                    po_translations = json.loads(f.read().decode('utf-8'))

            except urllib.error.URLError as e:
                print(e.reason)
            
            save_lang(self.project, ConfigManager.convert_language_code(language), po_translations)

        
    # Export FROM com.mojang folder INTO the PO Editor!
    def export_translations(self):
        url = ConfigManager.get_url("export")
        language = self.language_form.currentText()
        terms = create_terms(self.project, language)

        open(outpath, "r")

        files = {
            'file': terms
        }

        data = {
            'api_token': ConfigManager.get_api_token(),
            'id': self.project.get("id"),
            'updating': 'terms_translations',
            'sync_terms': 1,
            'language': ConfigManager.convert_language_code(language)
        }

        response = requests.post(url, files=files, data=data)

        terms.close()

        self.log_message(response.text)
        print(response.elapsed)
        print(response.text)

    def set_editable(self):
        self.settings_area.setDisabled(False)
        self.edit_button.setHidden(True)
        self.cancel_button.setHidden(False)
        self.save_button.setHidden(False)

    def save_edit(self):
        ConfigManager.set_project_id(self.project.get("name", ""), self.id_form.text())
        ConfigManager.set_primary_language(self.project.get("name", ""), self.language_form.currentText())
        self.settings_area.setDisabled(True)
        self.edit_button.setHidden(False)
        self.cancel_button.setHidden(True)
        self.save_button.setHidden(True)

    def cancel_edit(self):
        self.settings_area.setDisabled(True)
        self.edit_button.setHidden(False)
        self.cancel_button.setHidden(True)
        self.save_button.setHidden(True)


    def home(self):
        self.stacked_widget.setCurrentIndex(0)

    def __init__(self,  project, stacked_widget):
        super(QTranslateProjectView, self).__init__()
        self.project = project
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        main_button_row = QHBoxLayout()
        main_button_row.setAlignment(QtCore.Qt.AlignLeft)

        home_button = QIconButton('./images/home.png', text="Home")
        home_button.clicked.connect(self.home)

        import_button = QIconButton('./images/import.png', text="Import")
        import_button.setToolTip("Import FROM PO Editor INTO your com.mojang folder")
        import_button.clicked.connect(self.import_translations)


        export_button = QIconButton('./images/export.png', text = "Export")
        export_button.setToolTip("Export FROM your com.mojang INTO the PO Editor")
        export_button.clicked.connect(self.export_translations)

        main_button_row.addWidget(home_button)
        main_button_row.addWidget(import_button)
        main_button_row.addWidget(export_button)

        
        # =-=-=-=

        settings_button_row = QHBoxLayout()
        settings_button_row.setAlignment(QtCore.Qt.AlignLeft)

        self.edit_button = QIconButton('./images/edit.png', text="Edit")
        self.edit_button.clicked.connect(self.set_editable)

        self.save_button = QIconButton('./images/save.png', text="Save")
        self.save_button.clicked.connect(self.save_edit)
        self.save_button.setHidden(True)

        self.cancel_button = QIconButton('./images/cancel.png', text="Cancel")
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.cancel_button.setHidden(True)

        layout.addLayout(main_button_row)
        layout.addWidget(QTitle(project.get("name")))
        layout.addWidget(QHLine())

        settings_button_row.addWidget(self.edit_button)
        settings_button_row.addWidget(self.save_button)
        settings_button_row.addWidget(self.cancel_button)

        layout.addLayout(settings_button_row)

        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(0,0,0,0)
        self.settings_area = QWidget()
        self.settings_area.setDisabled(True)

        self.settings_area.setLayout(settings_layout)

        id_row = QHBoxLayout()
        id_row.setAlignment(QtCore.Qt.AlignLeft)
        id_row.addWidget(QLabel("Project ID: "))

        self.id_form = QLineEdit(project.get("id"))
        id_row.addWidget(self.id_form)
        settings_layout.addLayout(id_row)

        # Language row
        language_row = QHBoxLayout()
        language_row.setAlignment(QtCore.Qt.AlignLeft)
        language_label = QLabel("Default Language: ")
        language_label.setToolTip("The primary language: New strings should be created in this language file")
        language_row.addWidget(language_label)

        self.language_form = QComboBox()
        self.language_form.addItems(ConfigManager.get_all_language_names())
        
        index = self.language_form.findText(ConfigManager.get_project_field(project.get("name"), "primary_language"), QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.language_form.setCurrentIndex(index)

        language_row.addWidget(self.language_form)
        settings_layout.addLayout(language_row)

        settings_layout.addWidget(QHLine())

        # Add Project
        add_project_row = QHBoxLayout()
        add_project_row.setAlignment(QtCore.Qt.AlignLeft)
        add_project_label = QLabel("Create new PO Editor project for this pack: ")
        add_project_label.setToolTip("Creates a new PO Editor project, and automatically configures ID.")
        add_project_row.addWidget(add_project_label)
        

        self.add_project_button = QIconButton('./images/run.png')
        self.add_project_button.clicked.connect(self.add_project)
        add_project_row.addWidget(self.add_project_button)

        settings_layout.addLayout(add_project_row)


        # Add language row
        add_language_row = QHBoxLayout()
        add_language_row.setAlignment(QtCore.Qt.AlignLeft)
        add_language_label = QLabel("Create new language: ")
        add_language_label.setToolTip("Adds a new language target to your PO editor project.")
        add_language_row.addWidget(add_language_label)
        
        self.add_language_form = QComboBox()
        self.add_language_form.addItems(ConfigManager.get_all_language_names())
        
        add_index = self.add_language_form.findText(ConfigManager.get_project_field(project.get("name"), "primary_language"), QtCore.Qt.MatchFixedString)
        if add_index >= 0:
            self.language_form.setCurrentIndex(add_index)

        add_language_row.addWidget(self.add_language_form)
        self.add_language_button = QIconButton('./images/run.png')
        self.add_language_button.clicked.connect(self.add_language)
        add_language_row.addWidget(self.add_language_button)

        settings_layout.addLayout(add_language_row)
        
        
        # Layout stuff
        layout.addWidget(self.settings_area)
        layout.addWidget(QHLine())

        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.text_log = QLabel()
        self.text_log.setWordWrap(True)
        self.text_log.setTextInteractionFlags(Qt.TextSelectableByMouse)
        scroll_area.setWidget(self.text_log)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

# TODO: What is this?
def make_line(term):
    line = ""
    for comment in term.get("comment", "").split("\n"):
        line += ("##" + comment + "\n")
    line += "{}={}".format(term.get("term"), term.get("definition"))

    return line

# TODO: What is this?
def make_term(line, reference, comment):
    term = {}

    pattern = '(.+?)=(.+)'
    result = re.match(pattern, line)

    if result:
        term["term"] = result.group(1)
        term["definition"] = result.group(2)
        term["comment"] = comment
        term["reference"] = reference

        return term

def save_lang(project, language, po_translations):
    path = os.path.join(project.get("path"), "texts", language + ".lang")

    ConfigManager.archive_file(path)

    with open(path, "w+") as lang:
        for term in po_translations:
            lang.write("{}={}\n".format(term.get("term"), term.get("definition")))



def create_terms(project, language):
    path = os.path.join(project.get("path"), "texts", language + ".lang")
    data= []
    terms = open(os.path.join(os.getcwd(), "temp.json"), 'w+')

    comment = ""
    
    with open(path, "r") as lang:
        for line in lang.readlines():
            line = line.strip()
            if line.startswith("#"):
                if comment != "":
                    comment += "\n"
                comment += line[1:]
            else:
                term = make_term(line, "", comment)
                if term:
                    data.append(term)
                    comment = ""
    
        json.dump( data, terms, ensure_ascii=False)

    terms.seek(0)
    return terms

def get_folder_structure(directory, items, indent):
    items = []
    for item in os.listdir(directory):
        new = os.path.join(directory, item)
        if item in IGNORED_FOLDERS or (not os.path.isdir(new) and not item.endswith(".json")):
            continue

        items.append({
            "item": item,
            "indent": indent,
            "is_folder": os.path.isdir(new)
        })

        if os.path.isdir(new) and item != "settings":
            items.extend(get_folder_structure(new, items, indent + 1))
    return items



# def list_textures_v2():
#     for texture in glob.glob("./textures/**/*.png")+glob.glob("./textures/**/*.tga"):
#         bn = os.path.splitext(os.path.basename(texture))[1]
#         print (texture.replace(bn,"").replace("./","").replace("\\","/"))


if __name__ == "__main__":
    ConfigManager.create_config_if_missing()
    ConfigManager.generate_project_list()

    app = QtWidgets.QApplication([])
    
    tabs = QTabWidget()
    tabs.addTab(QTranslateTab(), "Translate")

    tabs.resize(800,650)

    app.setStyleSheet(
        """
        QPushButton {
            border: 0px;
            border-radius: 10px;
            background-color: rgb(255, 255, 255);
        }
        """
    )

    tabs.show()
    sys.exit(app.exec_())