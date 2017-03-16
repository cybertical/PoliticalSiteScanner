'''
State file to maintain global variables
Do NOT put any functions in here!
'''

# Global constant variables
sVersion = '0.9'
sProgramName = "Political Site Scanner"
sAuthor = "Jonathan Lampe (info@cybertical.com)"
sFullDateTimeRegEx = "20[1-2][0-9]-[0-1][0-9]-[0-3][0-9]_[0-2][0-9]-[0-5][0-9]-[0-5][0-9]"  # e.g., 2016-10-12_08-24-56
sRootFolderRegEx = "Evidence_20[1-2][0-9]-[0-1][0-9]-[0-3][0-9]_[0-2][0-9]-[0-5][0-9]-[0-5][0-9]"  # e.g., Evidence_2016-10-12_08-24-56
iMaxWordpressUsers = 200          # We will look for up to this many author users
iMaxWordpressUsersNotFound = 10   # If we have this many misses in a row we will stop looking
iMaxFeedPages = 50				  # We will try up to this many feed pages (a single miss stops the feed search)

# Global variables - these will generally be overridden at runtime
sFormattedDateTime = 'YyYy-Mm-Dd_Hh-Mm-Ss'   
sEvidenceFolder = "" 
sNTLMProxyUsername = ""
sNTLMProxyPassword = ""
sNTLMProxyHost = ""
sInputFile = ""
sLogFile = ""
sOutputFile = ""
sReprocessDateTime = ""
bPurgeEvidence = False
bRescanStubErrors = False

# Global headers - may be overwritten
# Upgrade-Insecure-Requests: 1
# User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
# Accept-Encoding: gzip, deflate, sdch
# Accept-Language: en-US,en;q=0.8
# Connection: close
sHeaderUpgradeInsecureRequests = "1"
sHeaderUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B350 Safari/8536.25"
sHeaderAccept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
#sHeaderAcceptEncoding = "gzip, deflate, sdch"
sHeaderAcceptEncoding = ""  # No encoding (otherwise servers will actually provide it!)
sHeaderAcceptLanguage = "en-US,en;q=0.8"
sHeaderConnection = "close"
sLastURL = "http://www.yahoo.com"  # Used in the referrer field, updated after each request

# Global statistics
iStatSitesTested = 0
iStatWordpressSitesFound = 0
iStatRequestsMade = 0

def asString():
	return "" + \
		"sVersion = " + sVersion + "\n" \
		"sProgramName =  " + sProgramName + "\n" \
		"sAuthor =  " + sAuthor + "\n" \
		"sFullDateTimeRegEx = " + sFullDateTimeRegEx + "\n" \
		"sRootFolderRegEx =  " + sRootFolderRegEx + "\n" \
		"sMaxWordpressUsers = " + str(iMaxWordpressUsers) + "\n" \
		"sMaxWordpressUsersNotFound = " + str(iMaxWordpressUsersNotFound) + "\n" \
		"iMaxFeedPages = " + str(iMaxFeedPages) + "\n" \
		"sFormattedDateTime =  " + sFormattedDateTime + "\n" \
		"sEvidenceFolder =  " + sEvidenceFolder + "\n" \
		"sNTLMProxyHost =  " + sNTLMProxyHost + "\n" \
		"sNTLMProxyUsername =  " + sNTLMProxyUsername + "\n" \
		"sNTLMProxyPassword =  " + str(len(sNTLMProxyPassword)) + " character password\n" \
		"sInputFile =  " + sInputFile + "\n" \
		"sLogFile =  " + sLogFile + "\n" \
		"sOutputFile =  " + sOutputFile + "\n" \
		"sReprocessDateTime =  " + sReprocessDateTime + "\n" \
		"bPurgeEvidence =  " + str(bPurgeEvidence) + "\n" \
		"bRescanStubErrors =  " + str(bRescanStubErrors) + "\n" \
		"sHeaderUpgradeInsecureRequests =  " + sHeaderUpgradeInsecureRequests + "\n" \
		"sHeaderUserAgent =  " + sHeaderUserAgent + "\n" \
		"sHeaderAccept =  " + sHeaderAccept + "\n" \
		"sHeaderAcceptEncoding =  " + sHeaderAcceptEncoding + "\n" \
		"sHeaderAcceptLanguage =  " + sHeaderAcceptLanguage + "\n" \
		"sHeaderConnection =  " + sHeaderConnection + "\n" \
		"sLastURL =  " + sLastURL + "\n" \
		"iStatSitesTested =  " + str(iStatSitesTested) + "\n" \
		"iStatWordpressSitesFound =  " + str(iStatWordpressSitesFound) + "\n" \
		"iStatRequestsMade =  " + str(iStatRequestsMade) + "\n"