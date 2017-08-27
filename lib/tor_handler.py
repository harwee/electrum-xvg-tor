import subprocess
import atexit
import sys, os


if getattr(sys, 'frozen', False):
    script_dir  = os.path.dirname(sys.executable)
else:
    script_dir  = os.path.dirname(os.path.realpath(__file__))

tor_dir = os.path.join(script_dir,"tor")



class TorProcessHandler(object):

	def __init__(self,tor_dir):
		if sys.platform == "linux" or sys.platform == "linux2":
		    pass
		elif sys.platform == "darwin":
		    pass
		elif sys.platform == "win32":
		    self.tor_binary = os.path.join(os.path.join(tor_dir,"windows"),"tor.exe")
		    self.tor_config_file = os.path.join(os.path.join(tor_dir,"torrc"))

	def start_tor(self):
		print(" ".join([self.tor_binary,"-f",self.tor_config_file]))
		self.tor_process = subprocess.Popen([self.tor_binary,"-f",self.tor_config_file])

	def stop_tor(self):
		self.tor_process.kill()
