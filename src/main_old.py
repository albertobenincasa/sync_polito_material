import json
import os

from polito_sync import PolitoWebClass
#import PolitoWebClass

if __name__ == "__main__":
    session = PolitoWebClass()

    settings = None

    try:
        with open(".settings.json") as s:
            settings = json.load(s)
    except:
        print("Error: rename settings file as settings.json")

    session.set_download_folder(settings['download_folder'])

    session.set_file_name('web')

    if settings['credentials']['enabled']:
        session.login(settings['credentials']['username'], settings['credentials']['password'])
    else:
        session.login()

    session.menu()