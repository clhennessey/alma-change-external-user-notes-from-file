# alma-change-external-user-notes-from-file
Convert Alma user notes from external to internal all at once from a file. Presented at IGeLU Developers Day annual conference September 14, 2020

<b>Convert Alma user notes from external to internal</b>

Conference sessions & descriptions: https://igelu.org/conferences/2020-digital-conference/igelu-2020-registration-pages/

Link directly to session description: https://proposalspace.com/p/29242/s
PPT slides from presentation: https://github.com/clhennessey/alma-change-external-user-notes-from-file/blob/master/Can%20we%20fix%20it%20user%20notes%20Hennessey%20IGeLU%202020%20FINAL.zip
Video from presentation: https://www.youtube.com/watch?v=lqyxJ8uEg0s

Alma user notes cannot be deleted or changed if they are marked as "external". 

This is a Python program to change the notes from external to internal from a list of IDs in a file so you can delete or change them inside of Alma or with other API calls. 

Change "strings_to_search" variable to whatever strings you want to match on in the user note text,
and those particular external notes will be turned into internal notes.

Replace api_key in the config.ini file with your API key that allows: User-Production-Read/Write.
Replace na in the config.ini file with your region (na, eu, ca, cn, ap).

Include a list of primary IDs for the input text file, as shown below. 
Errors with reading the IDs will be written to the error.txt file in the same directory.

Known errors: 1. if you replace a user record that has associated roles that did not require 
a service unit before but need one now, you will get errors when re-writing the user record to Alma.
Edit the user record roles in Alma until the user record allows you to re-rewrite it. 
Good candidates to check for a missing service unit: 
Work Order Operator, Receiving Operator, Receiving Operator Limited
2. The file name needs to be in the same directory where you are running the code

This was part of a longer program that does many things to an individual Alma user record, hence the overkill on the
structure of the program. There are plenty of optional print statements in the program so you can check your
user record changes while you use the program.

If you would like a version of the program without an input file to just work on one record at a time, see my other program at: https://github.com/clhennessey/alma-change-external-user-notes

This program is based on this code presented at ELUNA Developer's Day Workshop by Jeremy Hobbs,
linked here: https://github.com/MrJeremyHobbs/ELUNA-2019-Dev-Days-Alma-Course 

Requirements: Python 3.x, modules: <i>requests, xmltodict</i>

Questions, comments, changes?
Contact Christina Hennessey, Systems Librarian at California State University, Northridge
christina.hennessey@csun.edu

![Program with text file name entered](/program-textfilename.png)

![Program completed](/program-success.png)

![Program input file](/IDstofix-file-example.png)


