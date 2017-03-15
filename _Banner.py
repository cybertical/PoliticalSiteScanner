'''
Prints out a pretty banner
'''
import _Log
import _Config

def Banner(sMessage):
    "Writes a banner followed by an optional message."
    
    _Log.cPrintString(_Config.caColors.Cyan, 'Cybertical')
    _Log.cPrint("boldwhite", ' ' + sMessage)
    
    return 


