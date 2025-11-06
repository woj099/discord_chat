import os
import csv
import json
import time


class File:
    def __init__(self, root_folder="fm", info_folder = "info", info_file_name="data_files", debug = False): # File Managment 
        self.root_folder = root_folder # inicjacja folderu root
        self.info_folder = info_folder # inicjacja folderu info
        self.info_file_name = info_file_name
        self.d = debug
        try:
            os.makedirs(f"{self.root_folder}/{self.info_folder}", exist_ok=True) # tworzenie folderu root i root/info
        except:
            print(f"Error in creating root and root/info folder: {root_folder}/{info_folder}") # wypis bledu
        print(f"root folder '{self.root_folder}' created") # info o udaniu sie
        self.index = os.path.join(self.info_folder, f"{self.info_file_name}.csv") # inicjalizacja folderu / pliku index

        if os.path.exists(self.index):
            print(f"index path created succesfuly")
            with open(self.index, "r") as f:
                content = f.read()
                print(content)


    def append_index(self, data):
        if type(data) != dict:
            pass
        else:
            try:
                info = self.load(f"{self.info_folder}/{self.info_file_name}", "csv")
                # print(info.split("\n")[:-1]) # for debug
                length = len(info.split("\n")[:-1]) # for future logic
                # print(length) # for debug
                info = info.split("\n")
                for item in info:
                    item = item.split(",")
                    if data["name"] == item[0] and data["format"] == item[1]:
                        if self.d:
                            print(f"{data["name"]}.{data["format"]} already exists")
                        return 
                    # need to implement modify date logic. for this i would need an index of the info file line which i have and then modify only that column

            except:
                print("couldn't read info file [normal for first run]")
        with open(f"{self.root_folder}/{self.index}", "a") as f:
            f.write(f"{data["name"]},{data["format"]},{data["filepath"]},{data["created"]},{data["modified"]}\n")#changeeeeeeeeeeee
                


    def save(self, data, name=None, format="txt", mode="w", create_dir=False):
        if name is None:
            name = str(time.time())
        filename = f"{name}.{format}"
        filepath = os.path.join(self.root_folder, filename)
        if create_dir:
            filepathtrue = filepath.split("/")[:-1]
            filepathtrue = "/".join(filepathtrue)
            os.makedirs(filepathtrue, exist_ok=True)
        # Handle JSON format
        if format.lower() == "json":
            if mode == "a":
                raise ValueError("Append mode not supported for JSON files")
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)  # Serialize Python objects to JSON
        else:
            with open(filepath, mode) as f:
                f.write(str(data))
        
        # Update index file
        now = str(time.time())
        data = {"name": name, "format": format, "filepath": filepath, "created": now, "modified": now}
        self.append_index(data)

        
        return filepath

    def load(self, path, format=None):
        """
            Path includes both path to file and name, it can also include format.
        """
        try:
            if format:
                filepath = os.path.join(self.root_folder, f"{path}.{format}")
            else:
                filepath = path
                format = filepath.split(".")[-1] # here can be an error !!!
            # Handle JSON format
            if format.lower() == "json":
                with open(filepath, "r") as f:
                    return json.load(f)  # Deserialize JSON to Python objects
            else:
                with open(filepath, "r") as f:
                    return f.read()
        except:
            print(f"wrong path or format for '{path}' and '{format}'")
    
    def every_file(self, data=2):
        try:
            info = self.load("info/data_files", "csv") #add dynamic change
            # print(info.split("\n")[:-1]) # for debug
            length = len(info.split("\n")[:-1]) # for future logic
            # print(length) # for debug
            info = info.split("\n")[:-1]
            output = list()
            for item in info:
                item = item.split(",")
                output.append(item[data])
                if self.d:
                    print(f"{data[data]} added")
            return output 

        except:
            print("couldn't read info file for every_file [normal for first run]")
 
    # def each_full_file_name(self):
    #     xy = self.load(self.folder, "csv")
    #     xy = xy.split("\n")
    #     index = 0
    #     file_name = []
    #     for text in xy:
    #         text = text.split(",")
    #         file_name.append(text[0])
    #     file_name = [name for name in file_name if name != ""]
    #     file_name = set(file_name)
    #     return file_name
    
    # def contains(self, text, elements):
    #     text = str(text)
    #     if type(elements) == list:
    #         for element in elements:
    #             if text.find(str(element)) != -1:
    #                 continue
    #             else:
    #                 return False
    #     else:
    #         if text.find(elements) != -1:
    #             return True
    #         else:
    #             return False
    #     return True
            
            


# Test JSON functionality
if __name__ == "__main__":
    # f_manager = File("data_files")
    
    # data_dict = {"name": "Alice", "age": 30, "pets": ["dog", "cat"]}
    # f_manager.save(data_dict, "user_data/woman/frfr/long/name/path/Alice", "json", create_dir=True)
    
    # data_list = [1, 2, 3, 4, 5]
    # f_manager.save(data_list, "numbers_game/list_1", "json", create_dir=True)
    
    # loaded_dict = f_manager.load("user_data/woman/frfr/long/name/path/Alice", "json")
    # loaded_list = f_manager.load("numbers_game/list_1", "json")
    
    # print("Loaded dictionary:", type(loaded_dict), loaded_dict)
    # print("Loaded list:", type(loaded_list), loaded_list)
    # print()
    # print(f_manager.every_file())
    # files = f_manager.every_file()
    # for i in files:
    #     print(f_manager.load(i))
    fm = File()
    fm.save({"key": "value"}, "config", "json")
