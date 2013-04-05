/*
Moataz Soliman
*/

Smart House Web Interface
Overview:
This is a web application built using Google App engine using Django templates and libraries ported to Google App Engine.
The web application is an interface that interacts through wireless communication with specific Arduino boards at the house
that are configured and setup to control the appliances at the house and monitor the weather conditions inside the house.
========================================================================================================================================================================================================
How to Run the testing server ( the app ):
Testing the Application

First you need to download a small SDK for Python 2.7 (App Engine SDK) from : https://developers.google.com/appengine/downloads
We are going to be using Google App Engine Launcher by following the next steps :
1- Download or Clone the Whole project in a new folder on your Machine.
2- Open the Google App Engine Launcher that you downloaded with the SDK.
3- You can set up the application by selecting the File menu, Add Existing Application..., then selecting the directory ( select the whole folder that you downloaded the files of the App in) then click open.
4- Click the Run button to start the application, then click the Browse button to view it. Clicking Browse simply loads (or reloads) http://localhost:8080/ in your default web browser.

If you're not using Google App Engine Launcher, start the web server with the following command, giving it the path to the directory that you download the app in:
google_appengine/dev_appserver.py smarhouse/
The web server is now running, listening for requests on port 8080. You can test the application by visiting the following URL in your web browser:

http://localhost:8080/
========================================================================================================================================================================================================