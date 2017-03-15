'''
Class used by pScan.py to power everything
'''
# Import my own custom external modules
import _pScanState   # Global variables specific to this program
import _Config       # Global variables used in this and similar programs
import _Log          # Global logging and console display 
import _Banner       # Pretty banner 
import _Exit         # Exit handling for unit testing

# Import system modules 
import sys, os, re, itertools, os.path, time, urllib, argparse, urlparse, urllib2, socket, json, httplib
import getpass
import requests
from requests_ntlm import HttpNtlmAuth
# NOTE: "six.py" must ALSO be in the root folder to avoid the following error (caused by conflict with MacOS's default six install):
# ImportError: No module named http_client
import glob          # To help find files in a folder
import ssl           # To handle certificate errors


# FUNCTIONS
# # # # # # # # # # # # # # # # # # # # # # # # 

# Validates the provided input file
# Unit tested in # __test_pScan_validate.py 
def validate_Input_File(filepath):

	#_Log.dPrint(_Config.icLevels.AllDebug, 'validate_Input_File - Current directory is ' + os.getcwd())

    # If we were not given a path, just ignore it
	if len(filepath) == 0:
		_Log.dPrint(_Config.icLevels.Error, 'No input file provided!')
		_Exit.exit(1)		# _Exit call must be followed with return for unit tests to work
		return

	# First, make sure the file is actually there
	if not os.path.isfile(filepath):		
		_Log.dPrint(_Config.icLevels.Error, 'The input file path is invalid or the file does not exist!')
		_Exit.exit(1)		# _Exit call must be followed with return for unit tests to work
		return

# Returns true if the output file path is "legitimate", in other words it
# is not blank, is not None, and could be a valid path (easy on Unix)
# Unit tested in # __test_pScan_validate.py 
def validate_Output_File(sFilename, sFileName):
	cleanOutputFile = sFilename.strip()
	if(len(cleanOutputFile) == 0 or cleanOutputFile == 'None'):
		_Log.dPrint(_Config.icLevels.Error, 'The ' + sFileName + ' file path is invalid or the file does not exist!')
		_Exit.exit(1)		# _Exit call must be followed with return for unit tests to work
		return
	return

# Parses input file into an array
# Unit tested in # __test_pScan_utilities.py 
def parse_Input_File_Into_Array(filepath):
	"""
	Reads in a file full of URLs (and #-starting comments)
	and returns them in a pretty array we can iterate across later
	"""
	# (Re)validate the incoming path - just to be sure
	validate_Input_File(filepath)

	# Then, open the file and read in all content lines
	with open(filepath, "r") as ins:
		lines = 0
		array = []
		for line in ins:
			lines += 1
			cleanline = line.strip()
			if len(cleanline) > 0:
				# Ignore lines that are just tabs and spaces
				# Ignore lines that start with #
				if cleanline[0] != "#":
 					array.append(cleanline)    

	_Log.dPrint(_Config.icLevels.Normal, 'Read ' + str(len(array)) + ' URLs from ' + str(lines) + ' lines in ' + filepath + ' OK.')
	return(array)

# Loop to test all imported URLs
def check_All_URLs(saURLs):

	# If we have at least one valid URL, open an output file and cycle through the list
	if(len(saURLs) > 0):
		create_CSV_File()
		for oneURL in saURLs:
			check_One_URL(oneURL)

# Test one URL
def check_One_URL(sURL):

	_Log.dPrint(_Config.icLevels.AllDebug, 'Checking ' + sURL)

	# Create an evidence folder for this URL
	sEvidenceFolder = os.path.join(_pScanState.sEvidenceFolder, evidence_Name_of_URL(sURL))
	create_Folder(sEvidenceFolder)

	# Examine site for headers and error page clues
	sServerHeaderServer, sServerHeaderXPoweredBy = check_Server_Headers_and_404(sURL, sEvidenceFolder)

	# Examine HTTPS environment
	bHTTPSEnabled, bHTTPSRequired = check_Server_HTTPS(sURL, sEvidenceFolder)

	# Download home page and look for signs of Wordpress
	if(check_If_Wordpress(sURL, sEvidenceFolder)):
		bWordpressIsWordpress = True
		bWordpressRunsWordfence =check_Wordpress_Wordfence(sURL, sEvidenceFolder)
		sWordpressVersion1 = check_Wordpress_Version1(sURL, sEvidenceFolder)
		sWordpressVersion2 = check_Wordpress_Version2(sURL, sEvidenceFolder)
		sWordpressVersion3 = check_Wordpress_Version3(sURL, sEvidenceFolder)
		bWordpressLoginPage = check_Wordpress_Login(sURL, sEvidenceFolder)
		bWordpressRegistrationPage = check_Wordpress_Registration(sURL, sEvidenceFolder)
		bWordpressLostPasswordPage = check_Wordpress_LostPassword(sURL, sEvidenceFolder)
		saWordpressAuthorUsers, bWordpressRunsStopEnum = check_Wordpress_AuthorUsers(sURL, sEvidenceFolder)
		saWordpressPostUsers, sWordpressBusiestUser, sWordpressBusiestPercentage = check_Wordpress_PostUsers(sURL, sEvidenceFolder)
		_Log.dPrint(_Config.icLevels.Normal, "Scanned Wordpress site " + sURL + " OK")

		# Figure out Wordpress version
		sWordpressVersion = sWordpressVersion1 
		if(len(sWordpressVersion.strip()) == 0):
			sWordpressVersion = sWordpressVersion2 
		if(len(sWordpressVersion.strip()) == 0):
			sWordpressVersion = sWordpressVersion3

		# Figure out likely Wordpress admins
		bWordpressDefaultAdmin, sWordpressLikelyAdmin = \
		analyze_Wordpress_Admins_and_PostingUsers(saWordpressAuthorUsers, saWordpressPostUsers, sWordpressBusiestUser)

	else:
		bWordpressIsWordpress = False
		bWordpressRunsWordfence = False
		sWordpressVersion = ""
		bWordpressLoginPage = False
		bWordpressRegistrationPage = False
		bWordpressLostPasswordPage = False
		saWordpressAuthorUsers = []
		saWordpressPostUsers = []
		bWordpressRunsStopEnum = False
		bWordpressDefaultAdmin = False
		sWordpressLikelyAdmin = ""
		sWordpressBusiestUser = ""
		sWordpressBusiestPercentage = ""

		_Log.dPrint(_Config.icLevels.Normal, "Skipped non-Wordpress site " + sURL + "")

	# Summarize
	_Log.dPrint(_Config.icLevels.SomeDebug, "Summary for " + \
	sURL + "\n" \
	"  Server Headers:" + "\n" \
	"    Server:                  " + sServerHeaderServer + "\n" \
	"    X-Powered-By:            " + sServerHeaderXPoweredBy + "\n" \
	"  HTTPS:" + "\n" \
	"    Enabled:                 " + str(bHTTPSEnabled) + "\n" \
	"    Required:                " + str(bHTTPSRequired) + "\n" \
	"  Wordpress:" + "\n" \
	"    Is Wordpress:            " + str(bWordpressIsWordpress) + "\n" \
	"    Version:                 " + sWordpressVersion + "\n" \
	"    Exposed Login Page:      " + str(bWordpressLoginPage) + "\n" \
	"    Allows Registration:     " + str(bWordpressRegistrationPage) + "\n" \
	"    Allows Lost Password:    " + str(bWordpressLostPasswordPage) + "\n" \
	"    Runs Wordfence:          " + str(bWordpressRunsWordfence) + "\n" \
	"    Runs Stop User Enum:     " + str(bWordpressRunsStopEnum) + "\n" \
	"    Users via Author Enum:   " + str(len(saWordpressAuthorUsers)) + "\n" \
	"    Users via Post Enum:     " + str(len(saWordpressPostUsers)) + "\n" \
	"    Uses Default Admin:      " + str(bWordpressDefaultAdmin) + "\n" \
	"    Likely Admin Account:    " + sWordpressLikelyAdmin + "\n" \
	"    Busiest User:            " + sWordpressBusiestUser + "\n" \
	"    Posts by Busiest User:   " + sWordpressBusiestPercentage  + "\n" \
	"")

	write_CSV_Line( \
	CSVElement(sURL) + \
	CSVElement(sServerHeaderServer) + \
	CSVElement(sServerHeaderXPoweredBy) + \
	CSVElement(str(bHTTPSEnabled)) + \
	CSVElement(str(bHTTPSRequired)) + \
	CSVElement(str(bWordpressIsWordpress)) + \
	CSVElement(sWordpressVersion) + \
	CSVElement(str(bWordpressLoginPage)) + \
	CSVElement(str(bWordpressRegistrationPage)) + \
	CSVElement(str(bWordpressLostPasswordPage)) + \
	CSVElement(str(bWordpressRunsWordfence)) + \
	CSVElement(str(bWordpressRunsStopEnum)) + \
	CSVElement(str(len(saWordpressAuthorUsers))) + \
	CSVElement(str(len(saWordpressPostUsers))) + \
	CSVElement(str(bWordpressDefaultAdmin)) + \
	CSVElement(sWordpressLikelyAdmin) + \
	CSVElement(sWordpressBusiestUser) + \
	CSVElement(sWordpressBusiestPercentage) \
	)

# Creates a new CSV output file and adds a header
def create_CSV_File():
    with open(_pScanState.sOutputFile, 'w+') as file:
        file.write(	\
		CSVElement("URL") + \
		CSVElement("HeaderServer") + \
		CSVElement("HeaderXPoweredBy") + \
		CSVElement("HTTPSEnabled") + \
		CSVElement("HTTPSRequired") + \
		CSVElement("IsWordpress") + \
		CSVElement("WPVersion") + \
		CSVElement("WPLoginPage") + \
		CSVElement("WPRegPage") + \
		CSVElement("WPLostPass") + \
		CSVElement("WPWordfence") + \
		CSVElement("WPStopEnum") + \
		CSVElement("WPAuthorUsers") + \
		CSVElement("WPPostUsers") + \
		CSVElement("WPDefaultAdmin") + \
		CSVElement("WPLikelyAdmin") + \
		CSVElement("WPBusiestUser") + \
		CSVElement("WPBusiestPercentage") + \
		"\n" \
		)

# Writes a line	to the CSV output file
def write_CSV_Line(sLine):
    with open(_pScanState.sOutputFile, 'a') as file:
        file.write(sLine + "\n")

# Creates a CSV element
def CSVElement(sValue):
	return "\"" + sValue.strip().replace("\n","") + "\","

# Looks for Wordpress users at ?author=###		
def check_Wordpress_AuthorUsers(sBaseURL, sFolder):
	iMissesInARow = 0
	bRunningStopEnum = False
	saUsers = []
	for iX in range(1, _pScanState.iMaxWordpressUsers):
		# Stop checking if Misses in a Row tells us we should stop
		if(iMissesInARow < _pScanState.iMaxWordpressUsersNotFound):
			sURL = sBaseURL + "?author=" + str(iX)
			sFile = os.path.join(sFolder, "author_" + str(iX) + ".html")
			if download_URL_or_Use_Existing_File(sURL, sFile):
				# Look for fullname
				# <title>eddie, Author at Name of Site</title>
				regEx = re.compile(".*<title>(.+?),.*", re.MULTILINE)
				sFullname = first_RegEx_Group_Or_Nothing(regEx, read_Entire_File(sFile))
				if(len(sFullname) > 0):
					_Log.dPrint(_Config.icLevels.AllDebug, "Found fullname " + sFullname + " for author #" + str(iX))  
				# Look for username
				# <link rel="canonical" href="http://www.hostnamehere.com/author/myusername/" />
				regEx = re.compile(".*<link.*canonical.*\\/author\\/(.+?)\\/.*", re.MULTILINE)
				sUsername = first_RegEx_Group_Or_Nothing(regEx, read_Entire_File(sFile))
				if(len(sUsername) > 0):
					_Log.dPrint(_Config.icLevels.AllDebug, "Found username " + sUsername + " for author #" + str(iX))  
				# Look for Stop Enum behavior
				# <body id="error-page">
				# <p>forbidden</p>
				regEx = re.compile(".*<body id=\"(.+?)\".*", re.MULTILINE)
				sErrorPage = first_RegEx_Group_Or_Nothing(regEx, read_Entire_File(sFile))
				if(sErrorPage == "error-page"):
					_Log.dPrint(_Config.icLevels.AllDebug, "Got error page for author #" + str(iX))  

				# Typical "author not found" behavior (replicate with high/silly author numbers)	
				# <title>Page not found - Name of Site</title>
				# <body class="error404">

				# If it's a miss, log it.  If we got a Stop Enum, log that too
				if (len(sUsername) == 0 and len(sFullname) == 0):
					iMissesInARow += 1
					# If we see the string error-page in the body id this could be a stop enum plug-in
					if(sErrorPage == "error-page"):
						bRunningStopEnum = True 
						_Log.dPrint(_Config.icLevels.AllDebug, "Possibly running stop enum plug-in (id=error-page)")
				else:
					iMissesInARow = 0
					saUsers.append([sUsername, sFullname])
			else:
				iMissesInARow += 1
				# If we got a 500 error this could also be a stop enum plug-in
				if("500" in codes_From_Stubs(sFile)):
					bRunningStopEnum = True 
					_Log.dPrint(_Config.icLevels.AllDebug, "Probably running stop enum plug-in (500 return code)")

		else:
			_Log.dPrint(_Config.icLevels.AllDebug, "Stopping the author user search at " + str(iX) + " after " + str(iMissesInARow) + "misses in a row")			
			break # Stop the loop		

	# saWordpressAuthorUsers, bWordpressRunsStopEnum
	# return ['two','one','three'], False
	return saUsers, bRunningStopEnum

# Looks for Wordpress users in the feed
# Interesting output from RDF /wp-rdf.php or /feed
# Note: feeds can be paged like: /feed?paged=3
# Note: versions and usernames, and possibly date of first post
# <?xml version="1.0" encoding="UTF-8"?><rdf:RDF ...>
# <channel ...>
#   <pubDate>Tue, 30 Apr 2013 20:59:17 +0000</pubDate>
#	<admin:generatorAgent rdf:resource="https://wordpress.org/?v=4.4.5" />
#</channel>
#<item ...>
#	<dc:creator><![CDATA[shelby]]></dc:creator>
def check_Wordpress_PostUsers(sBaseURL, sFolder):

	sFeedRegEx = ".*<dc:creator><!\[CDATA\[(.+?)\]\].*"
	dictUsersAndPosts = {}  # Keys are usernames, values are number of posts
	iTotalPosts = 0
	iTotalPages = 0

	# Get the feeds
	for iX in range(0, _pScanState.iMaxFeedPages):
		_Log.dPrint(_Config.icLevels.AllDebug, "Looking at feed page " + str(iX))
		sURL = os.path.join(sBaseURL, "feed/?paged=" + str(iX))
		sFile = os.path.join(sFolder, "feed_paged_" + str(iX) + ".html")
		if download_URL_or_Use_Existing_File(sURL, sFile):
			# If we don't see see any dc:creators, stop paging
			regEx = re.compile(sFeedRegEx, re.MULTILINE)
			sFirstUserOnPage = first_RegEx_Group_Or_Nothing(regEx, read_Entire_File(sFile))
			if(sFirstUserOnPage == ""):
				_Log.dPrint(_Config.icLevels.AllDebug, "Stopped at empty feed page " + str(iX))
				break
			iTotalPages += 1
			# Pull the "dc:creators" off the page, then cycle through
			# them, weeding out duplicates with a dictionary
			result = regEx.findall(read_Entire_File(sFile))
			#result = re.search(regEx, read_Entire_File(sFile)).findall(body)
			for oneUser in result:
				iTotalPosts += 1
				oneUserClean = oneUser.replace("\n","").strip()
				if (oneUserClean in dictUsersAndPosts):
					dictUsersAndPosts[oneUserClean] += 1
					_Log.dPrint(_Config.icLevels.AllDebug, "Existing user " + oneUserClean + " now has " + str(dictUsersAndPosts[oneUserClean]) + " posts")
				else:
					_Log.dPrint(_Config.icLevels.AllDebug, "Found new user " + oneUserClean + "")
					dictUsersAndPosts[oneUserClean] = 1
		else:
			_Log.dPrint(_Config.icLevels.AllDebug, "Stopped at 404 on feed page " + str(iX))
			break

	_Log.dPrint(_Config.icLevels.AllDebug, "Found " + str(len(dictUsersAndPosts)) + " users in " + str(iTotalPosts) + " posts on " + str(iTotalPages) + " pages")

	# Prepare an array of usernames from the results
	saUsers = []
	for oneUser in dictUsersAndPosts:
		saUsers.append(oneUser)				

	# Now figure out who had the most posts
	sBusiestUser = ""
	iMostPosts = 0
	for oneUser in dictUsersAndPosts:
		if(dictUsersAndPosts[oneUser] > iMostPosts):
			sBusiestUser = oneUser
			iMostPosts = dictUsersAndPosts[oneUser]

	# Calculate that as a percentage
	fPercentage = 0.0
	if(iTotalPosts > 0):
		fPercentage = (100.0 * iMostPosts) / (1.0 * iTotalPosts)
	sPercentage = str(int(fPercentage)) + "%"

	_Log.dPrint(_Config.icLevels.AllDebug, "The busiest user was " + sBusiestUser + " with " + str(iMostPosts) + " posts (" + sPercentage + ")")

	# saWordpressPostUsers, sWordpressBusiestUser, sWordpressBusiestPercentage 
	#return ['twelve', 'eleven', 'thirteen', 'fourteen'], 'thirteen', '77%'
	return saUsers, sBusiestUser, sPercentage

# Figures out who the the admin might be from the lists of possible users
def analyze_Wordpress_Admins_and_PostingUsers(saAuthorUsers, saPostUsers, sBusiestUser):

	# Look for the default admin
	bDefaultAdmin = False
	for iX in range(0, len(saAuthorUsers)):
		if(saAuthorUsers[iX][0] == 'admin'):
			_Log.dPrint(_Config.icLevels.AllDebug, "Found a user named admin in the list of author users.")						
			bDefaultAdmin = True
	for iX in range(0, len(saPostUsers)):
		if(saPostUsers[iX][0] == 'admin'):
			_Log.dPrint(_Config.icLevels.AllDebug, "Found a user named admin in the list of post users.")						
			bDefaultAdmin = True

	# Try to guess the name of a likely admin
	# If the default admin is in use, use that
	# Else, try the first user in the list of author users
	# Else, use the busiest post user
	sLikelyAdmin = ""
	if(bDefaultAdmin):
		_Log.dPrint(_Config.icLevels.AllDebug, "Likely admin is, well, admin.")						
		sLikelyAdmin = "admin"
	else:
		if(len(saAuthorUsers) > 0):
			_Log.dPrint(_Config.icLevels.AllDebug, "Likely admin is first author user (" + saAuthorUsers[0][0] + ").")						
			sLikelyAdmin = saAuthorUsers[0][0]
		else:
			_Log.dPrint(_Config.icLevels.AllDebug, "Likely admin is busiest post user (" + sBusiestUser + ").")						
			sLikelyAdmin = sBusiestUser

	# bWordpressDefaultAdmin, sWordpressLikelyAdmin
	# return False, 'one'
	return bDefaultAdmin, sLikelyAdmin

# Check out the HTTPS environment
def check_Server_HTTPS(sBaseURL, sFolder):

	bHTTPEnabled = False
	bHTTPSEnabled = False
	bHTTPSRequired = False

	HTTP_URL = sBaseURL.replace("https://", "http://")
	HTTP_File = os.path.join(sFolder, "http_index.html")
 	HTTPS_URL = sBaseURL.replace("http://", "https://")
	HTTPS_File = os.path.join(sFolder, "https_index.html")
	if download_URL_or_Use_Existing_File(HTTP_URL, HTTP_File, False):
		_Log.dPrint(_Config.icLevels.AllDebug, sBaseURL + " allows HTTP requests.")  
		bHTTPEnabled = True
	if download_URL_or_Use_Existing_File(HTTPS_URL, HTTPS_File, False):
		_Log.dPrint(_Config.icLevels.AllDebug, sBaseURL + " allows HTTPS requests.")  
		bHTTPSEnabled = True

	if (not bHTTPEnabled and bHTTPSEnabled):
		_Log.dPrint(_Config.icLevels.AllDebug, sBaseURL + " requires HTTPS.")  
		bHTTPSRequired = True
	else:
		_Log.dPrint(_Config.icLevels.AllDebug, sBaseURL + " does not require HTTPS.")  

	return bHTTPSEnabled, bHTTPSRequired

# Check server headers on the home page and on a 404 page
# Also inspect the 404 page for any interesting information
def check_Server_Headers_and_404(sBaseURL, sFolder):
	# Inspect the home page
	sURL = sBaseURL
	sFile = os.path.join(sFolder, "index.html")
	sHeaderServer = ""
	sHeaderXPoweredBy = ""
	if download_URL_or_Use_Existing_File(sURL, sFile):
		# Inspect the home page headers
		sHeaderServer, sHeaderXPoweredBy = extract_Headers_from_File(sFile, "","")
		# Pull down a 404 file
		sURL = os.path.join(sBaseURL, "intentional404.html")
		sFile = os.path.join(sFolder, "intentional404.html")
		if download_URL_or_Use_Existing_File(sURL, sFile):
			# Inspect the 404 file
			#saArray = update_Headers_from_File(saArray, sFile)
			sHeaderServer, sHeaderXPoweredBy = extract_Headers_from_File(sFile, sHeaderServer, sHeaderXPoweredBy)
		else:
			# Inspect the 404 headers file
			#saArray = update_Headers_from_File(saArray, sFile)
			# NOTE: We have to use the error file instead of the expected
			sHeaderServer, sHeaderXPoweredBy = extract_Headers_from_File(sFile + "_" + codes_From_Stubs(sFile).split(',',1)[0] + ".txt", sHeaderServer, sHeaderXPoweredBy)
	else:
		_Log.dPrint(_Config.icLevels.Warning, "Could not access " + sURL + "!")  # Extra warning - we should at least be able to access the site's root page!
	return sHeaderServer, sHeaderXPoweredBy 

# Converts the headers we found into something we can use
# Interesting headers:
# Server: Apache/2.2.15 (Red Hat)
# X-Powered-By: PHP/5.3.3
def extract_Headers_from_File(sFile, sServerCurrent, sXPoweredByCurrent):
	if(len(sServerCurrent.strip()) == 0 ):
		regEx = re.compile(".*Server: (.+?)$", re.MULTILINE)
		sServer = first_RegEx_Group_Or_Nothing(regEx, read_Entire_File(sFile))
		if(len(sServer) > 0):
			_Log.dPrint(_Config.icLevels.AllDebug, "Found header Server=" + sServer)  
	else:
		sServer = sServerCurrent
	if(len(sXPoweredByCurrent.strip()) == 0 ):		
		regEx = re.compile(".*X-Powered-By: (.+?)$", re.MULTILINE)
		sXPoweredBy = first_RegEx_Group_Or_Nothing(regEx, read_Entire_File(sFile))
		if(len(sXPoweredBy) > 0):
			_Log.dPrint(_Config.icLevels.AllDebug, "Found header X-Powered-By=" + sXPoweredBy)  
	else:
		sXPoweredBy = sXPoweredByCurrent
	return sServer, sXPoweredBy

# Check to see if this a Wordpress URL by looking for any references to /wp-content/ on the home page
def check_If_Wordpress(sBaseURL, sFolder):
	sURL = sBaseURL
	sFile = os.path.join(sFolder, "index.html")
	if download_URL_or_Use_Existing_File(sURL, sFile):
		sResult = re.search(".*\/wp-content\/", read_Entire_File(sFile)) # Any matches?
		return true_if_Set(sResult, 'This is a Wordpress site.', 'This does not appear to be a Wordpress site.')
	return bool_with_Message(False, 'Could not download or use ' + sURL)

# Check to see if this is using Wordfence
def check_Wordpress_Wordfence(sBaseURL, sFolder):
	sURL = sBaseURL
	sFile = os.path.join(sFolder, "index.html")
	if download_URL_or_Use_Existing_File(sURL, sFile):
		sResult = re.search(".*Wordfence.*", read_Entire_File(sFile)) # Any matches?
		return true_if_Set(sResult, 'This site runs Wordfence.', 'This site does not appear to be running Wordfence.')
	return bool_with_Message(False, 'Could not download or use ' + sURL)

# Try to get the Wordpress version from /wp-links-opml.php
#<opml version="1.0">
#<head>
#<title>Links for (site title)</title>
#<dateCreated>Tue, 25 Oct 2016 15:53:07 GMT</dateCreated>
#<!--  generator="WordPress/4.4.5"  -->
#</head>
#<body></body>
#</opml>
def check_Wordpress_Version1(sBaseURL, sFolder):
	sURL = os.path.join(sBaseURL, "wp-links-opml.php")
	sFile = os.path.join(sFolder, "wp-links-opml.php.html")
	if download_URL_or_Use_Existing_File(sURL, sFile):
		regEx = re.compile(".*generator=\"WordPress\\/(.+?)\"", re.MULTILINE)
		sVersion = first_RegEx_Group_Or_Nothing(regEx, read_Entire_File(sFile))
		return value_if_Set(sVersion, 'Found a version number of ' + sVersion + ' in wp-links-opml.php', 'Did not find a version number in wp-links-opml.php')
	return value_with_Message("", 'Could not download or use ' + sURL)

# Try to get the Wordpress version from /readme.html
# More version
# <h1 id="logo">
# 	<a href="https://wordpress.org/"><img alt="WordPress" src="wp-admin/images/wordpress-logo.png" /></a>
# 	<br /> Version 4.6.1
# </h1>
def check_Wordpress_Version2(sBaseURL, sFolder):
	sURL = os.path.join(sBaseURL, "readme.html")
	sFile = os.path.join(sFolder, "readme.html")
	if download_URL_or_Use_Existing_File(sURL, sFile):
		regEx = re.compile(".* Version (.+?)$", re.MULTILINE)
		sVersion = first_RegEx_Group_Or_Nothing(regEx, read_Entire_File(sFile))
		return value_if_Set(sVersion, 'Found a version number of ' + sVersion + ' in readme.html', 'Did not find a version number in readme.html')
	return value_with_Message("", 'Could not download or use ' + sURL)

# Try to get the Wordpress version from /wp-admin/install.php
# <link rel='stylesheet' id='buttons-css'  href='(siteURL)/wp-includes/css/buttons.min.css?ver=4.6.1' type='text/css' media='all' />
# <link rel='stylesheet' id='install-css'  href='(siteURL)/wp-admin/css/install.min.css?ver=4.6.1' type='text/css' media='all' />
# <link rel='stylesheet' id='dashicons-css'  href='(siteURL)/wp-includes/css/dashicons.min.css?ver=4.6.1' type='text/css' media='all' />
def check_Wordpress_Version3(sBaseURL, sFolder):
	sURL = os.path.join(sBaseURL, "wp-admin/install.php")
	sFile = os.path.join(sFolder, "wp-admin_install.php.html")
	if download_URL_or_Use_Existing_File(sURL, sFile):
		regEx = re.compile(".*\.min\.css\?ver=(.+?)'", re.MULTILINE)
		sVersion = first_RegEx_Group_Or_Nothing(regEx, read_Entire_File(sFile))
		return value_if_Set(sVersion, 'Found a version number of ' + sVersion + ' in wp-admin/install.php', 'Did not find a version number in wp-admin/install.php')
	return value_with_Message("", 'Could not download or use ' + sURL)

# Check if the default Wordpress login form is at /wp-login.php
# <body class="login login-action-login wp-core-ui  locale-en-us">
#		<div id="login">
#<form name="loginform" id="loginform" action="https://cftpcert.com/wp-login.php" method="post">
#<label for="user_login">Username or Email<br />
#<input type="text" name="log" id="user_login" class="input" value="" size="20" /></label>
#<label for="user_pass">Password<br />
#<input type="password" name="pwd" id="user_pass" class="input" value="" size="20" /></label>
#<p class="forgetmenot"><label for="rememberme"><input name="rememberme" type="checkbox" id="rememberme" value="forever"  /> Remember Me</label></p>
#	<p class="submit">
#		<input type="submit" name="wp-submit" id="wp-submit" class="button button-primary button-large" value="Log In" />
#		<input type="hidden" name="redirect_to" value="http://cftpcert.com/wp-login.php" />
def check_Wordpress_Login(sBaseURL, sFolder):
	sURL = os.path.join(sBaseURL, "wp-login.php")
	sFile = os.path.join(sFolder, "wp-login.php.html")
	if download_URL_or_Use_Existing_File(sURL, sFile):
		sResult = re.search(".*loginform.*action=\"http.*wp-login.php.*", read_Entire_File(sFile)) # Any matches?
		return true_if_Set(sResult, 'Found a login form at wp-login.php', 'Did not find a login form at wp-login.php')
	return bool_with_Message(False, 'Could not download or use ' + sURL)

# Check if the Wordpress registration page is visible at /wp-login.php?action=register
# <body class="login login-action-register wp-core-ui  locale-en-us">
# <div id="login">
# <p class="message register">Register For This Site</p>
# <form name="registerform" id="registerform" action="https://cftpcert.com/wp-login.php?action=register" method="post" novalidate="novalidate">
# <p id="reg_passmail">Registration confirmation will be emailed to you.</p>
# <p class="submit"><input type="submit" name="wp-submit" id="wp-submit" class="button button-primary button-large" value="Register" /></p>
def check_Wordpress_Registration(sBaseURL, sFolder):
	sURL = os.path.join(sBaseURL, "wp-login.php?action=register")
	sFile = os.path.join(sFolder, "wp-login.php_action_register.html")
	if download_URL_or_Use_Existing_File(sURL, sFile):
		sResult = re.search(".*registerform.*action=\"http.*action=register.*", read_Entire_File(sFile)) # Any matches?
		return true_if_Set(sResult, 'Found a registration form at wp-login.php?action=register', 'Did not find a registration form at wp-login.php?action=register')
	return bool_with_Message(False, 'Could not download or use ' + sURL)

# Check if the Wordpress lost password page is visible at /wp-login.php?action=lostpassword
# (This is helpful to hackers because they get different messages depending on whether
#   a tested user exists or not - e.g., "ERROR: There is no user registered with that email address.")
# <body class="login login-action-lostpassword wp-core-ui  locale-en-us">
# <div id="login">
# <p class="message">Please enter your username or email address. You will receive a link to create a new password via email.</p>
# <div id="login_error">	<strong>ERROR</strong>: There is no user registered with that email address.<br />
# <form name="lostpasswordform" id="lostpasswordform" action="http://targetsite.com/wp-login.php?action=lostpassword" method="post">
# <label for="user_login" >Username or Email<br />
# <p class="aiowps-captcha"><label>Please enter an answer in digits:</label><div class="aiowps-captcha-equation"><strong>four &#43; 9 = 
# ... <input type="hidden" name="aiowps-captcha-string-info" id="aiowps-captcha-string-info" value="uyvjlbdprk" />
# ... <input type="hidden" name="aiowps-captcha-temp-string" id="aiowps-captcha-temp-string" value="1478026168" />
# ... <input type="text" size="2" id="aiowps-captcha-answer" name="aiowps-captcha-answer" value="" /></strong></div></p>	
# <p class="submit"><input type="submit" name="wp-submit" id="wp-submit" class="button button-primary button-large" value="Get New Password" /></p>
def check_Wordpress_LostPassword(sBaseURL, sFolder):
	sURL = os.path.join(sBaseURL, "wp-login.php?action=lostpassword")
	sFile = os.path.join(sFolder, "wp-login.php_action_lostpassword.html")
	if download_URL_or_Use_Existing_File(sURL, sFile):
		sResult = re.search(".*lostpasswordform.*action=\"http.*action=lostpassword.*", read_Entire_File(sFile)) # Any matches?
		return true_if_Set(sResult, 'Found a lost password form at wp-login.php?action=register', 'Did not find a lost password form at wp-login.php?action=register')
	return bool_with_Message(False, 'Could not download or use ' + sURL)

# Gets first group instance of searched string, or something that resolves to "False" if bool'ed
def first_RegEx_Group_Or_Nothing(regEx, sString):
	try:
		return re.search(regEx, sString).group(1)
	except AttributeError:
		return ""

# Returns true if the value is provided
def true_if_Set(sValue, sMessageIfSet, sMessageIfNotSet):
	return bool(value_if_Set(sValue, sMessageIfSet, sMessageIfNotSet))

# Returns the value provided, if set.  Also logs appropriate messages.
def value_if_Set(sValue, sMessageIfSet, sMessageIfNotSet):
	if(bool(sValue)):
		_Log.dPrint(_Config.icLevels.AllDebug, sMessageIfSet)
		return sValue
	_Log.dPrint(_Config.icLevels.AllDebug, sMessageIfNotSet)
	return ""	

# Returns the provided value after writing out the log message as if true_if_Set was called
def bool_with_Message(bValue, sMessage):
	if(bValue):
		return true_if_Set(True, sMessage, '')
	return true_if_Set(False, '', sMessage)

# Returns the provided value after writing out the log message
def value_with_Message(sValue, sMessage):
	_Log.dPrint(_Config.icLevels.AllDebug, sMessage)
	return sValue

# Reads an entire file into a string
def read_Entire_File(sFile):
	text_file = open(sFile)
	return text_file.read()	

# Writes a string or array into a file
def write_Entire_File(sFile, vValue):

	if isinstance(vValue, basestring):
		# String
		_Log.dPrint(_Config.icLevels.AllDebug, 'Writing a ' + str(len(vValue)) + ' character string to ' + sFile)
		sString = vValue
	else:
		sString = ""
		# Array to JSON	
		# sString = json.dumps(vValue)
		# _Log.dPrint(_Config.icLevels.AllDebug, 'Writing a ' + str(len(vValue)) + ' element variable as a ' + str(len(sString)) + ' character string to ' + sFile)
		#for hh, vv in vValue: #.getheaders():
		#	sString += hh + ": " + vv + "\n"
		for hh in vValue: #.getheaders():
			sString += hh + ": " + vValue[hh] + "\n"
		_Log.dPrint(_Config.icLevels.AllDebug, 'Writing a ' + str(len(vValue)) + ' element variable as a ' + str(len(sString)) + ' character string to ' + sFile)
	text_file = open(sFile, "w")
	text_file.write(sString)
	text_file.close()		

# Returns TRUE if we can use either an existing file or we got a valid download
def download_URL_or_Use_Existing_File(sURL, sFile, bFollowRedirects=True):
	if(os.path.isfile(sFile)):
		_Log.dPrint(_Config.icLevels.AllDebug, 'Using existing file ' + sFile + ' for ' + sURL)
		_pScanState.sLastURL = sURL   # Change the next referrer
	else:
		return download_URL_to_File(sURL, sFile, bFollowRedirects)   # Next referrer gets changed in here
	return True

# Prevents redirects with urllib2 (in download_URL_to_File)
class NoRedirect(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        pass

# Downloads a specific URL to a file
def download_URL_to_File(sURL, sFile, bFollowRedirects=True):
	_Log.dPrint(_Config.icLevels.AllDebug, 'Downloading ' + sURL + ' into ' + sFile)
	# If we have a error code stub, skip the download unless we've been told to retry errors
	if(stubs_Exist_For(sFile) and not _pScanState.bRescanStubErrors):
		_Log.dPrint(_Config.icLevels.AllDebug, "Not downloading - we previously got code(s) " + codes_From_Stubs(sFile) + " on " + sURL)
		_pScanState.sLastURL = sURL   # Change the next referrer
	else:		
		try:
			# See https://docs.python.org/2/library/urllib2.html for this request object
			request_headers = {
			"Upgrade-Insecure-Requests": _pScanState.sHeaderUpgradeInsecureRequests,
			"User-Agent": _pScanState.sHeaderUserAgent,
			"Accept": _pScanState.sHeaderAccept,
			"Accept-Encoding": _pScanState.sHeaderAcceptEncoding,
			"Accept-Language": _pScanState.sHeaderAcceptLanguage,
			"Referer": _pScanState.sLastURL,
			"Connection": _pScanState.sHeaderConnection 
			}
			_pScanState.sLastURL = sURL   # Change the next referrer
			#_Log.dPrint(_Config.icLevels.AllDebug, "Using headers:\n" + str(request_headers))

			# Build the request and invoke the appropriate opener to follow or not follow redirects
			request = urllib2.Request(sURL, headers=request_headers)
			if(bFollowRedirects):
				response = urllib2.urlopen(request)
			else:
				noredir_opener = urllib2.build_opener(NoRedirect())
				#urllib2.install_opener(noredir_opener)
				#response = urllib2.urlopen(request)
				#response = noredir_opener.urlopen(request)
				response = noredir_opener.open(request)

			_Log.dPrint(_Config.icLevels.AllDebug, "Got status code: %s" % response.getcode())
			write_Entire_File(sFile, response.read() + format_Headers_for_HTML_Insert(response.info()))	
			return True
		except urllib2.HTTPError, e:
			_Log.dPrint(_Config.icLevels.AllDebug, "Got error status code: %s" % e.code)
			if(_pScanState.sNTLMProxyUsername == 'None' or _pScanState.sNTLMProxyHost == 'None'):
				_Log.dPrint(_Config.icLevels.AllDebug, 'Not retrying NTLM proxy (missing hostname and/or username)')
				#write_Server_Error_Stub(sFile, e.code, response.info().headers)
				write_Server_Error_Stub(sFile, e.code, e.headers)
			else:
				_Log.dPrint(_Config.icLevels.AllDebug, 'Retrying ' + sURL + ' with NTLM proxy (as ' + _pScanState.sNTLMProxyUsername + ')')
				from requests_ntlm import HttpNtlmAuth
				# See http://docs.python-requests.org/en/master/user/quickstart/ for this request object
				if(bFollowRedirects):
					response = requests.get(sURL,auth=HttpNtlmAuth(_pScanState.sNTLMProxyHost + '\\' + _pScanState.sNTLMProxyUsername, _pScanState.sNTLMProxyPassword), headers=request_headers)
				else:
					response = requests.get(sURL,auth=HttpNtlmAuth(_pScanState.sNTLMProxyHost + '\\' + _pScanState.sNTLMProxyUsername, _pScanState.sNTLMProxyPassword), headers=request_headers, allow_redirects=False)
				_Log.dPrint(_Config.icLevels.AllDebug, "Got status code: %s" % response.status_code)
				if(response.status_code >= 200 and response.status_code < 300):
					write_Entire_File(sFile, response.read() + format_Headers_for_HTML_Insert(response.info()))	
					return True
				else:
					write_Server_Error_Stub(sFile, response.status_code, response.headers)
		except ssl.CertificateError, e:
			_Log.dPrint(_Config.icLevels.SomeDebug,  sURL + ' encountered certificate error. ' + e[0])
		except urllib2.URLError, e:
			_Log.dPrint(_Config.icLevels.SomeDebug,  sURL + ' encountered connection error. ' + str(e[0]))

	_Log.dPrint(_Config.icLevels.SomeDebug, 'Could not download ' + sURL + ' into ' + sFile)
	return False

# Formats headers for inclusion as a comment at the end of an HTML file
def format_Headers_for_HTML_Insert(infoObj):
	return "\n\n\n" + \
	"<!-- HEADERS \n" + \
	str(infoObj) + \
	"\n-->\n" 

# Figures out if any stubs exist for a "URL file"
def stubs_Exist_For(sFile):
	if(len(codes_From_Stubs(sFile)) == 0):
		return False
	return True

# Returns the list of codes for a "URL file"
def codes_From_Stubs(sFile):
	sCodes = ""
	# Get all matching code files
	listNames = glob.glob(stub_Name(sFile, "???")) # All files with three characters where the code should be
	# Unless the list is empty, strip off the non-code data
	for sName in listNames:
		sCode = sName.replace(sFile + "_","").replace(".txt","")
		if(len(sCodes) == 0):
			sCodes = sCode
		else:
			sCodes = sCodes + "," + sCode
	return sCodes

# Figures out the "code" path for a given "URL file" - this is the name of the "stub" that gets written
# Works for paths and filenames since the code and little more is just appended to the incoming base
def stub_Name(sBasePath, sCode):
	return sBasePath + "_" + str(sCode) + ".txt"

# Writes a stub file that indicates that during this run a specific error happened, and insert any headers returned
def write_Server_Error_Stub(sBasePath, sCode, sHeaders):
	write_Entire_File(stub_Name(sBasePath, sCode), sHeaders)

# Gets today's date and time in a formatted form
# Unit tested in # __test_pScan_utilities.py 
def now_Formatted():
	# Format: Evidence_YYYY-MM-DD_HH-MM-SS
	return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())   

# Validates an incoming date
# Unit tested in # __test_pScan_validate.py 
def validate_And_Normalize_DateTime(DateTimeToTest):
	CleanedDateTime	= DateTimeToTest.replace(":","-")
	CleanedDateTime	= CleanedDateTime.replace(" ","_")
	if(not bool(re.search(_pScanState.sFullDateTimeRegEx,CleanedDateTime))):
		_Log.dPrint(_Config.icLevels.Error, 'The provided datetime is invalid! (Must be in YYYY-MM-DD HH:MM:SS format.)')
		_Exit.exit(1)		# _Exit call must be followed with return for unit tests to work
		return ""	
	return CleanedDateTime

# Validates an evidence folder
# Unit tested in # __test_pScan_validate.py 
def validate_Existing_Evidence_Folder(FolderToTest):
	if not os.path.exists(FolderToTest):
		_Log.dPrint(_Config.icLevels.Error, 'The requested evidence folder (' + FolderToTest + ') does not exist.')
		_Exit.exit(1)		# _Exit call must be followed with return for unit tests to work
		return 	
	return 

# Converts an incoming URL into a similar name for use in a URL
# Unit tested in # __test_pScan_utilities.py 
def evidence_Name_of_URL(sURL):
	# Use the built-in urlparse module
	try:
		o = urlparse.urlparse(sURL)
		if(o.scheme != "" and o.hostname != ""):
			sName = o.scheme + "_" + o.hostname
		else:
			sName = ""		
	except:
		sName = ""		
	return sName

# Creates a folder
# Dies immediately if the folder could not be created
# Unit tested in # __test_pScan_utilities.py 
def create_Folder(sFolder):
	try:
		if not os.path.exists(sFolder):
			_Log.dPrint(_Config.icLevels.AllDebug, 'Creating folder ' + sFolder + '...')
			os.mkdir(sFolder)
		else:
			_Log.dPrint(_Config.icLevels.SomeDebug, 'Did not create folder ' + sFolder + ' because it already exists.')
	except: 
		_Log.dPrint(_Config.icLevels.Error, 'Could not create folder ' + sFolder + '!')
		_Exit.exit(1)		# _Exit call must be followed with return for unit tests to work
		return		
	return 

# Purges a folder, including all files and subfolders in it
# Dies immediately if the folder could not be created
# Unit tested in # __test_pScan_utilities.py 
def purge_Folder(sFolder):
	try:
		if(len(sFolder.strip()) < 28):  # Names should be pretty long - e.g., Evidence_2016-10-12_08-24-56
			_Log.dPrint(_Config.icLevels.Error, 'Will not try to purge ' + sFolder + ' because name is too short!')
			_Exit.exit(1)		# _Exit call must be followed with return for unit tests to work
			return		
		if(not bool(re.search(_pScanState.sRootFolderRegEx,sFolder))):
			_Log.dPrint(_Config.icLevels.Error, 'Will not try to purge ' + sFolder + ' because name looks odd!')
			_Exit.exit(1)		# _Exit call must be followed with return for unit tests to work
			return		
		if os.path.exists(sFolder):
			_Log.dPrint(_Config.icLevels.AllDebug, 'Purging folder ' + sFolder + '...')
			# CAUTION - CHECK incoming folder against rules before proceeding
			# and bail out if the incoming folder doesn't look legit
			for root, dirs, files in os.walk(sFolder, topdown=False):
				for name in files:
					_Log.dPrint(_Config.icLevels.AllDebug, '  deleting file: ' + os.path.join(root, name))
					os.remove(os.path.join(root, name))
				for name in dirs:
					_Log.dPrint(_Config.icLevels.AllDebug, '  deleting folder: ' + os.path.join(root, name))
					os.rmdir(os.path.join(root, name))			
			_Log.dPrint(_Config.icLevels.AllDebug, '  deleting folder: ' + sFolder)
			os.rmdir(sFolder)			

		else:
			_Log.dPrint(_Config.icLevels.SomeDebug, 'Did not purge folder ' + sFolder + ' because it does not exist.')
	except: 
		_Log.dPrint(_Config.icLevels.Error, 'Could not purge folder (and all its contents) ' + sFolder + '!')
		_Exit.exit(1)		# _Exit call must be followed with return for unit tests to work
		return		
	return

# VARIOUS NOTES

# Good list of interesting files on Wordpress:
# http://wp.sjkp.dk/wordpress-security-and-hacks/

# TODO for the future:
# /wp-settings.php
# Look for errors such as "No such file or directory in /home2/path1/path2"


# # # # # # # # # # # # # # # # # # # # # # # # 
# MAINLINE EXECUTION
# # # # # # # # # # # # # # # # # # # # # # # # 
def Run():

	# # # DEAL WITH COMMAND LINE INPUT

	# Define and then parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', dest='InputFile', \
	 help='input file of URLs (REQUIRED)', default='None')
	parser.add_argument('-re', dest='ReprocessDateTime', \
	 help='reprocess content from DateTime formatted as YYYY-MM-DD_HH-MM-SS or YYYY:MM:DD HH:MM:SS (Optional; helpful for stealth or for revised findings after new version)', default='None')
	parser.add_argument('-o', dest='OutputFile', \
	 help='use this output file for findings in CSV format (Optional; otherwise YYYY-MM-DD_HH-MM-SS_results.csv)', default='None')
	parser.add_argument('-l', dest='LogFile', \
	 help='use this output file for detailed log (Optional; otherwise YYYY-MM-DD_HH-MM-SS_log.txt)', default='None')
	#parser.add_argument('-p', dest='iPort', type=int, \
	# help='target port (REQUIRED)', default=-1)
	parser.add_argument('-d', dest='Debug', type=int, \
	 help='debug level (1=err 2=warn 3=OK (def), 4=debug, 5=all)')
	parser.add_argument('-nph', dest='NTLMProxyHost', \
	 help='NTLM Proxy Host (OPTIONAL)', default='None')
	parser.add_argument('-npu', dest='NTLMProxyUsername', \
	 help='NTLM Proxy Username (OPTIONAL)', default='None')
	#parser.add_argument('-npp', dest='NTLMProxyPassword', \
	# help='NTLM Proxy Password (OPTIONAL)', default='None')

	# parse the purge
	feature_parser = parser.add_mutually_exclusive_group(required=False)
	feature_parser.add_argument('-pe', dest='PurgeEvidence', action='store_true', help="Purge Evidence Folder (Optional)")
	feature_parser.add_argument('-no-pe', dest='PurgeEvidence', action='store_false', help="Do Not Purge Evidence Folder (Default, Optional)")
	parser.set_defaults(PurgeEvidence=False)

	# parse the rescan on error
	feature_parser = parser.add_mutually_exclusive_group(required=False)
	feature_parser.add_argument('-rse', dest='RescanStubErrors', action='store_true', help="Rescan Pages That Previously Got Errors (Optional)")
	feature_parser.add_argument('-no-rse', dest='RescanStubErrors', action='store_false', help="Do Not Rescan Pages That Previously Got Errors (Default, Optional)")
	parser.set_defaults(RescanStubErrors=False)

	args = parser.parse_args()

	# Move command-line argument values into local variables
	_pScanState.sInputFile = args.InputFile
	_pScanState.sOutputFile = args.OutputFile
	_pScanState.sLogFile = args.LogFile
	_pScanState.sReprocessDateTime = args.ReprocessDateTime
	_pScanState.bPurgeEvidence = args.PurgeEvidence
	_pScanState.bRescanStubErrors = args.RescanStubErrors
	_pScanState.sNTLMProxyHost = args.NTLMProxyHost
	_pScanState.sNTLMProxyUsername = args.NTLMProxyUsername
	#_pScanState.sNTLMProxyPassword = args.NTLMProxyPassword
	_Config.iDebug = args.Debug

	## Validate AND CORRECT debug level
	if(_Config.iDebug < 1) | (_Config.iDebug > 5): 
	    _Log.dPrint(_Config.icLevels.Warning, 'Debug level must be 1-5, resetting to 3.')
	    _Config.iDebug = 3

	# Announce self to user unless we're running quietly (Warning or Error)
	if _Config.iDebug > 2:
	    _Banner.Banner(_pScanState.sProgramName + " by " + _pScanState.sAuthor + " v" + _pScanState.sVersion) 

	# Validate parameters AND HALT EXECUTION if there are any problems
	## Look for required parameters
	if (_pScanState.sInputFile == 'None'):
	    _Log.dPrint(_Config.icLevels.Error, 'Input file is required!')
	    _Log.cPrint('white', parser.format_help())
	    exit(1)

	## Make sure the input file exists.
	validate_Input_File(_pScanState.sInputFile)

	## If a reprocessing date/time was provided, check to make sure that folder really exists.
	if (_pScanState.sReprocessDateTime == 'None'):
		_pScanState.sFormattedDateTime = now_Formatted()
		_pScanState.sEvidenceFolder = "Evidence_" + _pScanState.sFormattedDateTime
	else:
		_pScanState.sFormattedDateTime = validate_And_Normalize_DateTime(_pScanState.sReprocessDateTime)
		_pScanState.sEvidenceFolder = "Evidence_" + _pScanState.sFormattedDateTime
		validate_Existing_Evidence_Folder(_pScanState.sEvidenceFolder)

	## If an explicit output file was provided, see if it looks plausable.  Otherwise make one up.
	if (_pScanState.sOutputFile == 'None'):
		_pScanState.sOutputFile = _pScanState.sFormattedDateTime + "_results.csv"
	else:
		validate_Output_File(_pScanState.sOutputFile, "Output")

	## If an explicit log file was provided, see if it looks plausable.  Otherwise make one up.
	if (_pScanState.sLogFile == 'None'):
		_pScanState.sLogFile = _pScanState.sFormattedDateTime + ".log"
	else:
		validate_Output_File(_pScanState.sLogFile, "Log")

	## If a proxy username was provided, prompt for the password
	if(not _pScanState.sNTLMProxyUsername == 'None' and not _pScanState.sNTLMProxyHost == 'None'):
		_pScanState.sNTLMProxyPassword = getpass.getpass(prompt='Enter the password for ' + _pScanState.sNTLMProxyUsername + ":")

	## Engage the output debug file
	_Log.dPrint(_Config.icLevels.Normal, "Check " + _pScanState.sLogFile + " for additional debug/trace information.")
	_Log.StartLogFile(_pScanState.sLogFile, _pScanState.sProgramName, _pScanState.sVersion)

	## Before we hit the main code, print out the current state
	_Log.dPrint(_Config.icLevels.AllDebug, "Current State:\n" + _pScanState.asString())

	# # # LOAD UP THE URLS 
	# Load up the URLs
	saURLs = parse_Input_File_Into_Array(_pScanState.sInputFile)
	# If the URL array is OK...
	if (len(saURLs) > 0):
		# Create the root evidence folder if it doesn't already exist
		create_Folder(_pScanState.sEvidenceFolder)
		# Cycle through the URLs
		check_All_URLs(saURLs)

		# If we were instructed to clean up, purge the evidence folder
		if (_pScanState.bPurgeEvidence):
			purge_Folder(_pScanState.sEvidenceFolder)

		_Log.dPrint(_Config.icLevels.Normal, "All done. Check " + _pScanState.sOutputFile + " for URL output.")

	else:
	    _Log.dPrint(_Config.icLevels.Warning, 'All done. However, there were no URLs to process!')


