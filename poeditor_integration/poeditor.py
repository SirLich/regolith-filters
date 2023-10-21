import json
import os
import requests

# Constants
LIST_PROJECTS_URL = "https://api.poeditor.com/v2/projects/list"
EXPORT_URL = "https://api.poeditor.com/v2/projects/upload"
IMPORT_URL = "https://api.poeditor.com/v2/projects/export"
LIST_LANGUAGES_URL = "https://api.poeditor.com/v2/languages/list"
ADD_LANGUAGE_URL = "https://api.poeditor.com/v2/languages/add"
ADD_PROJECT_URL = "https://api.poeditor.com/v2/projects/add"

CONFIG_PATH = os.path.join(os.getcwd(), "data", "poeditor_integration", "config.json")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load()

def add_project(self, project_name: str) -> None:
    """
    Adds a new project into the PO-Editor account associated with the API token.
    """
    data = {
        'api_token': CONFIG.get("api_token"),
        'name': project_name,
        'description': 'Project created by PoEditorIntegration Filter!',
    }

    # TODO add response handling here
    response = requests.post(ADD_PROJECT_URL, data=data)


def add_language(self, language_code: str) -> None:
    """
    Adds a language into the project
    """
    url = ADD_LANGUAGE_URL
    language = self.add_language_form.currentText()

    data = {
        'api_token': CONFIG.get("api_token"),
        'id': CONFIG.get("project_id"),
        'language': convert_language_code(language_code)
    }
    
    # TODO add response handling here
    response = requests.post(url, data=data)

def list_languages(self):
    """
    Lists all languages associated with this project.
    """
    url = LIST_LANGUAGES_URL

    data = {
        'api_token': CONFIG.get("api_token"),
        'id': CONFIG.get("project_id")
    }
    
    response = requests.post(url, data=data)

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

def convert_language_code(code):
    """
    Converts back and forth between PO and Bedrock language codes.
    For example:
     - en_US -> en-us
     - en-us -> en_US
     - de_DE -> de
     - de -> de_DE

    Please note that all double (fr_FR) languages are just single in PO (fr)
    """
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

def get_project_languages(project_name):
    languages = []
    path = os.path.join(CONFIG.get("projects").get(project_name).get("path"), "texts")
    for lang_name in os.listdir(path):
        if lang_name.endswith(".lang"):
            languages.append(lang_name.replace(".lang", ""))
    return languages

def main():
    pass
    

if __name__ == "__main__":
    main()