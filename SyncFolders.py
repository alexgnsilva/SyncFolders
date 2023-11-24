"""
SyncFolders - A module for syncrhonizing two folders, source and replica.
 Contents of source are copied to replica, and contents of replica that do not exist on source are deleted.
 Actions are stored on log and synchronization is repetead on time interval.
Usage: SyncFolders [dir_source] [dir_replica] [dir_log] [interval]
@author: Alexandre Neves da Silva, November 2023 
"""

import sys
import os
import time
import hashlib

class SyncFolders:
    def __init__(self, dir_source, dir_replica, dir_log, time_interval):
        self._dir_source = dir_source
        self._dir_replica = dir_replica
        self._dir_log = dir_log
        self._time_interval = int(time_interval)

    # Validate all paths to verify their existence
    def _test_paths(self):
        if ( os.path.isdir(self._dir_source) == False ):
            print(" Dir Source \"" + self._dir_source + "\" does not exist.");
            return False
        if ( os.path.isdir(self._dir_replica) == False ):
            print(" Dir Replica \"" + self._dir_replica + "\" does not exist.");
            return False
        if ( os.path.isdir(self._dir_log) == False ):
            print(" Dir Log \"" + self._dir_log + "\" does not exist.");
            return False
        return True

    # Copy a file to another byte by byte
    def _copy_file(self, filein,fileout):
        fin = open(filein, "rb");
        fout = open(fileout, "wb");
        byte = fin.read(1)
        while byte:
            fout.write(byte)
            byte = fin.read(1)

    # Compute the a folder and its contents
    def _remove_directory(self, path):
        for entry in os.scandir(path):
            if entry.is_dir():
                self._remove_directory(entry)
            else:
                os.remove(entry)
        os.rmdir(path)

    # Compute the checksum of a file contents
    def _file_checksum(self, filecheck):
        return hashlib.md5(open(filecheck,"rb").read()).hexdigest()

    # Write log line information to console and file
    def _log(self, line):
        print(line)
        self._flog.write(line + "\n")

    # Remove the folders and files that exist on replica and not on source
    def _sync_replica(self,dir_in,dir_out):
        self._log(" Remove Replica [" + dir_out + "] contents not existent on Source [" + dir_in + "]")
        for file_path in os.listdir(dir_out):
            if os.path.isfile(os.path.join(dir_out, file_path)):
                file_in = dir_in + "\\" + file_path
                file_out = dir_out + "\\" + file_path
                if ( os.path.isfile(file_in) == False ):
                    self._log("  ACTION: File Deleted: " + file_out )
                    os.remove(file_out);
            else: 
                sub_dir_in = dir_in + "\\" + file_path
                sub_dir_out = dir_out + "\\" + file_path
                if ( os.path.isdir(sub_dir_in) == False ):
                    self._log("  ACTION: Folder Deleted: " + sub_dir_out )
                    self._remove_directory( sub_dir_out )
                else:
                    self._sync_replica( sub_dir_in, sub_dir_out )

    # Create the folders and copy the new/modified files from source to replica
    def _sync_source(self,dir_in,dir_out):
        self._log(" Copy Source [" + dir_in + "] contents to Replica [" + dir_out + "]" )
        for file_path in os.listdir(dir_in):
            if os.path.isfile(os.path.join(dir_in, file_path)):
                file_in = dir_in + "\\" + file_path
                file_out = dir_out + "\\" + file_path
                if ( os.path.isfile(file_out) == False ):
                    self._log("  ACTION: File Created: " + file_out )
                    self._copy_file( file_in, file_out )
                elif self._file_checksum( file_in ) != self._file_checksum( file_out ):
                    self._log("  ACTION: File Overwritten: " + file_out )
                    self._copy_file( file_in, file_out )
            else: 
                sub_dir_in = dir_in + "\\" + file_path
                sub_dir_out = dir_out + "\\" + file_path
                if ( os.path.isdir(sub_dir_out) == False ):
                    self._log("  ACTION: Folder Created: " + sub_dir_out )
                    os.mkdir( sub_dir_out )
                self._sync_source( sub_dir_in, sub_dir_out )

    # Executes the synchronization
    def execute(self):
        if ( self._test_paths() == False ):
            return False
        while (True):
            self._flog = open(self._dir_log + "\\SyncFolders.log", "a")
            t = time.localtime()
            current_time = time.strftime("%m/%d/%Y, %H:%M:%S", t)
            self._log("SYNC FOLDERS:  [" + self._dir_source + "] -> [" + self._dir_replica + "] - " + current_time)
            self._sync_replica(self._dir_source,self._dir_replica)
            self._sync_source(self._dir_source,self._dir_replica)
            self._log("Sleep: " + str(self._time_interval) + " seconds..." )
            self._log(" " )
            self._flog.close()
            time.sleep( self._time_interval )
        return True

if __name__ == "__main__":
    if ( len(sys.argv) < 4 ):
        print("Syntax: SyncFolders [dir_source] [dir_replica] [dir_log] [interval]")
        sys.exit(0)
    SyncFolders(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]).execute()

