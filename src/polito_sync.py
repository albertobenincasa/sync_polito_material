import subprocess
import requests
import getpass
import html
import json
import re
import os
import urllib

class PolitoWebClass:

    download_folder = None
    subjects_list = None
    login_cookie = None
    subject_cookie = None
    last_update_remote = None
    last_update_local = None
    file_name = 'file_name'

    headers = {'User-Agent': 'python-requests'}
    base_url = 'https://didattica.polito.it/pls/portal30/'
    handler_url = base_url + 'sviluppo.filemgr.handler'
    get_process_url = base_url + 'sviluppo.filemgr.get_process_amount'
    file_last_update = '.last_update'

    def __init__(self):
        print("-----------------------")
        print(" POLITO FILE DOWNLOADER ")
        print("-----------------------")

    def set_user_agent(self, user_agent):
        self.headers['User-Agent'] = user_agent

    def set_download_folder(self, download_folder):
        self._mkdir_if_not_exist(download_folder)
        self.download_folder = download_folder

    def set_file_name(self, file_name):
        if file_name == 'web':
            self.file_name = file_name
        elif file_name == 'file_name':
            self.file_name = 'file_name'

    def login(self, username=None, password=None):
        print("Credentials for http://didattica.polito.it")
        while not self._login(username, password):
            print("Login failed, try again!")
    
    def menu(self):
        while self._menu():
            self._clear()

    # PRIVATE

    def _login(self, username, password):
        if (username is None) and (password is None):
            user = input("Insert username: ")
            passw = getpass.getpass("Insert password: ")
        else:
            user = username
            passw = password

        print("Logging in...")

        with requests.session() as s:
            s.get('https://idp.polito.it/idp/x509mixed-login', headers=self.headers)
            r = s.post('https://idp.polito.it/idp/Authn/X509Mixed/UserPasswordLogin', 
                        data={'j_username': user, 'j_password': passw}, headers=self.headers)
            res = html.unescape(re.findall('name="RelayState".*value="(.*)"', r.text))

            if len(res) > 0:
                relay_state = res[0]
            else:
                return False

            saml_response = html.unescape(re.findall('name="SAMLResponse".*value="(.*)"', r.text)[0])
            s.post('https://www.polito.it/Shibboleth.sso/SAML2/POST',
                   data={'RelayState': relay_state, 'SAMLResponse': saml_response}, headers=self.headers)
            r = s.post('https://login.didattica.polito.it/secure/ShibLogin.php', headers=self.headers)

            relay_state = html.unescape(re.findall('name="RelayState".*value="(.*)"', r.text)[0])
            saml_response = html.unescape(re.findall('name="SAMLResponse".*value="(.*)"', r.text)[0])

            r = s.post('https://login.didattica.polito.it/Shibboleth.sso/SAML2/POST',
                       data={'RelayState': relay_state, 'SAMLResponse': saml_response}, headers=self.headers)

            if r.url == "https://didattica.polito.it/portal/page/portal/home/Studente":
                login_cookie = s.cookies
            else:
                return False

        # if i'm here, i'm logged!
        print("Successfully logged in! ")
        self.login_cookie = login_cookie
        return True

    def _get_subjects_list(self):
        with requests.session() as s:
            s.cookies = self.login_cookie
            hp = s.get('https://didattica.polito.it/portal/page/portal/home/Studente', headers=self.headers)
            # i take all the href of the subjects
            self.subjects_list = re.findall("cod_ins=(.+)&incarico=([0-9]+).+>(.+)[ ]*<", hp.text)

    def _select_subject(self, index):
        subject_name = self._purge_name(self.subjects_list[index][2])
        directory = os.path.join(self.download_folder, subject_name)
        self._mkdir_if_not_exist(directory)

        with requests.session() as s:
            s.cookies = self.login_cookie
            s.get('https://didattica.polito.it/pls/portal30/sviluppo.chiama_materia',
                  params={'cod_ins': self.subjects_list[index][0], 'incarico': self.subjects_list[index][1]},
                  headers=self.headers)
            
            self.subject_cookie = s.cookies
            self._get_path_content(directory, '/')

    def _get_path_content(self, folder, path, code='0'):
        with requests.session() as s:
            s.cookies = self.subject_cookie

            if code != '0':
                json_result = s.get(self.handler_url, params={'action': 'list', 'path': path, 'code': code},
                                     headers=self.headers)
            else:
                json_result = s.get(self.handler_url, params={'action': 'list', 'path': path},
                                     headers=self.headers)

            content = json_result.json()

            if path == '/':
                try:
                    folder_code = content['result'][0]['parent_code']
                    self._need_to_update(folder, folder_code)
                    self._save_update_file(folder)
                except :
                    pass

            for res in content['result']:
                
                if res['name'].startswith('ZZZZZ'):
                    # TO DO VIDEOLESSONS
                    continue
                
                if res['type'] == 'dir':
                    name = self._purge_name(res['name'])
                    folder_to_create = os.path.join(folder, name)

                    self._mkdir_if_not_exist(folder_to_create)
                    print('Folder: ' + name)
                    new_path = self._path_join(folder_to_create, name)

                    #recursion
                    self._get_path_content(folder_to_create, new_path, res['code'])

                elif res['type'] == 'file':
                    file_name = res['nomefile']

                    if self._need_to_update_this(folder, file_name, res['date']) and ".mp4" not in file_name:
                        print("[ DOWNLOAD ]" + file_name)
                        self._file_download(folder, file_name, path, res['code'])
                    else:
                        print("[ UPTODATE ]" + file_name)

    def _file_download(self, folder, name, path, code):
        with requests.session() as s:
            s.cookies = self.subject_cookie
            file = s.get(self.handler_url, params={'action': 'download', 'path': (path + '/' + name), 'code': code},
                         allow_redirects=True, headers=self.headers)
            try:
                name = self._purge_name(name)
                open(os.path.join(folder, name), 'wb').write(file.content)
            except ValueError:
                name = self._purge_name(name, 'strong')
                open(os.path.join(folder, name), 'wb').write(file.content)

    def _menu(self):
        if self.subjects_list is None:
            self._get_subjects_list()

        i = 1
        print('[00] Exit program')
        for subj in self.subjects_list:
            print('[%.2d] %s' % (i, subj[2]))
            i += 1

        x = -1
        while x not in range(1, i):
            x = input("Select subject: ")
            if x.isnumeric():
                x = int(x)
                if x == 0:
                    self._clear()
                    return
            else:
                continue

        self._select_subject(x - 1)

        print("Download finished, press ENTER to continue")
        input()
        return True

    def _last_update_remote(self, folder_code):
        with requests.session() as s:
            s.cookies = self.subject_cookie
            json_result = s.get(self.get_process_url, params={'items': folder_code})
            if json_result:
                json_result = json_result.json()
                self.last_update_remote = json_result['result']['lastUpload']
            else:
                print("Failed to load last update date")
                self.last_update_remote = None

    def _last_update_local(self, folder):
        check_file_nt = os.path.join(*[self.download_folder, folder, self.file_last_update])

        if os.path.isfile(check_file_nt):
            with open(check_file_nt, 'r') as f:
                self.last_update_local = f.read()
        else:
            self.last_update_local = None

    def _save_update_file(self, folder):
        updated_file = os.path.join(*[self.download_folder, folder, self.file_last_update])
        mode = 'r+' if os.path.isfile(updated_file) else 'w'

        with open(updated_file, mode) as f:
            f.write(self.last_update_remote)

    def _need_to_update(self, folder, folder_code):
        self._last_update_local(folder)
        self._last_update_remote(folder_code)
        if self.last_update_local is not None and self.last_update_remote is not None:
            if self.last_update_local < self.last_update_remote:
                return True
            else:
                return False
        else:
            return True 

    def _need_to_update_this(self, folder, file_name, data):
        file_name = self._purge_name(file_name)
        check_file = os.path.join(*[self.download_folder, folder, file_name])

        if not os.path.isfile(check_file):
            check_file = self._purge_name(file_name, 'strong')
            check_file = os.path.join(*[self.download_folder, folder, file_name])
            if not os.path.isfile(check_file):
                return True

        if self.last_update_local is None:
            return True

        if self.last_update_local < data:
            return True

        return False

    def _generate_video_url(self, code):
        url = None
        # base_url = "https://didattica.polito.it/portal/pls/portal/sviluppo.videolezioni.vis?cor="
        # base_url_e = "https://elearning.polito.it/gadgets/video/template_video.php?"
        return url

    # STATIC METHODS

    @staticmethod
    def _path_join(a, b):
        if a.endswith('/'):
            return a + b
        else:
            return a + '/' + b    

    @staticmethod
    def _mkdir_if_not_exist(folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    @staticmethod
    def _clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    def _purge_name(self, string, strong=None):
        if strong is None:
            return re.sub('[/:*?\"<>|]', '', string).strip()
        elif strong == 'strong':
            return re.sub('[^a-zA-Z0-9 .]', '', self._purge_name(string)).strip()
        else:
            return string