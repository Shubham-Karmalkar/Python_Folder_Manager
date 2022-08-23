import json
import os
import sys
import platform
import shutil

# User Settings
"""
1. When Script is run check if extension mapping file is available or not
2. If not then Proceed as below:
3. Creating mapping of extensions with user required names
4. Find file extension to store that data in user space(using JSON)
"""

# Working Priciples
"""
1. Read the whole directory
2. list all the files only
3. list all the folders only
4. map over all the files 
    a. check if file is valid file or not 
    b. check whether file extension has a folder for its own or not
        i. if it does not have folder then create one add that folder in folders only list
    c. then save the file in that folder 
"""
# Adding new Features:
"""
    1.Adding recuresive Feature So that we can clean a directory recursively
    2.Add use_default(True/False) field so that we know weather user want to user default
      config to use while cleaning the directory
        a. if user don't want to use default config then create temperory space for cleaning that
            Folder
    3.User must be able to update his/her Default config
    4.Make this as good command line tool
     
"""

# default_config_list = ["txt","pdf","mp4","doc","zip","xml","png","gif","html","rar","xlsx","ppt","pptx"]

# Adding list for Forbidden names and characters for WINDOWS and Linux/Unix and MAC
# window_no_contain = ["<",">",":","\"","/","\\","|","?","*","0","..",""]
# window_no_match = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9","NUL","SOH","STX","ETX","EOT","ENQ","ACK","BEL","BS","TAB","LF","VT","FF","CR","SO","SI","DLE","DC1","DC2","DC3","DC4","NAK","SYN","ETB","CAN","EM","SUB","ESC","FS","GS","RS","US"]
# ubuntu_no_contain = ["/"]
# ubuntu_no_match = ["\0"]
# mac_no_match = [":"]
# mac_no_contain = []
"""Globally available config_file_path"""
config_path = os.path.dirname(os.path.abspath(__file__))+"/usr_config.json"

def create_folder_of_extension(ext,PATH,config_data):
    user_extensions = config_data["USER_OBJECT"]["file"]
    user_defined_extension = user_extensions.get(ext)
    while not user_defined_extension:
        user_defined_extension = get_folder_name_for_ext(ext,config_data)
        if not user_defined_extension:
            print("Can't create folder without name")
        else:
            user_extensions[ext] = user_defined_extension
            update_config(config_path,config_data)  

    try:
        dir_path = os.path.join(PATH,user_defined_extension)
        os.mkdir(dir_path)
        return dir_path
    except Exception as e :
        print(e)
        return False

def move_file_to_folder(file_path,folder_path):
    try:
        shutil.move(file_path,folder_path)
    except Exception as e:
        print(f"Error: can not move file from {file_path} to {folder_path}\n Exception: {e} ")

"""Adding recuresive Feature So that we can clean a directory recursively"""
def clean_dir(PATH,config_data=None):
    if config_data == None:
        config_data = get_config(config_path)
    user_extension_list = config_data["USER_OBJECT"]["file"]
    file_exceptions = config_data["Exception_File_Names"]
    dir_data = os.listdir(PATH)
    dir_list = []
    files_list = []
    
    for item in dir_data:
        if os.path.isfile(os.path.join(PATH,item)):
            files_list.append(item)
        else:
            dir_list.append(item)

    for file in files_list:
        extension = file.split(".")[1] # ask user if array length is more that 2 then which one to choose
        file_path = os.path.join(PATH,file)
        if file in file_exceptions: continue
        if user_extension_list.get(extension) not in dir_list:
            dir_path = create_folder_of_extension(extension,PATH,config_data)
            if not dir_path:
                sys.exit(f"Error: while creating directory, {user_extension_list[extension]} for {file}")      
            if user_extension_list[extension] not in dir_list:
                dir_list.append(user_extension_list[extension])
        else:
            dir_path = os.path.join(PATH,user_extension_list.get(extension))
        
        move_file_to_folder(file_path,dir_path)

def validate_folder_name(name,config_data):
    os_name = platform.system()
    os_data = config_data["OS"][os_name]
    no_contains_list, no_match_list = os_data["no_contains"], os_data["no_match"]
    for item in no_contains_list:
        if item in name:
            return False
    if name in no_match_list:
        return False
    
    return True

def get_config(config_path):
    with open(config_path) as file:
        data = json.load(file)
    return data

def update_config(config_path,data):
    with open(config_path,'w') as file:
        json.dump(data,file,indent=3)

def update_user_config_extension(data):
    user_data = get_config(config_path)
    for prop,val in data.items():
        user_data["USER_OBJECT"]["file"][prop] = val
    update_config(config_path,user_data)

def get_folder_name_for_ext(extension,config_data=None):
    if config_data == None:
        config_data = get_config(config_path)
    
    valid = False
    while not valid:
        value = input(f"Enter folder name for {extension} format (SKIP (N/n)): ").strip()
        # Consider the condition if User wants to have folder name as N or n.
        test_value = value.lower()
        if(test_value == "n" or test_value == ""): break #check if user enter anything else like Enter only etc.
        valid = validate_folder_name(value,config_data)
        if not valid:
            print("Name Entered is not valid in your System, Please try again !")
    if valid:
        return value
    return None

def create_user_config(config_data):
    default_config_list = config_data["DEFAULT_CONFIG_LIST"]
    user_config_data = config_data["USER_OBJECT"]
    user_config_data_file = user_config_data["file"]
    
    user_config_data["run_default"] = False

    want_to_set_default = input("Would like to set Default extensions? YES(y/Y) : SKIP(n/N): ")
    if(want_to_set_default.lower() != "y"):
        update_config(config_path,config_data)
        return 

    for format in default_config_list : 
        value = get_folder_name_for_ext(format,config_data)
        if value :
            user_config_data_file[format] = value
    update_config(config_path,config_data)



if __name__ == "__main__":
    if len(sys.argv)>1:
        PATH = sys.argv[1]
    else:
        sys.exit("ERROR: please provide path argument for clean up")
    
    config_data = get_config(config_path)
    if config_data["USER_OBJECT"]["run_default"]:
        create_user_config(config_data)
    clean_dir(PATH,config_data)
    # pass

