'''
PoliticalSiteScanner by Cybertical

Web site security scanner. Originally developed in 2016 to analyze political
web sites using publicly available information such as headers and CMS artifacts, 
especially Wordpress artifacts.

Performs a non-invasive (zero hacking) review of a list of URLs.  

Licensed under the GNU GENERAL PUBLIC LICENSE v3.

For more information see: 
https://github.com/cybertical/PoliticalSiteScanner

'''

# Import own master class
import _pScan		# Class to allow clean unit testing

# # # RUN THE PROGRAM
_pScan.Run()