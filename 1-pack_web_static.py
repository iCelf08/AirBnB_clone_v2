#!/usr/bin/python3
""" This module contains the function create_archive that generates a .tgz archive
  from the contents of the web_static folder (fabric script) """


from fabric.api import *
from datetime import datetime


def create_archive():
    """ Fabric script that generates a .tgz archive from the contents of the
    web_static folder """
    # Create the versions directory if it does not exist
    local("sudo mkdir -p versions")
    
    # Generate a timestamped filename for the archive
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_path = "versions/web_static_{}.tgz".format(timestamp)
    
    # Create the tarball archive from the web_static folder
    command_result = local("sudo tar -cvzf {} web_static".format(archive_path))
    
    # Check if the command was successful and return the archive path or None
    if command_result.succeeded:
        return archive_path
    else:
        return None