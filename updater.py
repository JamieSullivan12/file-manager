import os


class Updater:
    
    def get_version(self, version):
        """
        Retrieves the value associated with the given version.

        Parameters:
            version (str): The version to retrieve.

        Returns:
            str or None: The value associated with the given version, or None if the version is not found.
        """
        if version in self.versions:
            return self.versions[version]
        else: return None

    def get_version(self, major, minor, minor_minor):
        """
        Returns the version corresponding to the given major, minor, and minor_minor values.

        Parameters:
            major (int): The major version number.
            minor (int): The minor version number.
            minor_minor (int): The minor minor version number.

        Returns:
            str or None: The version corresponding to the given parameters, or None if no matching version is found.
        """

        if self.combine_semantic_versioning(major, minor, minor_minor) in self.versions:
            return self.versions[self.combine_semantic_versioning(major, minor, minor_minor)]
        else: return None

    def get_current_version_key(self):
        return list(self.versions.keys())[-1]

    def get_current_version(self):
        return self.versions[self.get_current_version_key()]
    
    def __init__(self):
        self.versions = {
            "1.0.0":{"major":1,"minor":0,"minor_minor":0,"function":None},
            "1.0.1":{"major":1,"minor":0,"minor_minor":1,"function":self.update1_0_0to1_0_1},
            "1.0.2":{"major":1,"minor":0,"minor_minor":2,"function":self.update1_0_1to1_0_2},
            "1.0.3":{"major":1,"minor":0,"minor_minor":3,"function":self.update1_0_2to1_0_3},
        }
        self.db_object = None
        
    def extract_semantic_versioning(self,semantic_versioning):
        return list(map(int, semantic_versioning.split(".")))
    
    def combine_semantic_versioning(self,major, minor, minor_minor):
        return f"{major}.{minor}.{minor_minor}"


    def update_seperate_version(self, version_old_major, version_old_minor, version_old_patch, update_database=False):
        self.update(self.combine_semantic_versioning(version_old_major, version_old_minor, version_old_patch), update_database=update_database)

    def update(self, version_old, update_database=False):
        index = list(self.versions.keys()).index(version_old)
        index = index + 1

        while index < len(self.versions):
            version_key = list(self.versions.keys())[index]
            version_value = self.versions[version_key]
            old_major, old_minor, old_minor_minor = self.extract_semantic_versioning(version_key)
            
            if old_major != None and old_minor != None and old_minor_minor != None:    
                version_value["function"](version_key, old_major, old_minor, old_minor_minor, update_database=update_database) if not version_value["function"] == None else None

            index += 1

    def change_version_file(self, new_version_to_write):
        with open(self.version_file_path, "w") as file:
            file.write(new_version_to_write)
        file.close()
    

    def link_database_object(self, db_object):
        self.db_object = db_object

    def change_version_database(self, new_version_to_write):
        self.db_object.update_version(self.versions[new_version_to_write]["major"],self.versions[new_version_to_write]["minor"],self.versions[new_version_to_write]["minor_minor"])

    def open_version_file(self, directory, version_to_write = None):
        """
        Opens the version file located in the specified directory and returns its contents.

        Parameters:
            directory (str): The directory where the version file is located.
            version_to_write (str, optional): The version to write in the file. If not provided, the current version key will be used.

        Returns:
            str: The contents of the version file.

        """
        # check if the version file is present, make it otherwise
        if version_to_write == None: version_to_write = self.self.get_current_version_key()
        self.version_file_path = os.path.join(directory, "version.txt")
        if not os.path.exists(self.version_file_path):
            with open(self.version_file_path, "w") as file:
                file.write(version_to_write)
            file.close()
        return open(self.version_file_path, "r").read().strip()




    def update1_0_0to1_0_1(self, version_number, major, minor, minor_minor,update_database):
        self.change_version_file(version_number)
        if update_database:self.change_version_database(version_number)
    
    def update1_0_1to1_0_2(self, version_number, major, minor, minor_minor,update_database):
        self.change_version_file(version_number)
        if update_database:self.change_version_database(version_number)
    
    def update1_0_2to1_0_3(self, version_number, major, minor, minor_minor,update_database):
        self.change_version_file(version_number)
        if update_database:
            self.db_object.add_column("past_papers","course","text")
            self.change_version_database(version_number)
