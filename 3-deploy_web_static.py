#!/usr/bin/python3
""" Fabric script that creates and distributes an archive to web servers
    using the function deploy. The script uses do_pack to generate the
    archive and do_deploy to distribute it. """


from fabric.api import *
from datetime import datetime
from os.path import exists

# Define the remote hosts (web servers) for deployment
env.hosts = ['35.237.166.125', '54.167.61.201']

def create_archive():
    """ Generates a .tgz archive from the contents of the web_static folder.
    
    Returns:
        str: The path to the generated archive if successful, otherwise None.
    """
    local("mkdir -p versions")  # Create the versions directory locally
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_path = "versions/web_static_{}.tgz".format(timestamp)
    command_result = local("tar -cvzf {} web_static".format(archive_path))
    
    if command_result.succeeded:
        return archive_path
    else:
        return None

def distribute_archive(archive_path):
    """ Distributes an archive to the web servers.
    
    Args:
        archive_path (str): The path to the archive file to be deployed.
        
    Returns:
        bool: True if the deployment was successful, False otherwise.
    """
    if not exists(archive_path):
        return False  # Return False if the file at archive_path doesn't exist
    
    archive_filename = archive_path.split('/')[-1]
    release_path = '/data/web_static/releases/{}'.format(archive_filename.split('.')[0])
    temp_path = "/tmp/{}".format(archive_filename)

    try:
        # Upload the archive to the /tmp/ directory on the remote server
        put(archive_path, temp_path)
        
        # Create the target directory on the remote server
        run("mkdir -p {}".format(release_path))
        
        # Extract the archive to the target directory
        run("tar -xzf {} -C {}".format(temp_path, release_path))
        
        # Remove the temporary archive file
        run("rm {}".format(temp_path))
        
        # Move the contents of the extracted archive to the target directory
        run("mv {}/web_static/* {}".format(release_path, release_path))
        
        # Remove the now-empty web_static directory
        run("rm -rf {}/web_static".format(release_path))
        
        # Remove the current symbolic link
        run("rm -rf /data/web_static/current")
        
        # Create a new symbolic link to the new version
        run("ln -s {} /data/web_static/current".format(release_path))
        
        return True
    except Exception as e:
        # Print the exception for debugging purposes
        print(f"An error occurred: {e}")
        return False

def deploy():
    """ Creates and distributes an archive to the web servers.
    
    Returns:
        bool: True if both creating and deploying the archive were successful, False otherwise.
    """
    # Create a new archive and get its path
    archive_path = create_archive()
    
    if not archive_path:
        return False  # Return False if no archive was created
    
    # Distribute the created archive to the web servers
    return distribute_archive(archive_path)
