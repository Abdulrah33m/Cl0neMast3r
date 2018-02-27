# coding: utf-8
# Coded with love and bugs by Abdulraheem Khaled @abdulrah33mk

import os
from requests import get
from threading import Thread
from bs4 import BeautifulSoup
from datetime import datetime
from re import findall, search

# Adding some colors to the script
end = '\033[1;m'
red = '\033[1;31m'
white = '\033[1;37m'
green = '\033[1;32m'


class Tool:  # This class is responsible about Tools
	list = []
	toolNum = num = 1
	toolsFile = "ToolsList.txt"
	htmlFile = "ToolsList.html"

	def __init__(self, url, *add):  # Constructor
		u = url[19:-4 if url.endswith('.git') else None].split("/")
		self.author = u[0]
		self.name = u[1]
		self.url = url
		self.num = (Tool.toolNum if add else Tool.num)
		if add:  # If user wants to add the tool to the list
			if self.check(self.url):  # Check that the tool is available
				self.isInstalled = self.exists(self.name)
				self.lastInstall = self.lastInstall() if self.isInstalled else "Couldn't retrieve the date"
				self.lastUpdate = self.lastUpdate()
				self.isUpToDate = type(self.lastInstall) != str and self.lastInstall >= self.lastUpdate
				Tool.toolNum += 1
		else:
			Tool.num += 1

	def lastUpdate(self):  # Returns last update for the tool on GitHub
		s = BeautifulSoup(get(self.url).text, 'html.parser')
		return self.strpTime(str(s.find("relative-time")['datetime'].replace("T", " ")[:-1]))

	def lastInstall(self):  # Returns last installation for the tool on PC
		if self.exists(self.name + "/install"):
			return self.strpTime(open(self.name + "/install", "r").read())
		else:
			return "Couldn't retrieve the date"

	def clone(self, *path):  # Clone the tool to the path argument
		print "Installing: " + self.name + ": ",
		if not os.system("git clone -q " + self.url + " " + (path[0] if path else "")+self.name):
			print green + "Ok" + end
			open((path[0] if path else "")+self.name + "/install", 'w').write(Tool.strfTime(datetime.now()))
			return True
		else:
			print red + "Error" + end
			return False

	def remove(self, *path):  # Delete the passed directory
		if path:
			print "Deleting the tool from tmp : ",
		else:
			print "Deleting the previous version of " + self.name + " : ",
		if not os.system("rm -rf " + (path[0] if path else "")+self.name):
			print green + "Ok" + end
		else:
			print red + "Error" + end

	def copy(self):  # Copy installed tool from tmp to current directory
		print "Copying the tool : ",
		if not os.system("cp -af /tmp/" + self.name + " ./"):
			print green + "Ok" + end
		else:
			print red + "Error" + end

	def printInfo(self):  # Print some information about found tools
		print "Tool Number: " + red + str(self.num) + end
		print "Tool: " + red + self.name + end
		print "Author: " + red + self.author + end
		if hasattr(self,'isInstalled'):
			print "Last Update On GitHub: " + red + Tool.strfTime(self.lastUpdate) + end
			print "Last Update On PC: " + red + (self.lastInstall if type(self.lastInstall) == str else Tool.strfTime(self.lastInstall)) + end
			print "Uptodate: " + (green if self.isUpToDate else red) + str(self.isUpToDate) + end
			print "Status: " + (green + "Installed" if self.isInstalled else red + "Not Installed") + end
		print red + "================================================================================" + end

	# --------------
	# Static Methods
	# --------------
	@staticmethod
	def exists(path):  # Check if path exists or not
		return os.path.exists(path)

	@staticmethod
	def deleteFile(path):  # Delete the past path
		if Tool.exists(path):
			os.remove(path)

	@staticmethod
	def check(url):  # Checks that the tool is available on GitHub
		req = get(url)
		return req.ok and "This repository is empty" not in req.text

	@staticmethod
	def strpTime(date):  # Converts string to datetime object
		return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

	@staticmethod
	def strfTime(date):  # Converts datetime object to formated string
		return datetime.strftime(date, "%Y-%m-%d %H:%M:%S")

	@staticmethod
	def add(url):  # Add tool using its URL
		try:
			if not url.startswith("https://github.com/"):
				raise Exception("Check the tool URL. It must be like this: https://github.com/User/Tool")
			elif Tool.found(url):
				raise Exception("The tool was found on the list already")
			elif not Tool.check(url):
				raise Exception("Tool is not available")
			resource.write(url + "\n")
			print green + "New tool has been added" + end  # + ": " + Tool(url, True).name
		except Exception, err:
			print red + str(err) + end

	@staticmethod
	def find(tool):  # Search for a tool on GitHub
		if tool:
			r = get("https://github.com/search?q=" + tool)
			if "any repositories matching" not in r.text:
				foundTools = []
				f = [int(x[3:]) for x in findall("\?p=\d+", r.text)]
				pages = max(f) if len(f) > 0 else 1
				if pages > 1:
					try:
						pages = input("I found {0}{1}{2} pages, How many page do you want me to display{0}:{2} ".format(red, str(pages), end))
					except:
						print red + "Wrong choice!" + end
						return
				for p in xrange(1, pages + 1):  # Shows the found tools in the found pages
					s = BeautifulSoup(get("https://github.com/search?p=" + str(p) + "&q=" + tool).text, 'html.parser')
					for t in [str(x["href"]) for x in s.find_all('a', class_="v-align-middle")]:
						foundTools.append('https://github.com' + t)
				print red + "================================================================================" + end
				for tool in foundTools:
					Tool(tool).printInfo()
				print "I found " + red + str(len(foundTools)) + end + " tools"
				try:
					choice = input("Which one do you want{0}:{1} ".format(red, end))
				except:
					print red + "Wrong choice!" + end
					return
				if choice <= len(foundTools):
					wait()
					Tool.add(foundTools[int(choice) - 1])
				else:
					print red+"Choose a number from 1 to "+str(len(foundTools))+end
			else:
				print red + "I couldn't find " + tool + end

	# --------------
	# Class Methods
	# --------------
	@classmethod
	def isEmpty(cls):  # Return if the list is empty or not
		return len(cls.list) == 0

	@classmethod
	def reset(cls):  # Reset tools' number
		cls.toolNum = cls.num = 1

	@classmethod
	def found(cls, toolURL):  # Check if the tool was added before
		return toolURL in [tool.url for tool in cls.list]

	@classmethod
	def display(cls):  # Display users tools
		if Tool.isEmpty():
			print red + "No tools have been added" + end
		else:
			for tool in cls.list:
				tool.printInfo()

	@classmethod
	def update(cls):  # Update all tools on the list
		try:
			x = input("[{0}1{1}] Update all tools\n[{0}2{1}] Update old tools: ".format(red, end))
		except:
			print red + "Wrong choice!" + end
			return
		if x == 1:
			listToUpdate = cls.list
		elif x == 2:
			listToUpdate = [tool for tool in cls.list if not tool.isUpToDate]
		else:
			print red + "Wrong choice!" + end
			return
		for tool in listToUpdate:
			print green + "[" + tool.name + "]" + end
			if tool.clone("/tmp/"):
				tool.copy()
				tool.remove("/tmp/")
		print red + "================================================================================" + end

	@classmethod
	def reinstall(cls):  # Reinstall all tools on the list
		for tool in cls.list:
			print green + "[" + tool.name + "]" + end
			tool.remove()
			tool.clone()
		print red + "================================================================================" + end

	@classmethod
	def importToolsHtml(cls):  # Import tools from HTML page
		if cls.exists(cls.htmlFile):
			for tool in BeautifulSoup(open(cls.htmlFile, "r").read(), 'html.parser').find_all("a"):
				cls.add(tool["href"])

	@classmethod
	def importToolsDir(cls):  # Import tools from current directory
		directories = [d for d in os.listdir('./') if os.path.isdir(d) and cls.exists(d + "/.git/config")]
		for d in directories:
			x = open(d + "/.git/config").read()
			cls.add(search("https://github.com/.+\w+", x).group())

	@classmethod
	def exportTools(cls):  # Export tools on the list to HTML page
		Tool.deleteFile(cls.htmlFile)
		#   Beginning
		htmlCode = """<html><head><title>Cl0neMast3r</title><style>@font-face{font-family:Hacked;src:url(https://hackedfont.com/HACKED.ttf);}
body{color:red;background-color:black;text-align:center;font-size:25px;font-family:Hacked}
h1{font-size:55px;}a{display:block;width:200px;color:white;background-color:red;text-decoration: none;
border: 1px solid red;border-radius:10px;margin:20px auto;padding:5px;}</style></head><body><h1>Cl0neMast3r</h1>"""

		# Middle
		htmlCode += "".join(["<a href=" + tool.url + ">" + tool.name + "</a>" for tool in cls.list])

		# End
		htmlCode += "./Abdulraheem_Khaled</body></html>"
		soup = BeautifulSoup(htmlCode, 'html.parser')
		open(cls.htmlFile, 'w').write(soup.prettify())
		print "Tools have been exported to " + red + cls.htmlFile + end


def wait():  # Wait until all tools on the list are updated
	if not updated:
		print red + "Please wait to update tools list" + end
	while not updated:
		pass


def update():  # Update the list of tools
	global updated
	Tool.list = [Tool(tool.strip(), True) for tool in resource]
	updated = True


if __name__ == '__main__':  # Main method
	while True:
		Tool.reset()  # Reset number of tools
		resource = open(Tool.toolsFile, "a+")  # List of added tools
		resource.seek(0)  # Start reading from the beginning of file
		updated = False  # Check that tools list has been read
		Thread(target=update).start()  # Using threading to
		os.system("clear")
		print """{0}
================================================================================
	   _____ _  ___             __  __           _   ____
	  / ____| |/ _ \           |  \/  |         | | |___ \\
	 | |    | | | | |_ __   ___| \  / | __ _ ___| |_  __) |_ __
	 | |    | | | | | '_ \ / _ \ |\/| |/ _` / __| __||__ <| '__|
	 | |____| | |_| | | | |  __/ |  | | (_| \__ \ |_ ___) | |
	  \_____|_|\___/|_| |_|\___|_|  |_|\__,_|___/\__|____/|_|

	  				./{1}Abdulraheem Khaled {0}@{1}Abdulrah33mK{0}
================================================================================{2}
[{0}A{2}] Add a tool using URL
[{0}F{2}] Find a tool on GitHub
[{0}R{2}] Reinstall your tools
[{0}U{2}] Update your tools
[{0}S{2}] Display your tools
[{0}D{2}] Delete tools list
[{0}X{2}] Export tools to HTML
[{0}M{2}] Import your tools
[{0}E{2}] Exit """.format(red, white, end)
		choice = raw_input("How can I help you" + red + ": " + end).lower()
		# ---------------------------------------------------------------------------------
		if choice == 'a':
			print "[" + red + "Adding to your tool" + end + "]"
			r = "y"  # Add more tools
			while r == "y":
				wait()
				Tool.add(raw_input("Enter the new tools GitHub link" + red + ": " + end).lower())
				r = raw_input("Add a new tool (Yes or No): ").lower()
		# ---------------------------------------------------------------------------------
		elif choice == 's':
			print "[" + red + "Displaying your tool" + end + "]"
			wait()
			Tool.display()
		# ---------------------------------------------------------------------------------
		elif choice == 'r':
			print "[" + red + "Reinstalling your tool" + end + "]"
			wait()
			Tool.reinstall()
		# ---------------------------------------------------------------------------------
		elif choice == 'u':
			print "[" + red + "Updating your tool" + end + "]"
			wait()
			Tool.update()
		# ---------------------------------------------------------------------------------
		elif choice == 'f':
			print "[" + red + "Finding your tool" + end + "]"
			Tool.find(raw_input("What tool do you want me to download" + red + ": " + end))
		# ---------------------------------------------------------------------------------
		elif choice == 'd':
			print "[" + red + "Deleting your tool" + end + "]"
			wait()
			Tool.deleteFile(Tool.toolsFile)
			print green + "Deleted your tools" + end
		# ---------------------------------------------------------------------------------
		elif choice == 'm':  # Importing your tools
			print "[" + red + "Importing tools" + end + "]"
			wait()
			print "You have two options{0}:{1}\n[{0}1{1}] Import from HTML\n[{0}2{1}] Import from current directory".format(red, end)
			try:
				choice = input("Which one you want{0}:{1} ".format(red, end))
			except:
				choice = 3
			if choice == 1:  # HTML
				Tool.importToolsHtml()
			elif choice == 2:  # Current directory
				Tool.importToolsDir()
			else:
				print red + "Wrong choice!" + end
		# ---------------------------------------------------------------------------------
		elif choice == 'x':  # Exporting your tools
			print "[" + red + "Exporting to HTML" + end + "]"
			wait()
			Tool.exportTools()
		# ---------------------------------------------------------------------------------
		elif choice == 'e':  # Exit
			print red + "Exiting, Good Bye :D" + end
			break
		# ---------------------------------------------------------------------------------
		else:
			print red + "Wrong choice!" + end
		# ---------------------------------------------------------------------------------
		while raw_input("Enter {0}M{1} to return to main page: ".format(red, end)).lower() != 'm':
			print red + "Wrong choice!" + end
