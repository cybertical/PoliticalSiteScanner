# __test_wpScan_validate.py

# Reference target modules
import _wpScan

# Reference custom modules
import _Exit, _Config, _Log

# Reference system modules
import os, re

def TEST_parse_Input_File_Into_Array():

	# Set up exit and config classes for unit testing
	#_Config.iDebug = _Config.icLevels.AllDebug    # All Debug during testing or debugging
	_Config.iDebug = _Config.icLevels.Success    # Success when the test is ready
	_Exit.ExitOnExit = False
	_Config.caColors.Mute()  # Tone down error and other console colors

	sTestName = "TEST_parse_Input_File_Into_Array"
	_Log.dPrint(_Config.icLevels.SomeDebug, sTestName + " Started...")	

	# Test a good but empty file
	_Exit.reset()
	sRealFile = sTestName + '.deleteme'
	file = open(sRealFile, 'w')
	file.write("#delete me")
	file.close()
	saArr = _wpScan.parse_Input_File_Into_Array(sRealFile)
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "good but empty file")
	_Exit.DieIfNoMatch(len(saArr), 0, sTestName, "good but empty file")
	os.remove(sRealFile)

	# Test a good file with 12 lines: 3 blank, 4 comments, 5 URLs
	_Exit.reset()
	sRealFile = sTestName + '.deleteme'
	file = open(sRealFile, 'w')
	file.write(" 	 \n") # Tabs
	file.write("# I am a comment\n")
	file.write("# I am a comment\n")
	file.write("https:\\\\a.url.com\\1\n")
	file.write("https:\\\\a.url.com\\2 \n")
	file.write("# I am a comment\n")
	file.write(" https:\\\\a.url.com\\3\n")
	file.write(" https:\\\\a.url.com\\4 \n")
	file.write("# I am a comment\n")
	file.write("	https:\\\\a.url.com\\5	\n") # Tabs
	file.write(" \n") 
	file.write("\n") 
	file.close()
	saArr = _wpScan.parse_Input_File_Into_Array(sRealFile)
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "good file")
	_Exit.DieIfNoMatch(len(saArr), 5, sTestName, "good file")
	os.remove(sRealFile)

	_Config.caColors.Unmute()
	_Log.dPrint(_Config.icLevels.Success, sTestName + " Tested OK!")	

def TEST_now_Formatted():

	# Set up exit and config classes for unit testing
	#_Config.iDebug = _Config.icLevels.AllDebug    # All Debug during testing or debugging
	_Config.iDebug = _Config.icLevels.Success    # Success when the test is ready
	_Config.caColors.Mute()  # Tone down error and other console colors

	sTestName = "TEST_now_Formatted"
	_Log.dPrint(_Config.icLevels.SomeDebug, sTestName + " Started...")	

	sFormatted = _wpScan.now_Formatted()
	sRegEx = "20[1-2][0-9]-[0-1][0-9]-[0-3][0-9]_[0-2][0-9]-[0-5][0-9]-[0-5][0-9]"
	_Exit.DieIfNotTrue(bool(re.search(sRegEx,sFormatted)), sTestName, "regex check")

	_Config.caColors.Unmute()
	_Log.dPrint(_Config.icLevels.Success, sTestName + " Tested OK!")	

def TEST_evidence_Name_of_URL():

	# Set up exit and config classes for unit testing
	#_Config.iDebug = _Config.icLevels.AllDebug    # All Debug during testing or debugging
	_Config.iDebug = _Config.icLevels.Success    # Success when the test is ready
	_Config.caColors.Mute()  # Tone down error and other console colors

	sTestName = "TEST_evidence_Name_of_URL"
	_Log.dPrint(_Config.icLevels.SomeDebug, sTestName + " Started...")	

	sFormatted = _wpScan.evidence_Name_of_URL("http://www.yahoo.com")
	_Exit.DieIfNoMatch(sFormatted, "http_www.yahoo.com", sTestName, "http://www.yahoo.com")

	sFormatted = _wpScan.evidence_Name_of_URL("htTp://wWw.yaHoo.cOm")
	_Exit.DieIfNoMatch(sFormatted, "http_www.yahoo.com", sTestName, "htTp://wWw.yaHoo.cOm")

	sFormatted = _wpScan.evidence_Name_of_URL("htTp://wWw.yaHoo.cOm/hello?world=too")
	_Exit.DieIfNoMatch(sFormatted, "http_www.yahoo.com", sTestName, "htTp://wWw.yaHoo.cOm/hello?world=too")

	sFormatted = _wpScan.evidence_Name_of_URL("htTpS://wWw.yaHoo.cOm:3452/hello?world=too")
	_Exit.DieIfNoMatch(sFormatted, "https_www.yahoo.com", sTestName, "htTpS://wWw.yaHoo.cOm/hello?world=too")


	# Test some invalid cases
	sFormatted = _wpScan.evidence_Name_of_URL("")
	_Exit.DieIfNoMatch(sFormatted, "", sTestName, "bad 1")

	sFormatted = _wpScan.evidence_Name_of_URL("http://")
	_Exit.DieIfNoMatch(sFormatted, "", sTestName, "bad 2")

	sFormatted = _wpScan.evidence_Name_of_URL("https://:234/hello.com")
	_Exit.DieIfNoMatch(sFormatted, "", sTestName, "bad 3")

	_Config.caColors.Unmute()
	_Log.dPrint(_Config.icLevels.Success, sTestName + " Tested OK!")	


def TEST_create_Folder():

	# Set up exit and config classes for unit testing
	#_Config.iDebug = _Config.icLevels.AllDebug    # All Debug during testing or debugging
	_Config.iDebug = _Config.icLevels.Success    # Success when the test is ready
	_Config.caColors.Mute()  # Tone down error and other console colors

	sTestName = "TEST_create_Folder"
	_Log.dPrint(_Config.icLevels.SomeDebug, sTestName + " Started...")	

	# Empty folder should die
	_Exit.reset()
	_wpScan.create_Folder("")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "empty path")	

	sRootNew = sTestName + "_ROOTNEW"
	sRootExisting = sTestName + "_ROOTEXISTING"
	sSubfolderNew = sTestName + "_SUBNEW"
	sSubfolderExisting = sTestName + "_SUBEXISTING"

	# Create some folders and check on others
	if not os.path.exists(sRootExisting):
		os.mkdir(sRootExisting)
	if not os.path.exists(os.path.join(sRootExisting, sSubfolderExisting)):
		os.mkdir(os.path.join(sRootExisting, sSubfolderExisting))
	_Exit.DieIfTrue(os.path.exists(sRootNew), sTestName, "Root folder " + sRootNew + " already exists - please delete manually!")	
	_Exit.DieIfTrue(os.path.exists(os.path.join(sRootExisting, sSubfolderNew)), sTestName, "Subfolder folder " + os.path.join(sRootExisting, sSubfolderNew) + " already exists - please delete manually!")	

	# Folder that does not exist
	_Exit.reset()
	_wpScan.create_Folder(sRootNew)
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "Folder that does not exist - exited app")	
	_Exit.DieIfNotTrue(os.path.exists(sRootNew), sTestName,      "Folder that does not exist - failed to create")	

	# Folder that does exist
	_Exit.reset()
	_wpScan.create_Folder(sRootExisting)
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "Folder that does exist - exited app")	
	_Exit.DieIfNotTrue(os.path.exists(sRootExisting), sTestName, "Folder that does exist - failed to create")	

	# Subfolder that does not exist
	_Exit.reset()
	_wpScan.create_Folder(os.path.join(sRootExisting, sSubfolderNew))
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName,                              "Subfolder that does not exist - exited app")	
	_Exit.DieIfNotTrue(os.path.exists(os.path.join(sRootExisting, sSubfolderNew)), sTestName, "Subfolder that does not exist - failed to create")	

	# Subfolder that does exist
	_Exit.reset()
	_wpScan.create_Folder(os.path.join(sRootExisting, sSubfolderExisting))
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName,                                   "Subfolder that does exist - exited app")	
	_Exit.DieIfNotTrue(os.path.exists(os.path.join(sRootExisting, sSubfolderExisting)), sTestName, "Subfolder that does exist - failed to create")	

	# Clean up
	os.rmdir(os.path.join(sRootExisting, sSubfolderExisting))
	os.rmdir(os.path.join(sRootExisting, sSubfolderNew))
	os.rmdir(sRootExisting)
	os.rmdir(sRootNew)

	_Config.caColors.Unmute()
	_Log.dPrint(_Config.icLevels.Success, sTestName + " Tested OK!")	

	return


def TEST_purge_Folder():
	# Set up exit and config classes for unit testing
	#_Config.iDebug = _Config.icLevels.AllDebug    # All Debug during testing or debugging
	_Config.iDebug = _Config.icLevels.Success    # Success when the test is ready
	_Config.caColors.Mute()  # Tone down error and other console colors

	sTestName = "TEST_purge_Folder"
	_Log.dPrint(_Config.icLevels.SomeDebug, sTestName + " Started...")	

	# Blank case
	_Exit.reset()
	_wpScan.purge_Folder("")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "blank")	

	# Too short (try to avoid testing root folder case)
	_Exit.reset()
	_wpScan.purge_Folder("slash")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "slash")	

	# Long and exists but invalid
	sLongButInvalid = "012345678901234567890123456789"
	if not os.path.exists(sLongButInvalid):
		os.mkdir(sLongButInvalid)
	_Exit.reset()
	_wpScan.purge_Folder(sLongButInvalid)
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "long but invalid")	
	os.rmdir(sLongButInvalid)

	# Valid and exists (and make sure it's actually gone)
	sValid = "Evidence_2016-10-12_08-24-56"
	if not os.path.exists(sValid):
		os.mkdir(sValid)
	if not os.path.exists(os.path.join(sValid, "a")):
		os.mkdir(os.path.join(sValid, "a"))
	if not os.path.exists(os.path.join(sValid, "b")):
		os.mkdir(os.path.join(sValid, "b"))
	file = open(os.path.join(sValid,"dfile.txt"), 'w')
	file.write("#delete me")
	file.close()
	file = open(os.path.join(os.path.join(sValid, "a"),"cfile.txt"), 'w')
	file.write("#delete me")
	file.close()

	_Exit.reset()
	_wpScan.purge_Folder(sValid)
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "valid - return code")	
	_Exit.DieIfTrue(os.path.exists(sValid), sTestName, "valid - failed to purge")	

	# Valid but does not exist (this is OK)
	_Exit.reset()
	_wpScan.purge_Folder(sValid)
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "valid but does not exist - return code")	

	_Config.caColors.Unmute()
	_Log.dPrint(_Config.icLevels.Success, sTestName + " Tested OK!")	

	return


# Run the tests
_Log.dPrint(_Config.icLevels.Normal, "Now running __test_wpScan_utilities.py")	
TEST_parse_Input_File_Into_Array()
TEST_now_Formatted()
TEST_evidence_Name_of_URL()
TEST_create_Folder()
TEST_purge_Folder()

# Exit the unit test suite cleanly
exit(0)