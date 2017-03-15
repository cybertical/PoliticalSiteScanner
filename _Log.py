'''
Global log and console display functions
'''
import _Config   # Global configuration (JGL)
# System functions
import sys, time 

DebugLogPath = ""

# Sets up a new file
def StartLogFile(sFilename, sProgramName, sVersion):
    global DebugLogPath
    DebugLogPath = sFilename
    #with open(DebugLogPath, 'w+') as file:
    with open(DebugLogPath, 'a') as file:
        file.write("# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #")
        file.write("# Debugging/Trace for " + sProgramName + "\n")
        file.write("# Created " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")
        file.write("# By " + sProgramName + " v" + sVersion + "\n")
        file.write("# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #")

# Writes a message out the listed Debug Log (if any)
def logPrint(sMessage):
    if(len(DebugLogPath) > 0):
        with open(DebugLogPath, 'a') as file:
            # Write out date formatted, severity messages (severity is prepended by submitting routine)
            file.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " " + sMessage + '\n')

# Writes a "debugging" message to the console and or log as appropriate
def dPrint(iLevel, sMessage):
    "Writes a message if the provided level is equal or less than global level."

    # Print to log
    if(iLevel == _Config.icLevels.Error):
        logPrint("ERROR: " + sMessage)
    if(iLevel == _Config.icLevels.Warning):
        logPrint("WARNING: " + sMessage)
    if(iLevel == _Config.icLevels.Success):
        logPrint("SUCCESS: " + sMessage)
    if(iLevel == _Config.icLevels.Normal):
        logPrint("NORMAL: " + sMessage)
    if(iLevel == _Config.icLevels.SomeDebug):
        logPrint("SOMEDEBUG: " + sMessage)
    if(iLevel == _Config.icLevels.AllDebug):
        logPrint("ALLDEBUG: " + sMessage)
    
    # Error
    if(iLevel <= _Config.iDebug) & (iLevel == _Config.icLevels.Error):
        print _Config.caColors.Error + sMessage + _Config.caColors.ENDC 
        print('\a')   # Bell sound
        return
    
    # Warning        
    if(iLevel <= _Config.iDebug) & (iLevel == _Config.icLevels.Warning):
        print _Config.caColors.Warning + sMessage + _Config.caColors.ENDC 
        return
    
    # Success (green)        
    if(iLevel <= _Config.iDebug) & (iLevel == _Config.icLevels.Success):
        print _Config.caColors.Success + sMessage + _Config.caColors.ENDC 
        return
    
    # Normal (terminal color Success)        
    if(iLevel <= _Config.iDebug) & (iLevel == _Config.icLevels.Normal):
        print _Config.caColors.Normal + sMessage + _Config.caColors.ENDC 
        return
    
    # Some Debug        
    if(iLevel <= _Config.iDebug) & (iLevel == _Config.icLevels.SomeDebug):
        print _Config.caColors.SomeDebug + sMessage + _Config.caColors.ENDC 
        return
    
    # All Debug        
    if(iLevel <= _Config.iDebug) & (iLevel == _Config.icLevels.AllDebug):
        print _Config.caColors.AllDebug + sMessage + _Config.caColors.ENDC 
        return

    # If no message was printed head back anyway    
    return

# Writes a message to the console in a particular color (also to log as appropriate)
def cPrint(sColor, sMessage):
    "Writes a colored message with a line feed to the console."

    logPrint("CONSOLE(" + sColor + "): " + sMessage)

    if sColor == 'white':
        print _Config.caColors.White + sMessage + _Config.caColors.ENDC 
        return

    if sColor == 'boldwhite':
        print _Config.caColors.BOLD + _Config.caColors.White + sMessage + _Config.caColors.ENDC 
        return

    if sColor == 'green':
        print _Config.caColors.Green + sMessage + _Config.caColors.ENDC 
        return

    if sColor == 'red':
        print _Config.caColors.Red + sMessage + _Config.caColors.ENDC 
        return

    if sColor == 'blue':
        print _Config.caColors.Blue + sMessage + _Config.caColors.ENDC 
        return

    # If no matching color was provided, print a normal message
    print sMessage    
    return

def cPrintString(sColor, sString):
    "Writes a bold colored string with no line feed to the log."
    #print _Config.caColors.BOLD + caColor + cChar + _Config.caColors.ENDC
    sys.stdout.write(_Config.caColors.BOLD + sColor + sString + _Config.caColors.ENDC)
    logPrint("CONSOLE-nolinefeed(" + sColor + "): " + sString)
    return
    