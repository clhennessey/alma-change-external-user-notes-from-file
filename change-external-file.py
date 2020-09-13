from tkinter import *
from tkinter import messagebox
import requests
import configparser
import xmltodict
import pprint
import string

# configurations ##############################################################
config = configparser.ConfigParser()
config.read('config.ini')

apikey   = config['misc']['apikey']
region = config['misc']['region']

# main program ################################################################
def main(*args):
    
    # open the file to write errors, assumes in the same directory
    error_file_object = open("error.txt","w")
    try: 
        error_file_object.write("Beginning of error file for change-external-file program.\n")
    except IOError:
        gui.msgbox(error_file_object, "Could not write the error file in the current path")
        error_file_object.close()
        return
    
    # user ID file
    user_file_name = gui.get_user()
    if user_file_name == "":
        error_file_object.write("Bad user file name: "+user_file_name)
        gui.msgbox(user_file_name, "Bad user file name")
        error_file_object.close()
        return
    # strip leading and trailing spaces
    user_file_name = user_file_name.strip()
    print("user file name = ", user_file_name)
    gui.clear_user()
    
    # open the file to read, assumes in the same directory
    try: 
        with open(user_file_name, 'r') as file_object:
            user_ids_from_file = file_object.read().splitlines()
 #           print("Here are the lines in the file:", user_ids_from_file)
    except IOError:
        error_file_object.write("File name does not exist in the current path: "+user_file_name)
        gui.msgbox(user_file_name, "This file name does not exist in the current path")
        error_file_object.close()
        return
         
    zcount=0
    # start loop
    for z in user_ids_from_file:
        print("user", zcount, ":", z)
        user = z
        zcount = zcount + 1
        #if this is a blank line in the file, just skip it
        if user == "":
    #       gui.msgbox(user, "Bad user ID.")
           continue 
       
        #region should have a format like na, eu, ca, cn, ap
    
        # get user record
    #   print(region, "\n")
        r = requests.get("https://api-"+region+".hosted.exlibrisgroup.com/almaws/v1/users/"+user+"?user_id_type=all_unique&status=ACTIVE&apikey="+apikey)
        
        # check for errors
        errors_exist = check_errors(r)
        if errors_exist[0] == True:
            error = errors_exist[1]
            print("error was:", error)
            if error.startswith("API-key not defined"):
                print("problem with API Key, write this to an error file\n")
                error_file_object.write("Problem with API Key: "+apikey)
                gui.msgbox(user, error)
                error_file_object.close()
                return
            if "not found" in error:
                print("There was an error with user",user,"\n")
            # not sure what other errors we might find here so check this    
            error_file_object.write(error+"\n")
 
    #        gui.msgbox(user, error)
            continue
 
      
        # parse user record. 
        original_user_xml = r.text
    #    print(original_user_xml, "\n")
        user_dict = xmltodict.parse(r.text,dict_constructor=dict)
   #     print("all user_dict before change", user_dict)
        primaryID = user_dict['user']['primary_id']
        firstname = user_dict['user']['first_name']
        lastname = user_dict['user']['last_name']
        usernotesbase = user_dict['user']['user_notes']
        # strings_to_search must be in lowercase!
        strings_to_search = ["pcode3","p type", "cl rtrnd", "tot chkout", "tot renwal", "pcode2", "pmessage"]
    
        if usernotesbase == None:
            print("there were no user notes in this one\n")
   #         gui.msgbox("all okay","No user notes to update in this record")
        else:
            print("there are user notes here\n")
          
            print("before user_dict change, ",user_dict['user']['user_notes']['user_note'])
            eachusernotesbase = user_dict['user']['user_notes']['user_note']
        #    print(type(eachusernotesbase))
   
           # if eachusernotesbase is one note, it will be dict, if it is several, it will be a list
            if type(eachusernotesbase) == dict:
                new_user_dict_notes = {}
                if any (c in eachusernotesbase['note_text'].lower() for c in strings_to_search): 
                       print("the note text is: ",eachusernotesbase['note_text'])
                       segment_type = eachusernotesbase['@segment_type']
                       print("segment_type:", segment_type)
                       if (segment_type == "External"):
                           print("this note is an external note, modify this note\n")
                           eachusernotesbase['@segment_type'] = "Internal"
                       else:
                           print("this note is an internal note, keep this note\n")
                       new_user_dict_notes = eachusernotesbase
                else:
                       print("the note text is: ",eachusernotesbase['note_text'])
                       print("this note is not in the match list, keep this note\n")
                       new_user_dict_notes = eachusernotesbase
                    
            else:         #this record has several notes and is a list
                new_user_dict_notes = []
                count = 0
                for k in eachusernotesbase:
                    print(f"user note #{count}")
                    count = count + 1
                    
                    text_of_note = k['note_text']
                    print("The note text is: ", text_of_note)
                    if any(c in text_of_note.lower() for c in strings_to_search):
                       segment_type = k['@segment_type']
                       print("segment_type:", segment_type)
                       if (segment_type == "External"):
                           print("this note is an external note, modify this note\n")
                           k['@segment_type'] = "Internal"
                       else:
                           print("this note is an internal note, keep this note\n")
                       new_user_dict_notes.append(k)
                    else:
                   
                       print("this note is not in the match list, keep this note\n")
         #               print(f"k is currently {k} \n")
          #              print(f"new_user_dict_notes is currently {new_user_dict_notes} \n")
                       new_user_dict_notes.append(k)
                
            if user_dict['user']['user_notes'] != None:
                user_dict['user']['user_notes']['user_note'] = new_user_dict_notes
                print("after user_dict change here is the note part, ",user_dict['user']['user_notes']['user_note'],"\n")
          #  print(f"here is the whole user_dict: {user_dict} \n")
                 
            # remake the XML
            new_user_xml = xmltodict.unparse(user_dict)
      #      print(new_user_xml)
      
      # comment out the next line if you don't want to write anything during testing
            r = putXML("https://api-na.hosted.exlibrisgroup.com/almaws/v1/users/"+user+"?user_id_type=all_unique&apikey="+apikey, new_user_xml)
            
            # check for errors
            errors_exist = check_errors(r)
            if errors_exist[0] == True:
               print("there was an error in the putXML for user =", user)
               error = errors_exist[1]
               error_file_object.write("User "+user+" had this error: "+error+"\n")
     #         gui.msgbox(user, error)
               continue
                           
             #finish
            gui.update_status_success(primaryID, firstname, lastname)
             
    #end of text loop here
    print("we are done processing the file\n")
    error_file_object.write("The program has finished processing the file.")
    error_file_object.close()
# end of main here
         
 
            
# functions ###################################################################

def putXML(url, xml):
    headers = {'Content-Type': 'application/xml', 'charset':'UTF-8'}
    r = requests.put(url, data=xml.encode('utf-8'), headers=headers)
    return r

def check_errors(r):
    if r.status_code != 200:
        errors = xmltodict.parse(r.text)
        error = errors['web_service_result']['errorList']['error']['errorMessage']
        return True, error
    else: 
        return False, "OK"
            
# gui #########################################################################
class gui:
    def __init__(self, master):
        self.master = master
        master.title("CSUN change user notes to external from a file")
        master.resizable(0, 0)
        master.minsize(width=600, height=100)
        master.iconbitmap("csunalone.ico")

        logo = PhotoImage(file="csunalone.png")
        self.logo = Label(image=logo)
        self.logo.image = logo
        self.logo.pack()

        self.status_title = Label(height=1, text="Enter the text filename of primary IDs to begin.", font="Consolas 12 italic")
        self.status_title.pack(fill="both", side="top")

        self.status_added = Label(height=1, text="READY", font="Consolas 12 bold", fg="green")
        self.status_added.pack(fill="both", side="top")

        self.user_entry_field = Entry(font="Consolas 16")
        self.user_entry_field.focus()
        self.user_entry_field.bind('<Key-Return>', main)
        self.user_entry_field.pack(fill="both", side="top")
        
        self.scan_button = Button(text="SCAN", font="Arial 16", command=main)
        self.scan_button.pack(fill="both", side="top")
        
    def msgbox(self, title, msg):
        messagebox.showerror("Attention", msg)
        gui.update_status_failure(title, msg)
        
    def get_user(self):
        user = self.user_entry_field.get()
        user = user.replace(" ", "")
        return user
        
    def clear_user(self):
        self.user_entry_field.delete(0, END)
        self.status_title.config(text="")
        self.status_added.config(text="")
        
    def update_status_success(self, primaryID, first, last):
        self.status_title.config(text=primaryID+" "+first+" "+last)
        self.status_added.config(text="NOTES SUCCESSFULLY UPDATED IN USER DATABASE", fg="green")
        
    def update_status_failure(self, title, msg):
        self.status_title.config(text=title)
        self.status_added.config(text=msg, fg="red")
        
root = Tk()
gui = gui(root)
root.mainloop()