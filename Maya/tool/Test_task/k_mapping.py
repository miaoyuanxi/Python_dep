# -*- coding: utf-8 -*-
import time
import os
import sys
import subprocess

class k_mapping():
    def __init__(self,mount):
        self.is_win   = True
        self.is_linux = False
        print ('go mapping')
        self.clean_network()
        self.mapping_network(mount)

        
    def clean_network(self):

        for j in range(3):
            if os.system("net use * /delete /y"):
                print ("clean mapping network failed.")
                time.sleep(2)
                print ("Wait 2 seconds...")
            else:
                print ("clean mapping network successfully.")
                break
        sys.stdout.flush()


    '''
    def mapping_network(self,mount):
        for i in mount:

            path = mount[i].replace("/", "\\")
            if os.path.exists(path):
                if path.startswith("\\"):
                    for j in range(3):
                        if os.system("net use %s %s" % (i, path)):
                            print ("can not mapping %s to %s" % (i, path))
                            time.sleep(5)
                            print ("Wait 5 seconds...")
                        else:
                            print ("Mapping %s to %s" % (i, path))
                            break

            else:
                print ('[warn]The path is not exist:%s' % path)

            sys.stdout.flush()
    '''

    def run_command(self, command):

        if self.is_win:
            return subprocess.call(command)
        if self.is_linux:
            return subprocess.call(command, shell=1)

    def mapping_network(self,mount):
        for i in mount:
            path = mount[i].replace("/", "\\")
            if path.startswith("\\"):
                if self.run_command("net use %s %s" % (i, path)):
                    print ("can not mapping %s to %s" % (i, path))
                else:
                    print ("Mapping %s to %s" % (i, path))
            else:
                self.create_virtua_drive(i, path)

                sys.stdout.flush()

        self.run_command("net use")
        self.run_command("subst")

    def create_virtua_drive(self, virtual_drive, path, max=60):
        if max == 0:
            print("can not create virutal drive: %s => %s" % (virtual_drive,path))
            sys.stdout.flush()
            return 0
        else:
            self.run_command("subst %s %s" % (virtual_drive, path))
            sys.stdout.flush()
            if os.path.exists(virtual_drive + "/"):
                print("create virutal drive: %s => %s" % (virtual_drive,path))
                print(virtual_drive + "/" + " is exists")
                sys.stdout.flush()
            else:
                time.sleep(1)
                print
                "wait 1 second and try subst again"
                sys.stdout.flush()
                self.create_virtua_drive(virtual_drive, path, max - 1)