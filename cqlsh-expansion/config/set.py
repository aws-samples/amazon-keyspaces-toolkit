#!/usr/bin/env python

import shutil, getpass, os, site

def expansion_config():
    user = getpass.getuser()
    user_dir = os.path.expanduser('~'+user)
    installation_dir = site.USER_SITE + '/' + 'config/'
    config_dir = os.path.join( user_dir, '.cassandra')
    if not os.path.exists(config_dir):
            print('Creating .cassandra directory in home path and copying cert and cqlshrc file')
            os.mkdir(config_dir)
            shutil.move( installation_dir + 'sf-class2-root.crt' , config_dir)
            shutil.move( installation_dir + 'cqlshrc' , config_dir)
    else:
            print('.cassandra directory already exists validate & copy if cert and cqlshrc files ')
            if not os.path.exists(os.path.join(config_dir, 'sf-class2-root.crt')):
                print('Moving cert file to .cassandra directory in User home directory ')
                shutil.move( installation_dir + 'sf-class2-root.crt', config_dir)
            if not os.path.exists(os.path.join(config_dir, 'cqlshrc')):
                print('Moving cqlshrc file to .cassandra directory in User home directory')
                shutil.move( installation_dir + 'cqlshrc' , config_dir)
    print('Post installation config for expansion utility completed')
#
