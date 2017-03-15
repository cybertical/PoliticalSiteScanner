'''
Replaces "exit()" with something that can be used in unit tests
'''

import _Log
import _Config
import sys

# Unit tests should set this to true
ExitOnExit = True

# This is set by the exit function and is available for inspection in unit tests
ExitCode_NotSet = -1
LastExitCode = ExitCode_NotSet

# Cleanly exits the calling program or just captures the return code
def exit(ExitCode):
	global LastExitCode
	LastExitCode = ExitCode
	#_Log.dPrint(_Config.icLevels.AllDebug, "_Exit.exit() LastExitCode=" + str(LastExitCode))
	if(ExitOnExit):
		_Log.dPrint(_Config.icLevels.SomeDebug, "Exiting program with return code of " + str(ExitCode))
		sys.exit(ExitCode)
	else:
		_Log.dPrint(_Config.icLevels.SomeDebug, "Exit halted - would have returned code of " + str(ExitCode))

# Resets the exit object (should mainly be used by unit tests)
def reset():
	global LastExitCode
	LastExitCode = ExitCode_NotSet
	#_Log.dPrint(_Config.icLevels.AllDebug, "_Exit.reset() LastExitCode=" + str(LastExitCode))

# Returns true if last exit code indicates an error
def LastExitCode_IsError():
	#_Log.dPrint(_Config.icLevels.AllDebug, "_Exit.LastExitCode_IsError LastExitCode=" + str(LastExitCode))
	if(LastExitCode > 0):
		return True
	return False

# Returns true if last exit code indicates an successful completion
def LastExitCode_IsSuccess():
	#_Log.dPrint(_Config.icLevels.AllDebug, "_Exit.LastExitCode_IsSuccess LastExitCode=" + str(LastExitCode))
	if(LastExitCode == 0):
		return True
	return False

# Returns true if last exit code does not appear to be set
def LastExitCode_IsNotSet():
	#_Log.dPrint(_Config.icLevels.AllDebug, "_Exit.LastExitCode_IsNotSet LastExitCode=" + str(LastExitCode))
	#_Log.dPrint(_Config.icLevels.AllDebug, "_Exit.LastExitCode_IsNotSet ExitCode_NotSet=" + str(ExitCode_NotSet))
	if(LastExitCode == ExitCode_NotSet):
		return True
	return False

def DieIfTrue(value, CallingModule, CallingContext):
	if(value == True):
		_Config.caColors.Unmute()
		_Log.dPrint(_Config.icLevels.Error, "DieIfTrue FAILED in " + CallingModule + " at " + CallingContext + "!")
		global ExitOnExit
		ExitOnExit = True
		exit(255)

def DieIfNotTrue(value, CallingModule, CallingContext):
	if(value != True):
		_Config.caColors.Unmute()
		_Log.dPrint(_Config.icLevels.Error, "DieIfNotTrue FAILED in " + CallingModule + " at " + CallingContext + "!")
		global ExitOnExit
		ExitOnExit = True
		exit(255)

def DieIfNoMatch(tested, expected, CallingModule, CallingContext):
	if(tested != expected):
		_Config.caColors.Unmute()
		_Log.dPrint(_Config.icLevels.Error, "DieIfNoMatch FAILED in " + CallingModule + " at " + CallingContext + "! Expected:" + str(expected) + " Got:" + str(tested))
		global ExitOnExit
		ExitOnExit = True
		exit(255)
