# __test_wpScan_validate.py

# Reference target modules
import _wpScan

# Reference custom modules
import _Exit, _Config, _Log

# Reference system modules
import os

def TEST_validate_Input_File():

	# Set up exit and config classes for unit testing
	#_Config.iDebug = _Config.icLevels.AllDebug    # All Debug during testing or debugging
	_Config.iDebug = _Config.icLevels.Success    # Success when the test is ready
	_Exit.ExitOnExit = False
	_Config.caColors.Mute()  # Tone down error and other console colors

	sTestName = "TEST_validate_Input_File"
	_Log.dPrint(_Config.icLevels.SomeDebug, sTestName + " Started...")	

	# Test for blank file
	_Exit.reset()
	_wpScan.validate_Input_File("")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "blank file")

	# Test the reset function
	_Exit.reset()
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "reset()")

	# Test a bad file
	_Exit.reset()
	_wpScan.validate_Input_File("notthere.does.not.exist")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "bad file")

	# Test a good file
	_Exit.reset()
	sRealFile = '__unittest_wordpress-scan_validate_Input_File.deleteme'
	file = open(sRealFile, 'w')
	file.write("delete me")
	file.close()
	_wpScan.validate_Input_File(sRealFile)
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "good file")
	os.remove(sRealFile)

	_Config.caColors.Unmute()
	_Log.dPrint(_Config.icLevels.Success, sTestName + " Tested OK!")	

def TEST_validate_Output_File():

	# Set up exit and config classes for unit testing
	#_Config.iDebug = _Config.icLevels.AllDebug    # All Debug during testing or debugging
	_Config.iDebug = _Config.icLevels.Success    # Success when the test is ready
	_Config.caColors.Mute()  # Tone down error and other console colors

	sTestName = "TEST_validate_Output_File"
	_Log.dPrint(_Config.icLevels.SomeDebug, sTestName + " Started...")	

	# Test for blank files
	_Exit.reset()
	_wpScan.validate_Output_File("", "Test")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "blank file 1")
	_Exit.reset()
	_wpScan.validate_Output_File(" ", "Test")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "blank file 2") # Single space
	_Exit.reset()
	_wpScan.validate_Output_File(" 		 ", "Test")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "blank file 3")  # Tabs

	# Test for 'None'
	_Exit.reset()
	_wpScan.validate_Output_File("None", "Test")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "None file")  

	# Test a missing but valid file
	_Exit.reset()
	_wpScan.validate_Output_File("notthere.does.not.exist", "Test")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "missing file")  

	# Test a good file
	sRealFile = '__unittest_wordpress-scan_validate_Output_File.deleteme'
	file = open(sRealFile, 'w')
	file.write("delete me")
	file.close()
	_Exit.reset()
	_wpScan.validate_Output_File(sRealFile, "Test")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "existing file")  
	os.remove(sRealFile)

	_Config.caColors.Unmute()
	_Log.dPrint(_Config.icLevels.Success, sTestName + " Tested OK!")	

def TEST_validate_And_Normalize_DateTime():

	# Set up exit and config classes for unit testing
	#_Config.iDebug = _Config.icLevels.AllDebug    # All Debug during testing or debugging
	_Config.iDebug = _Config.icLevels.Success    # Success when the test is ready
	_Exit.ExitOnExit = False
	_Config.caColors.Mute()  # Tone down error and other console colors

	sTestName = "TEST_validate_And_Normalize_DateTime"
	_Log.dPrint(_Config.icLevels.SomeDebug, sTestName + " Started...")	

	# Test blank 
	_Exit.reset()
	sTest = _wpScan.validate_And_Normalize_DateTime("")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "blank")

	# Test incomplete
	_Exit.reset()
	sTest = _wpScan.validate_And_Normalize_DateTime("201-1-2 4:2:3")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "incomplete")

	# Test invalid
	_Exit.reset()
	sTest = _wpScan.validate_And_Normalize_DateTime("201X-15-14 10-12-32")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "invalid")

	# Test valid
	_Exit.reset()
	sTest = _wpScan.validate_And_Normalize_DateTime("2016-10-12_23-59-59")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "valid 1 - exit code")
	_Exit.DieIfNoMatch(sTest, "2016-10-12_23-59-59", sTestName, "valid 1 - value")

	_Exit.reset()
	sTest = _wpScan.validate_And_Normalize_DateTime("2016:10:12 23:59:59")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "valid 2 - exit code")
	_Exit.DieIfNoMatch(sTest, "2016-10-12_23-59-59", sTestName, "valid 2 - value")

	_Config.caColors.Unmute()
	_Log.dPrint(_Config.icLevels.Success, sTestName + " Tested OK!")	

def TEST_validate_Existing_Evidence_Folder():

	# Set up exit and config classes for unit testing
	#_Config.iDebug = _Config.icLevels.AllDebug    # All Debug during testing or debugging
	_Config.iDebug = _Config.icLevels.Success    # Success when the test is ready
	_Exit.ExitOnExit = False
	_Config.caColors.Mute()  # Tone down error and other console colors

	sTestName = "TEST_validate_Existing_Evidence_Folder"
	_Log.dPrint(_Config.icLevels.SomeDebug, sTestName + " Started...")	

	_Exit.reset()
	sTest = _wpScan.validate_Existing_Evidence_Folder("")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "blank")

	_Exit.reset()
	sTest = _wpScan.validate_Existing_Evidence_Folder("thisfolderdoesnotexist")
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsError(), sTestName, "not there")

	sFolder = sTestName + "_TestFolder"
	if not os.path.exists(sFolder):
		os.mkdir(sFolder)
	_Exit.reset()
	sTest = _wpScan.validate_Existing_Evidence_Folder(sFolder)
	_Exit.DieIfNotTrue(_Exit.LastExitCode_IsNotSet(), sTestName, "valid")		
	os.rmdir(sFolder)

	_Config.caColors.Unmute()
	_Log.dPrint(_Config.icLevels.Success, sTestName + " Tested OK!")	



# Run the tests
_Log.dPrint(_Config.icLevels.Normal, "Now running __test_wpScan_validate.py")	
TEST_validate_Input_File()
TEST_validate_Output_File()
TEST_validate_And_Normalize_DateTime()
TEST_validate_Existing_Evidence_Folder()

# Exit the unit test suite cleanly
exit(0)