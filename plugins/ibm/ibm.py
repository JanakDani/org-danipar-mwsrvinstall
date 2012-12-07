"""IBM Middleware product installation. Supports for Installation manager, Packaging utility and other products.
"""
import logging
import sys
import os
import stat
#import configparser
import zipfile
from lib import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("ibm.ibm")

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
    For Packaging utility, copy or delete packages
    """
    __oprofileIM = 'InstallationManager'
    __repoOnline = 'Online_Repo'
    __repoLocal = 'Local_Repo'
    __packageNameIM = 'IBM Installation Manager'
    __packageNamePU = 'IBM Packaging Utility'

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

        ## Load IM if Package is not IM
        if self.config['packagename'] != Package.__packageNameIM:
            self.config.update(propsparser.ini(self.configFile,
                                scope=[Package.__oprofileIM])[Package.__oprofileIM])
            self.config.update(propsparser.ini(self.configFile, scope=[self.oprofile])[self.oprofile])
        self.config['offering_profile'] = self.oprofile
        self.config['imcl'] = os.path.join(self.config['im_install_root'],'eclipse','tools','imcl')

        ## Load local repo if package is IM or PU
        if self.config['packagename'] == Package.__packageNameIM or \
        self.config['packagename'] == Package.__packageNamePU:
                self.config.update(propsparser.ini(self.configFile,
                                    scope=[Package.__repoLocal])[Package.__repoLocal])
        else:
            self.config.update(propsparser.ini(self.configFile,
                                scope=[self.config['repo_option']])[self.config['repo_option']])

    def install(self):
        # Read online and download software
        xml = urlutils.XMLReader(url=self.config['url'], file=self.config['dm_file'],
                                sysName=self.sysName,sysBit=self.machine,vendorName=self.config['vendorname'],
                                packageName=self.config['packagename'], version=self.version)
        print self.config
        self.config.update(xml.getSWDownloadDetails())

        if self.config['packagename'] != Package.__packageNameIM and \
        not os.path.isdir(self.config['im_install_root']):
            raise Exception('Installation Manager not found installed')

        if self.config['repo_option'] == Package.__repoLocal:
            urlutils.Download(self.config['url'], self.config['fileName'], self.config['target_loc'])

        if self.config['packagename'] == Package.__packageNameIM:
            InstallationManager.install(os.path.join(self.config['target_loc'], 'tools', 'imcl'),
                        self.config['im_install_root'], self.config['imdl_install_root'],
                        self.config['imshared_root'], self.config['target_loc'],
                        self.config['offering_id'], self.config['offering_version']
                        )
        elif self.config['packagename'] == Package.__packageNamePU:
            Package.imcl_install(self.config['imcl'], self.config['install_root'], self.config['imshared_root'],
                        os.path.join(self.config['target_loc'], self.config['fileName'].rstrip('.zip')),
                        self.config['offering_id'], self.config['offering_version']
                        )
        else:
            if self.config['repo_option'] == Package.__repoLocal:
                Package.imcl_install(self.config['imcl'], self.config['install_root'], self.config['imshared_root'],
                        os.path.join(self.config['target_loc'], self.config['fileName'].rstrip('.zip')),
                        self.config['offering_id'], self.config['offering_version'], self.config['offering_features']
                        )
            elif self.config['repo_option'] == Package.__repoOnline:
                Package.imcl_install(self.config['imcl'], self.config['install_root'], self.config['imshared_root'],
                        os.path.join(self.config['target_loc']),
                        self.config['offering_id'], self.config['offering_version'], self.config['offering_features']
                        )

    def uninstall(self):
        if self.config['packagename'] == Package.__packageNameIM:
            InstallationManager.uninstall(self.config['imdl_install_root'])
        else:
            cmd =   (self.config['imcl'] +
                    " listInstalledPackages " +
                    " -long"
                    )
            (ret_code, output) = shell.Shell.runCmd(cmd)
            for line in output.split("\n"):
                if line == '': continue
                (installed_loc,packageid_ver,displayName,displayVersion) = line.split(" : ")
                if installed_loc == self.config['install_root']:
                    self.config['offering_id'], self.config['offering_version'] = packageid_ver.split('_',1)

            Package.imcl_uninstall(self.config['imcl'], self.config['install_root'],
                    self.config['offering_id'], self.config['offering_version']
                    )

    def rollback(self):
        ##Get offering version to rollback to
        if self.version != None:
            if self.config['repo_option'] == Package.__repoLocal:
                xml = urlutils.XMLReader(url=self.config['url'], file=self.config['dm_file'],
                                sysName=self.sysName,sysBit=self.machine,vendorName=self.config['vendorname'],
                                packageName=self.config['packagename'], version=self.version)
                self.config.update(xml.getSWDownloadDetails())
            elif self.config['repo_option'] == Package.__repoOnline:
                for line in self.imcl_getAvailablePackages(self.config['target_loc']).split("\n"):
                    if line == '': continue
                    (repo,packageid_ver,displayName,displayVersion) = line.split(" : ")
                    if displayVersion == self.version and str(displayName) == self.config['packagename']:
                        self.config['offering_id'], self.config['offering_version'] = packageid_ver.split('_',1)
        else:
            cmd =   (self.config['imcl'] +
                    " listInstalledPackages " +
                    " -long"
                    )
            (ret_code, output) = shell.Shell.runCmd(cmd)
            for line in output.split("\n"):
                if line == '': continue
                (installed_loc,packageid_ver,displayName,displayVersion) = line.split(" : ")
                if installed_loc == self.config['install_root']:
                    self.config['offering_id'] = packageid_ver.split('_',1)[0]
                    self.config['offering_version'] = None

        Package.imcl_rollback(self.config['imcl'], self.config['install_root'],
                self.config['offering_id'], self.config['offering_version']
                )

    def copy_package(self, packageName):
        xml = urlutils.XMLReader(url=self.config['url'], file=self.config['dm_file'],
                                sysName=self.sysName,sysBit=self.machine,vendorName=self.config['vendorname'],
                                packageName=packageName, version=self.version)
        self.config.update(xml.getSWDownloadDetails())
        urlutils.Download(self.config['url'], self.config['fileName'], self.config['target_loc'])
        Package.pucl_copy(os.path.join(self.config['install_root'], 'PUCL'), 'copy',
                    os.path.join(self.config['target_loc'],self.config['fileName'].rstrip('.zip')), self.config['pu_local_target'],
                    self.config['offering_id'], self.config['offering_version']
                    )

    def delete_package(self, packageName):
        for line in self.imcl_getAvailablePackages(self.config['pu_local_target']).split("\n"):
            if line == '': continue
            (repo,packageid_ver,displayName,displayVersion) = line.split(" : ")
            if displayVersion == self.version and str(displayName) == str(packageName):
                self.config['offering_id'], self.config['offering_version'] = packageid_ver.split('_',1)

        Package.pucl_delete(os.path.join(self.config['install_root'], 'PUCL'), 'delete',
                    self.config['pu_local_target'],
                    self.config['offering_id'], self.config['offering_version']
                    )

    def imcl_getAvailablePackages(self, repo):
        cmd =   (self.config['imcl'] +
                " listAvailablePackages " +
                " -repositories " + repo +
                " -long"
                )
        (ret_code, output) = shell.Shell.runCmd(cmd)
        return output

    @staticmethod
    def imcl_install(exec_script, install_root, imshared_root, repository,
                offering_id, offering_version=None, offering_features=None):
        logger.debug("Setting up cmd")
        offering_str = offering_id
        if offering_version != None:
            offering_str += '_' + offering_version
        if offering_features != None:
            offering_str += ',' + offering_features
        cmd =   ( exec_script +
                " install " + offering_str +
                " -repositories " + repository +
                " -installationDirectory " + install_root +
                " -sharedResourcesDirectory " + imshared_root +
                " -acceptLicense"
                )
        (ret_code, output) = shell.Shell.runCmd(cmd)

    @staticmethod
    def imcl_rollback(exec_script, install_root,
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
    def imcl_uninstall(exec_script, install_root, offering_id, offering_version=None, offering_features=None):
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

    @staticmethod
    def pucl_copy(exec_script, command, repository, target, offering_id=None, offering_version=None):
        offering_str = ""
        if offering_id != None:
            offering_str = offering_id
            if offering_version != None:
                offering_str += '_' + offering_version
        cmd =   (exec_script +
                " " + command + " " + offering_str +
                " -repositories " + repository +
                " -target " + target +
                " -acceptLicense"
                )
        (ret_code, output) = shell.Shell.runCmd(cmd)

    @staticmethod
    def pucl_delete(exec_script, command, target, offering_id, offering_version=None):
        offering_str = offering_id
        if offering_version != None:
            offering_str += '_' + offering_version
        cmd =   (exec_script +
                " " + command + " " + offering_str +
                " -target " + target
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
