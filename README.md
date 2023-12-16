# SyncFolders
A Python application for syncrhonizing two folders

This application, running on command line, allows make the syncrhonization of two folders, by giving as parameters:
SyncFolders -s source -r replica -l logdir -t timeinterval

source: the source folder to be synchronized

replica: the target folder that should replicate the contents of the source folder

logdir: the folder where a log file will be placed with the results of the synchronization

timeinterval: the time interval between syncrhonizations

When the application is executed, it does the synchornization every [interval] seconds, on a endless loop.
It first verifies if the replica folder contains files and sub-folders that do not exist on source, and deletes them
Then it copies all non-existent files and sub-folders from source to replica. Regarding existant ones on both sides,
it verifies if each file is equal, otherwise it overwrites it.


