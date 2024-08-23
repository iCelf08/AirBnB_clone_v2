#!/usr/bin/python3
""" A Fabric script that distributes an archive to web servers, using the
    function deploy_archive. The script assumes archives are stored and
    managed in the /data/web_static/releases/ directory on the remote servers. """


from fabric.api import *
from os.path import exists

# Define the hosts (web servers) to which the archive will be deployed
env.hosts = ['35.237.166.125', '54.167.61.201']

def deploy_archive(archive_path):
    """ Distributes an archive to the web servers.
    
    Args:
        archive_path (str): The path to the archive file to be deployed.
        
    Returns:
        bool: True if the deployment was successful, False otherwise.
    """
    if not exists(archive_path):
        return False  # Returns False if the file at archive_path doesn't exist

    # Extract the filename from the path
    archive_filename = archive_path.split('/')[-1]
    
    # Define the target directory and temporary file path
    target_directory = '/data/web_static/releases/{}'.format(archive_filename.split('.')[0])
    temporary_file = "/tmp/{}".format(archive_filename)

    try:
        # Upload the archive to the /tmp/ directory on the remote server
        put(archive_path, temporary_file)
        
        # Create the target directory on the remote server
        run("mkdir -p {}".format(target_directory))
        
        # Extract the archive to the target directory
        run("tar -xzf {} -C {}".format(temporary_file, target_directory))
        
        # Remove the temporary archive file
        run("rm {}".format(temporary_file))
        
        # Move the contents of the extracted archive to the target directory
        run("mv {}/web_static/* {}".format(target_directory, target_directory))
        
        # Remove the now-empty web_static directory
        run("rm -rf {}/web_static".format(target_directory))
        
        # Remove the current symbolic link
        run("rm -rf /data/web_static/current")
        
        # Create a new symbolic link to the new version
        run("ln -s {} /data/web_static/current".format(target_directory))
        
        return True
    except Exception as e:
        # Print the exception if needed for debugging
        print(f"An error occurred: {e}")
        return False
