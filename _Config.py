'''
Global configuration file
'''

# DEFAULT VALUES
iDebug = 3  # (Success)

# Possible debug levels shown below ("ic" = "Integer Constant")
class icLevels: 
    Error = 1      # Error
    Warning = 2    # Warning
    Success = 2.5    # Success
    Normal  = 3    # (terminal color) Success
    SomeDebug = 4  # Some Debug
    AllDebug = 5   # All Debug

# Terminal display colors ("ca" = "Character Array") 
# Originally imported from http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
# And augmented with ANSI sequences from https://pypi.python.org/pypi/colorama
class caColors:
    #HEADER = '\033[95m'
    #OKBLUE = '\033[94m'
    #OKGREEN = '\033[92m'
    #WARNING = '\033[93m'
    #FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m' 
    Error = '\033[1m\033[91m'
    Warning = '\033[1m\033[93m'
    Success = '\033[92m'
    Normal = '\033[0m'  # Reset terminal
    SomeDebug = '\033[2m'
    AllDebug = '\033[2m'
    Red = '\033[31m'
    Green = '\033[32m'
    Yellow = '\033[33m'
    Blue = '\033[34m'
    Magenta = '\033[35m'
    Cyan = '\033[36m'
    White = '\033[37m'

    # Function to "mute" the colors (handy when running unit tests)
    # Also adds a severity prefix
    @staticmethod
    def Mute():
        caColors.Error = '\033[2m ERROR:'        # Reset terminal
        caColors.Warning = '\033[2m WARNING:'    # Reset terminal
        caColors.Success = '\033[2m SUCCESS:'    # Reset terminal
        caColors.Normal = '\033[2m'              # Reset terminal

    # Function to "un-mute" the colors 
    @staticmethod
    def Unmute():
        caColors.Error = '\033[1m\033[91m'
        caColors.Warning = '\033[1m\033[93m'
        caColors.Success = '\033[92m'
        caColors.Normal = '\033[0m'  # Reset terminal

# Regular expressions useful for validating various strings
class sRegExes:
    ValidIP4Address = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
    ValidHostname = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$";