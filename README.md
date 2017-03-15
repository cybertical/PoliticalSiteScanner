# PoliticalSiteScanner
Web site security scanner.  Originally developed in 2016 to analyze political web sites using publicly available information such as headers and CMS artifacts, especially Wordpress artifacts.

## Prerequisites

This program depends on an existing installation of Python on a Linux or BSD operating system.  The application was original developed and is tested on a Mac OS platform (currently Python 2.7.12.2 on Mac OS 10.12.1).     

## Installation

Copy this project into a local folder.  Run "python pScan.py" and look for a colored help message (similar to the "Usage" section below) to make sure the prerequisites are in place.   

    python pScan.py

## Usage

    Cybertical Political Site Scanner by (info@cybertical.com) vXX.XX

    usage: pScan.py [-h] [-i INPUTFILE] [-re REPROCESSDATETIME] [-o OUTPUTFILE]
                    [-l LOGFILE] [-d DEBUG] [-nph NTLMPROXYHOST]
                    [-npu NTLMPROXYUSERNAME] [-pe | -no-pe] [-rse | -no-rse]

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUTFILE          input file of URLs (REQUIRED)
      -re REPROCESSDATETIME
                            reprocess content from DateTime formatted as YYYY-MM-
                            DD_HH-MM-SS or YYYY:MM:DD HH:MM:SS (Optional; helpful
                            for stealth or for revised findings after new version)
      -o OUTPUTFILE         use this output file for findings in CSV format
                            (Optional; otherwise YYYY-MM-DD_HH-MM-SS_results.csv)
      -l LOGFILE            use this output file for detailed log (Optional;
                            otherwise YYYY-MM-DD_HH-MM-SS_log.txt)
      -d DEBUG              debug level (1=err 2=warn 3=OK (def), 4=debug, 5=all)
      -nph NTLMPROXYHOST    NTLM Proxy Host (OPTIONAL)
      -npu NTLMPROXYUSERNAME
                            NTLM Proxy Username (OPTIONAL)
      -pe                   Purge Evidence Folder (Optional)
      -no-pe                Do Not Purge Evidence Folder (Default, Optional)
      -rse                  Rescan Pages That Previously Got Errors (Optional)
      -no-rse               Do Not Rescan Pages That Previously Got Errors
                            (Default, Optional)

## How To Use

This application examines the public security attributes of a list of target sites and scores their apparent openness to cyberattack or at least potentially malicious inspection.  This application is not a "hacking tool" and does not perform any hacking operations, but it does help expose some of the attributes hackers would find interesting about a list of targets, and helps determine which targets appear to be "softer" than others.  

To avoid hammering potential targets, the application can be configured to gather evidence and findings incrementally.   

### Basic Invocation

The basic invocation will read in a list of URLs from a text file.  It will write results into a "YYYY-MM-DD_HH-MM-SS_results.csv" file and a log into a "YYYY-MM-DD_HH-MM-SS_log.txt" file.  

    python pScan.py -i ListOfURLs.txt

You should start with a list of "friendly" URLs entirely under your control until you become familiar with the application's options.  Pay special attention to the files and folders created by the application, and read on for more information about how to use them.

### Advanced Invocation

Before you point this application at any sites not under your control, you should understand how to use and reuse evidence folders.  The first time you run the application it will create a timestamped evidence folder such as "Evidence_2016-11-02_01-09-27".  Within this folder are subfolders for each site that was inspected.  Within each of these subfolders are "evidence" files that contain the complete headers and contents of each page examined, or errors for pages that could not be reached.  

To avoid hammering a target site, evidence folders should be reused via the "-re" command.  For example:

    python pScan.py -i ListOfURLs.txt -re 2016-11-02_01-09-27
    
By default, all pages that were previously downloaded or encountered errors will be ignored in subsequent scans.  To force rescans of specific sites, delete that folder from the evidence folder.  To force rescans of particular pages, delete those specific evidence files or error files.  And, to force rescans of all pages that led to errors, use the "-rse" command.      

    python pScan.py -i ListOfURLs.txt -rse -re 2016-11-02_01-09-27

### CSV Report

The CSV report contains the following fields for each site studied:

* URL - Base URL of site, such as http://cybertical.com
* HeaderServer - Reported name of server, such as "Apache"
* HeaderXPoweredBy - Reported application, such as "PHP/5.4.0"
* HTTPSEnabled - "True" if HTTPS is enabled on the site, otherwise "False"
* HTTPSRequired - "True" if HTTPS is required on the site, otherwise "False"
* IsWordpress - "True" if Wordpress powers the site, otherwise "False"
* WPVersion - If Wordpress powers the site, this is the version it appears to be
* WPLoginPage - If Wordpress powers the site, this is "True" if the login page is available
* WPRegPage - If Wordpress powers the site, this is "True" if the registration page is available
* WPLostPass - If Wordpress powers the site, this is "True" if the lost password page is available
* WPWordfence - If Wordpress powers the site, this is "True" if the "WordFence" plug-in appears to be in place (experimental)
* WPStopEnum - If Wordpress powers the site, this is "True" if the "StopEnum" plug-in appears to be in place (experimental)
* WPAuthorUsers - Number of Wordpress users (authors) detected through username enumeration
* WPPostUsers - Number of Wordpress users (authors) detected on public posts
* WPDefaultAdmin - If Wordpress powers the site, this is "True" if the default admin ("admin") appears to be available
* WPLikelyAdmin - If Wordpress powers the site, this is our best guess at the site admin's username
* WPBusiestUser - If Wordpress powers the site, this appears to be the busiest user (author) on the site
* WPBusiestPercentage - If Wordpress powers the site, this appears to be the percentage of posts created by the busiest user

## History

In 2015 Cybertical founder Jonathan Lampe presented a session called "Evaluating the Security of Potential Partners - Without Permission!" to the national (ISC)2 Congress (the CISSP certification body) in Anaheim, California.  This session presented several reconnaisance techniques that IT personnel could use against publicly available information to evaluate the cybersecurity posture of potential partners.  Unlike a "penetration test" or an "ethical hack", no explicit permission is necessary to perform this type evaluation since it relies on information that the targeted partners freely reveal to the general public (including anyone who connects to their public interfaces).  

In late 2015, Lampe used these techniques (now as an employee of the InfoSec Institute) to explore the security profile of US 2016 presidential candidates, finding that most had serious flaws.  The results of these studies were published in several national publications (e.g., Politico) and appear to have led to the rapid correction of most flaws on the web sites of the remaining candidates.  Lampe presented a summary of multiple rounds of analysis at Thotcon in Chicago and revealed an additional finding: a phishing vulnerability in candidate Clinton's site that remained unfixed through the end of the election.  

In mid 2016, Lampe formed Cybertical and developed the first version of this utility, which was used to examine and score the cybersecurity of 67 US senatorial candidates.  The results of this study were published several weeks ahead of the election and were picked up by regional media (such as NBC4 in Washington DC) who used them in coverage of their federal candidates.  At the same time Cybertical began offering affordable cybersecurity evaluations of political sites as its primary service.  

In early 2017, Lampe was invited to speak at Milwaukee's CypherCon convention and decided to release a version of the utility used to examine and score political web sites in advance of his talk.  This is that utility.  
