"""Custom-made Packages installation.
"""
import logging
import sys
import os
import stat
import zipfile
from lib import *
import diomreader
from time import strftime
import shutil

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("cmpack.cmpack")

class Package():
    """Install/rollback/uninstall Packages
    """
    __repoOnline = 'Online_Repo'
    __repoLocal = 'Local_Repo'

    def __init__(self, vendorname, profile, configFile, version=None):
        self.profile = profile
        self.configFile = configFile
        self.version = version
        self.setConfig(vendorname)

    def setConfig(self, vendorname):
        self.config = {}
        self.config['vendorname'] = vendorname
        (self.sysName, nodeName, release, version, self.machine) = os.uname()
        logger.debug("System Information: %s(OS), %s(HOST), %s(Release), %s(ARCH)", self.sysName, nodeName, release, self.machine)
        self.config.update(propsparser.ini(self.configFile, scope=['Root'])['Root'])
        ## load Root data if file found
        if self.config.has_key('root_config_file'):
            self.config['root_config_file'] = os.path.join(os.path.dirname(self.configFile),
                                                        self.config['root_config_file'])
            self.config.update(propsparser.ini(self.config['root_config_file'],
                                                scope=['Root'])['Root'])
            self.config.update(propsparser.ini(self.configFile, scope=['Root'])['Root'])
            self.config['root_config_file'] = os.path.join(os.path.dirname(self.configFile),
                                                self.config['root_config_file'])
        self.config.update(propsparser.ini(self.configFile, scope=[self.profile])[self.profile])
        self.config['profile'] = self.profile
        if self.config.has_key('root_config_file'):
            self.config.update(propsparser.ini(self.config['root_config_file'],
                        scope=[self.config['repo_option']])[self.config['repo_option']])
        else:
            self.config.update(propsparser.ini(self.configFile,
                        scope=[self.config['repo_option']])[self.config['repo_option']])

        ## Load local repo. Online repo is disabled.
        """
        self.config.update(propsparser.ini(self.configFile,
                                           scope=[Package.__repoLocal])[Package.__repoLocal])
        """

    def install(self):
        # Read online and download software
        xml = diomreader.XMLReader(url=self.config['url'], file=self.config['dm_file'],
                        sysName=self.sysName,sysBit=self.machine,vendorName=self.config['vendorname'],
                        packageName=self.config['pkg_name'], version=self.version,
                        realm=self.config['url_realm'],user=self.config['url_user'],
                        passwd=self.config['url_passwd'])

        self.config.update(xml.getSWDownloadDetails())
        if self.config['repo_option'] == Package.__repoLocal:
            download.Download(self.config['url'], self.config['fileName'], self.config['target_loc'],
                              realm=self.config['url_realm'], user=self.config['url_user'],
                              passwd=self.config['url_passwd'])

        if self.config['install_type'] == 'copy':
            Package.cmpack_copy(os.path.join(self.config['target_loc'],
                                self.config['fileName'].rstrip('.zip')),
                                self.config['install_root'],
                               )
        elif self.config['install_type'] == 'overwrite':
            Package.cmpack_overwrite(os.path.join(self.config['target_loc'],
                                     self.config['fileName'].rstrip('.zip')),
                                     self.config['install_root'],
                                    )
        elif self.config['install_type'] == 'symlink':
            Package.cmpack_symlink(os.path.join(self.config['target_loc'],
                                     self.config['fileName'].rstrip('.zip')),
                                     self.config['install_root'],
                                    )


    @staticmethod
    def cmpack_copy(src, dst):
        if os.path.isdir(dst):
            timestamp = strftime("%Y%m%d_%H%M%S")
            logger.info("Existing package found. Taking backup as %s", dst + "." + timestamp)
            os.rename(dst, dst + "." + timestamp)
        logger.info("Copying from %s to %s", src, dst)
        shutil.copytree(src, dst, symlinks=False, ignore=None)

    @staticmethod
    def cmpack_overwrite(src, dst):
        if os.path.isdir(dst):
            timestamp = strftime("%Y%m%d_%H%M%S")
            logger.info("Existing package found. Taking backup as %s", dst + "." + timestamp)
            shutil.copytree(dst, dst + "." + timestamp, symlinks=False, ignore=None)
            cmd = ( "cp -R " + src + '/* ' + dst)
        else:
            cmd = ( "cp -R " + src + ' ' + dst)
        logger.info("Copying from %s to %s", src, dst)
        (ret_code, output) = shell.Shell.runCmd(cmd)

    @staticmethod
    def cmpack_symlink(src, dst):
        logger.info("Copying from %s to %s", src, dst)
        cmd = ( "cp -R " + src + ' ' + os.path.join(os.path.dirname(dst), os.path.basename(src)))
        (ret_code, output) = shell.Shell.runCmd(cmd)
        if os.path.islink(dst):
            logger.info("Symlink found for %s. Removing it.", dst)
            cmd = ( "unlink " + dst)
            (ret_code, output) = shell.Shell.runCmd(cmd)
        cmd = ( "ln -s " + os.path.join(os.path.dirname(dst), os.path.basename(src)) + \
                        " " + dst)
        logger.info("Creating symlink for %s -> %s", dst,
                    os.path.join(os.path.dirname(dst), os.path.basename(src)))
        (ret_code, output) = shell.Shell.runCmd(cmd)
