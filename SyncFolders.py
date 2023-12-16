"""
SyncFolders - A module for syncrhonizing two folders, source and replica.
 Contents of source are copied to replica, and contents of replica that do not exist on source are deleted.
 Actions are stored on log and synchronization is repetead on time interval.
Usage: SyncFolders -s source -r replica -l logdir -t timeinterval
@author: Alexandre Neves da Silva, December 2023 
"""

import sys
import os
import time
import hashlib
import logging
import argparse
import shutil
import filecmp

class SyncFolders:
    def __init__(self, dir_source, dir_replica, dir_log, time_interval):
        self._dir_source = dir_source
        self._dir_replica = dir_replica
        self._dir_log = dir_log
        self._time_interval = int(time_interval)

    # Validate all paths to verify their existence
    def _test_paths(self):
        if ( os.path.isdir(self._dir_source) == False ):
            print(" Source folder \"" + self._dir_source + "\" does not exist.");
            return False
        if ( os.path.isdir(self._dir_replica) == False ):
            print(" Replica folder \"" + self._dir_replica + "\" does not exist.");
            return False
        if ( self._dir_source == self._dir_replica ):
            print("Source and Replica folder are the same.");
            return False
        if ( os.path.isdir(self._dir_log) == False ):
            print(" Dir Log \"" + self._dir_log + "\" does not exist.");
            return False
        return True

    # Copy a file to another
    def _copy_file(self, filein,fileout):
        try:
            shutil.copy(filein, fileout)
        except shutil.SameFileError:
            logging.error("   Error on copy: In and out file [" + filen + "] are the same")
        except PermissionError:
            logging.error("   Permission error on copying file: " + filein )
        except:
            logging.error("   Error copying file:" + filein )        

    # Remove the folders and files that exist on replica and not on source
    def _sync_replica(self,dir_in,dir_out):
        logging.info(" Removing Replica [" + dir_out + "] contents not existent on Source [" + dir_in + "]")
        try:
            listdir = os.listdir(dir_out)
        except Exception as e:
            logging.error(f'Failed to list folder: {e}')
            return        
        for file_path in listdir:
            if os.path.isfile(os.path.join(dir_out, file_path)):
                file_in = dir_in + "\\" + file_path
                file_out = dir_out + "\\" + file_path
                if ( os.path.isfile(file_in) == False ):
                    logging.info("  ACTION: Deleting file: " + file_out )
                    try:
                        os.remove(file_out);
                    except Exception as e:
                        logging.error(f'Failed to delete file: {e}')
            else: 
                sub_dir_in = dir_in + "\\" + file_path
                sub_dir_out = dir_out + "\\" + file_path
                if ( os.path.isdir(sub_dir_in) == False ):
                    logging.info("  ACTION: Deleting folder: " + sub_dir_out )
                    try:
                        shutil.rmtree( sub_dir_out )
                    except Exception as e:
                        logging.error(f'Failed to delete folder: {e}')
                else:
                    self._sync_replica( sub_dir_in, sub_dir_out )

    # Create the folders and copy the new/modified files from source to replica
    def _sync_source(self,dir_in,dir_out):
        logging.info(" Copying Source [" + dir_in + "] contents to Replica [" + dir_out + "]" )
        try:
            listdir = os.listdir(dir_in)
        except Exception as e:
            logging.error(f'Failed to list folder: {e}')
            return
        for file_path in listdir:
            if os.path.isfile(os.path.join(dir_in, file_path)):
                file_in = dir_in + "\\" + file_path
                file_out = dir_out + "\\" + file_path
                if ( os.path.isfile(file_out) == False ):
                    logging.info("  ACTION: Copying file: " + file_out )
                    self._copy_file( file_in, file_out )
                elif ( filecmp.cmp( file_in, file_out ) == False ):
                    logging.info("  ACTION: Overwriting file: " + file_out )
                    self._copy_file( file_in, file_out )
            else: 
                sub_dir_in = dir_in + "\\" + file_path
                sub_dir_out = dir_out + "\\" + file_path
                if ( os.path.isdir(sub_dir_out) == False ):
                    logging.info("  ACTION: Creating folder: " + sub_dir_out )
                    try:
                        os.mkdir( sub_dir_out )
                    except Exception as e:
                        logging.error(f'Failed to create folder: {e}')
                        continue
                self._sync_source( sub_dir_in, sub_dir_out )

    # Executes the synchronization
    def execute(self):
        if ( self._test_paths() == False ):
            return False
        while (True):
            logfile = self._dir_log + "\\SyncFolders.log"
            logging.basicConfig(
                level=logging.INFO,
                handlers=[
                    logging.FileHandler(logfile),
                    logging.StreamHandler()
                ]
            )
            t = time.localtime()
            current_time = time.strftime("%m/%d/%Y, %H:%M:%S", t)
            logging.info("SYNC FOLDERS:  [" + self._dir_source + "] -> [" + self._dir_replica + "] - " + current_time)
            self._sync_replica(self._dir_source,self._dir_replica)
            self._sync_source(self._dir_source,self._dir_replica)
            logging.info("Sleep: " + str(self._time_interval) + " seconds..." )
            logging.info(" " )
            time.sleep( self._time_interval )
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', type=str, help="Source folder", required=True)
    parser.add_argument('-r', '--replica', type=str, help="Replica folder", required=True)
    parser.add_argument('-l', '--logfolder', type=str, help="Log folder", required=True)
    parser.add_argument('-t', '--timelapse', type=int, help="Time interval", required=True)
    args = parser.parse_args()
    SyncFolders(args.source,args.replica,args.logfolder,args.timelapse).execute()

