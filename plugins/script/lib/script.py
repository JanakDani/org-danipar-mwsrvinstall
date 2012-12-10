"""IBM Middleware product installation. Supports for Installation manager, Packaging utility and other products.
"""
import logging
import sys
import os
import stat
#import configparser
import zipfile
from lib import *
import diomreader

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("script.script")

class InstallationManager():
    """Install/Remove Installation Manager.
    """
    def __init__(self):
        pass

    @staticmethod
    def install(exec_script, im_install_root, imdl_install_root, imshared_root, repository,
                offering_id, offering_version=None, offering_features=None):
        """Installs installation manager
        """
        logger.debug("Setting up imcl cmd")

        offering_str = offering_id
        if offering_version != None:
            offering_str += '_' + offering_version
        if offering_features != None:
            offering_str += ',' + offering_features

        cmd =   ( exec_script +
                " install " + offering_id +
                " -repositories " + repository +
                " -installationDirectory " + os.path.join(im_install_root, 'eclipse') +
                " -dataLocation " + imdl_install_root +
                " -sharedResourcesDirectory " + imshared_root +
                " -acceptLicense"
                )
        (ret_code, output) = shell.Shell.runCmd(cmd)

    @staticmethod
    def uninstall(imdl_install_root):
        """Uninstalls installation manager
        """
        cmd = ( os.path.join(imdl_install_root, 'uninstall', 'uninstallc') +
                " -silent" )
        (ret_code, output) = shell.Shell.runCmd(cmd)

class Package():
    """Install/rollback/uninstall Packages
    """
    __repoOnline = 'Online_Repo'
    __repoLocal = 'Local_Repo'

    def __init__(self, vendorname, oprofile, configFile, version=None):
        self.oprofile = oprofile
        self.configFile = configFile
        self.version = version
        self.setConfig(vendorname)

    def setConfig(self, vendorname):
        self.config = {}
        self.config['vendorname'] = vendorname
        (self.sysName, nodeName, release, version, self.machine) = os.uname()
        logger.debug("System Information: %s(OS), %s(HOST), %s(Release), %s(ARCH)", self.sysName, nodeName, release, self.machine)
        self.config.update(propsparser.ini(self.configFile, scope=['Root'])['Root'])
        self.config.update(propsparser.ini(self.configFile, scope=[self.oprofile])[self.oprofile])

        ## Load local repo. Online repo is disabled.
        self.config.update(propsparser.ini(self.configFile,
                                           scope=[Package.__repoLocal])[Package.__repoLocal])

    def install(self):
        # Read online and download software
        xml = diomreader.XMLReader(url=self.config['url'], file=self.config['dm_file'],
                                sysName=self.sysName,sysBit=self.machine,vendorName=self.config['vendorname'],
                                packageName=self.config['packagename'], version=self.version)
        #print self.config
        self.config.update(xml.getSWDownloadDetails())

        if self.config['repo_option'] == Package.__repoLocal:
            download.Download(self.config['url'], self.config['fileName'], self.config['target_loc'])
        print self.config

        Package.script_install(self.config['install_type'],
                               self.config['install_root'],
                               os.path.join(self.config['target_loc'],
                                            self.config['fileName'].rstrip('.zip')),
                               self.config['type_name'],
                        )

    def uninstall(self):
        print "Uninstall does not work at this point. Please uninstall it manually"

    def rollback(self):
        pass

    @staticmethod
    def script_install(install_type, install_root, repository, type_name):
        logger.debug("Setting up cmd")
        if install_type == 'alias':
            if os.path.isdir(os.path.join(install_root, type_name)):
                cmd = ( "rm -rf " + os.path.join(install_root, type_name))
                (ret_code, output) = shell.Shell.runCmd(cmd)
            cmd =   ( "cp -R " + repository + ' ' + os.path.join(install_root, type_name))
            (ret_code, output) = shell.Shell.runCmd(cmd)
        elif install_type == 'link':
            cmd = ( "cp -R " + repository + ' ' + install_root)
            (ret_code, output) = shell.Shell.runCmd(cmd)
            if os.path.islink(os.path.join(install_root, type_name)):
                cmd = ( "unlink " + os.path.join(install_root, type_name))
                (ret_code, output) = shell.Shell.runCmd(cmd)
            cmd = ( "ln -s " + os.path.join(install_root,
                                            os.path.basename(repository)) + \
                   " " + os.path.join(install_root, type_name))
            (ret_code, output) = shell.Shell.runCmd(cmd)

    @staticmethod
    def script_rollback(exec_script, install_root,
                offering_id, offering_version=None, offering_features=None):
        logger.debug("Setting up cmd")
        offering_str = offering_id
        if offering_version != None:
            offering_str += '_' + offering_version
        if offering_features != None:
            offering_str += ',' + offering_features
        cmd =   ( exec_script +
                " rollback " + offering_str +
                #" -repositories " + repository +
                " -installationDirectory " + install_root +
                #" -sharedResourcesDirectory " + imshared_root +
                " -acceptLicense"
                )
        (ret_code, output) = shell.Shell.runCmd(cmd)

    @staticmethod
    def script_uninstall(exec_script, install_root, offering_id, offering_version=None, offering_features=None):
        offering_str = offering_id
        if offering_version != None:
            offering_str += '_' + offering_version
        if offering_features != None:
            offering_str += ',' + offering_features
        cmd =   (exec_script +
                " uninstall " + offering_str +
                " -installationDirectory " + install_root
                )
        (ret_code, output) = shell.Shell.runCmd(cmd)

def unzip(file, target_loc):
    if not os.path.isdir(file.rstrip('.zip')):
        if zipfile.is_zipfile(file):
            logger.info("Extracting software %s. please wait...", file)
            zip = zip = zipfile.ZipFile(file)
            zip.extractall(path=target_loc)
            logger.info("Software extracted to %s", target_loc)
            for dirpath,dirs,fileNames in os.walk(os.path.join(target_loc, file.rstrip('.zip'))):
                for fileName in fileNames:
                    file = os.path.join(dirpath, fileName)
                    os.chmod(file, stat.S_IRWXU)
    else:
        logger.debug("Software %s already found. Skipping unzip ...", file)
