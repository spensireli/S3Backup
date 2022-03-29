import os
import sys

class Backups():

    def file_size(self, directory, file_name):
        full_path = directory + '/' + file_name
        file_size = os.path.getsize(full_path)
        return file_size