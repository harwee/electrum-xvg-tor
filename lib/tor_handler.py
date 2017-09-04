import atexit
import sys, os, shutil ,stat
import platform
from urllib import urlopen, urlretrieve
from zipfile import ZipFile
import json,re 
import subprocess, time, shlex

CREATE_NO_WINDOW = 0x08000000

if getattr(sys, 'frozen', False):
    script_dir  = os.path.dirname(sys.executable)
else:
    script_dir  = os.path.dirname(os.path.realpath(__file__))

tor_dir = os.path.join(script_dir,"tor")  

class TorProcessHandler(object):

    def __init__(self,tor_dir):
        self.tor_dir = tor_dir
        self.tor_installation_run_retries = 0
        if sys.platform == "linux" or sys.platform == "linux2":
            self.tor_binary = "tor"
            self.tor_binary_alternative = os.path.join(os.path.join(tor_dir,"Tor"),"tor")
            self.tor_config_file = os.path.join(os.path.join(tor_dir,"torrc"))
        elif sys.platform == "darwin":
            self.tor_binary = "tor"
            self.tor_config_file = os.path.join(os.path.join(tor_dir,"torrc"))
        elif sys.platform == "win32":
            self.tor_binary = "tor"
            self.tor_binary_alternative = os.path.join(os.path.join(tor_dir,"Tor"),"tor.exe")
            self.tor_config_file = os.path.join(os.path.join(tor_dir,"torrc"))

    def start_tor(self,retries=0):
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        
        try:
            self.tor_process = subprocess.Popen([self.tor_binary,"-f",self.tor_config_file],startupinfo=startupinfo)
            return
        except Exception as e:
            print(e)
            try:
                self.tor_process = subprocess.Popen([self.tor_binary_alternative,"-f",self.tor_config_file],startupinfo=startupinfo)
                return
            except Exception as e:
                print(e)
        if self.tor_installation_run_retries>=2:
            print("Tor cannot be started by Verge Wallet. Tor may not be in the PATH or not properly installed, Try to install Tor manually")

        self.install_tor() ## Copies download files from self.download_tor for Windows and install using shell for Linux and OSX
            
    def stop_tor(self):
        self.tor_process.kill()       

    def get_latest_bundle_version(self):
        base_url = "https://api.github.com/repos/TheTorProject/gettorbrowser/releases"
        releases_info = json.loads(urlopen(base_url).read().decode())
        return releases_info[0]["tag_name"].lower().replace("v","")

    def get_tor_download_url(self,bundle_version=None):
        base_url = "https://www.torproject.org/dist/torbrowser/{bundle_version}/".format(bundle_version=bundle_version)
        if sys.platform == "win32":
            download_page_source = urlopen(base_url).read().decode()
            regex_expression = "(tor-win32-.*?zip)".format(bundle_version=bundle_version)
            return base_url+re.search(regex_expression,download_page_source).group()
        elif sys.platform == "darwin":
            return base_url+"TorBrowser-{bundle_version}-osx64_en-US.dmg".format(bundle_version)
        elif sys.platform == "linux" or sys.platform == "linux2":
            download_page_source = urlopen(base_url).read().decode()
            return base_url+"tor-linux{}-debug.zip".format(platform.architecture()[0].replace("bit",""))
        else:
            print("Not a supported platform to autoinstall Tor, please install Tor manually")
            return

    def download_tor(self,bundle_version=None):

        if sys.platform != "win32":
            return

        if not bundle_version:
            bundle_version = self.get_latest_bundle_version()
        download_url = self.get_tor_download_url(bundle_version)
        self.temp_download_dir = os.path.join(self.tor_dir,"temp")
        if not os.path.exists(self.temp_download_dir):
            os.mkdir(self.temp_download_dir)
        print("YAYAY")
        self.tor_zip_file_path = os.path.join(self.temp_download_dir,download_url.strip().strip("/").split("/")[-1])
        urlretrieve(download_url,self.tor_zip_file_path)

    def install_tor(self):
        if sys.platform == "win32":
            self.download_tor()
            try:
                torzip = ZipFile(self.tor_zip_file_path,"r")
                torzip.extractall(self.tor_dir)
                torzip.close()
                shutil.rmtree(self.temp_download_dir)
            except Exception as e:
                print(e)
        elif sys.platform == "darwin":
            print("Installing Tor for OSX")
            subprocess.call(shlex.split("brew install tor"))
        elif sys.platform == "linux" or sys.platform=="linux2":
            print("Installing Tor for linux")
            try:
                subprocess.call(shlex.split("gksudo 'apt-get install tor -y'"))
            except Exception as e:
                print(e)

        self.tor_installation_run_retries +=1
        self.start_tor(retries=self.tor_installation_run_retries)
      
if __name__ == "__main__":
    ## testing handler
    torhandler = TorProcessHandler("../tor")
    torhandler.start_tor()
    time.sleep(10)
    torhandler.stop_tor()