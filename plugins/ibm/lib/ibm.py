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
logger = logging.getLogger("ibm.ibm")

class InstallationManager():
    """Install/Remove Installation Manager.
    """
    def __init__(self):
        pass

    @staticmethod
    def install(exec_script, im_install_root, imdl_install_root, imshared_root, repository,
                packagename, packagebuild=None, offering_features=None):
        """Installs installation manager
        """
        logger.debug("Setting up imcl cmd")

        offering_str = packagename
        if packagebuild != None:
            offering_str += '_' + packagebuild
        if offering_features != None:
            offering_str += ',' + offering_features

        cmd =   ( exec_script +
                " install " + packagename +
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
    __profileIM = 'InstallationManager'
    __repoOnline = 'Online_Repo'
    __repoLocal = 'Local_Repo'
    __pkg_nameIM = 'com.ibm.cic.agent'
    __pkg_namePU = 'com.ibm.cic.packagingUtility'

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
        ## Load IM if Package is not IM
        if self.config['pkg_name'] != Package.__pkg_nameIM:
            self.config.update(propsparser.ini(self.configFile,
                                scope=[Package.__profileIM])[Package.__profileIM])
            ## load IM data if file found
            if self.config.has_key('im_config_file'):
                self.config['im_config_file'] = os.path.join(os.path.dirname(self.configFile),
                                                             self.config['im_config_file'])
                self.config.update(propsparser.ini(self.config['im_config_file'],
                                                   scope=[Package.__profileIM])[Package.__profileIM])
                self.config.update(propsparser.ini(self.configFile,
                                scope=[Package.__profileIM])[Package.__profileIM])
                self.config['im_config_file'] = os.path.join(os.path.dirname(self.configFile),
                                                             self.config['im_config_file'])
            self.config.update(propsparser.ini(self.configFile, scope=[self.profile])[self.profile])
        self.config['profile'] = self.profile
        self.config['imcl'] = os.path.join(self.config['im_install_root'],'eclipse','tools','imcl')
        ## Load local repo if package is IM or PU based on root data file
        if self.config['pkg_name'] == Package.__pkg_nameIM or \
        self.config['pkg_name'] == Package.__pkg_namePU:
            if self.config.has_key('root_config_file'):
                self.config.update(propsparser.ini(self.config['root_config_file'],
                                                   scope=[Package.__repoLocal])[Package.__repoLocal])
            else:
                self.config.update(propsparser.ini(self.configFile,
                                    scope=[Package.__repoLocal])[Package.__repoLocal])
        else:
            if self.config.has_key('root_config_file'):
                self.config.update(propsparser.ini(self.config['root_config_file'],
                                                   scope=[self.config['repo_option']])[self.config['repo_option']])
            else:
                self.config.update(propsparser.ini(self.configFile,
                                scope=[self.config['repo_option']])[self.config['repo_option']])

    def install(self):
        # Read online and download software
        #xml = diomreader.XMLReader(url=self.config['url'], file=self.config['dm_file'],
        #                        sysName=self.sysName,sysBit=self.machine,vendorName=self.config['vendorname'],
        #                        packageName=self.config['pkg_name'], version=self.version)
        #self.config.update(xml.getSWDownloadDetails())
        #print self.config

        if self.config['packagename'] != Package.__pkg_nameIM and \
        not os.path.isdir(self.config['im_install_root']):
            raise Exception('Installation Manager not found installed')

        if self.config['repo_option'] == Package.__repoLocal:
            download.Download(self.config['url'], self.config['fileName'],
                              self.config['target_loc'], realm=self.config['url_realm'],
                              user=self.config['url_user'], passwd=self.config['url_passwd'])

        if self.config['packagename'] == Package.__pkg_nameIM:
            InstallationManager.install(os.path.join(self.config['target_loc'],
                                                     self.config['fileName'].rstrip('.zip'),
                                                     'tools', 'imcl'),
                                        self.config['im_install_root'],
                                        self.config['imdl_install_root'],
                                        self.config['imshared_root'],
                                        os.path.join(self.config['target_loc'],
                                                                   self.config['fileName'].rstrip('.zip')),
                                        self.config['packagename'],
                                        self.config['packagebuild']
                        )
        elif self.config['packagename'] == Package.__pkg_namePU:
            Package.imcl_install(self.config['imcl'], self.config['install_root'], self.config['imshared_root'],
                        os.path.join(self.config['target_loc'], self.config['fileName'].rstrip('.zip')),
                        self.config['packagename'], self.config['packagebuild']
                        )
        else:
            if not self.config.has_key('offering_properties') or self.config['offering_properties'] == "":
                self.config['offering_properties'] = None
            if not self.config.has_key('offering_preferences') or self.config['offering_preferences'] == "":
                self.config['offering_preferences'] = None
            if self.config['repo_option'] == Package.__repoLocal:
                Package.imcl_install(self.config['imcl'], self.config['install_root'], self.config['imshared_root'],
                        os.path.join(self.config['target_loc'], self.config['fileName'].rstrip('.zip')),
                        self.config['packagename'], self.config['packagebuild'], self.config['offering_features'],
                        self.config['offering_properties'], self.config['offering_preferences']
                        )
            elif self.config['repo_option'] == Package.__repoOnline:
                Package.imcl_install(self.config['imcl'], self.config['install_root'], self.config['imshared_root'],
                        os.path.join(self.config['target_loc'], self.config['packagename']),
                        self.config['packagename'], self.config['packagebuild'], self.config['offering_features'],
                        self.config['offering_properties'], self.config['offering_preferences']
                        )

    def uninstall(self):
        if self.config['pkg_name'] == Package.__pkg_nameIM:
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
                    self.config['pkg_name'], self.config['packagebuild'] = packageid_ver.split('_',1)

            Package.imcl_uninstall(self.config['imcl'], self.config['install_root'],
                    self.config['pkg_name'], self.config['packagebuild']
                    )

    def rollback(self):
        ##Get offering version to rollback to
        if self.version != None:
            if self.config['repo_option'] == Package.__repoLocal:
                xml = diomreader.XMLReader(url=self.config['url'], file=self.config['dm_file'],
                                sysName=self.sysName,sysBit=self.machine,vendorName=self.config['vendorname'],
                                packageName=self.config['pkg_name'], version=self.version,
                                realm=self.config['realm'], user=self.config['url_user'],
                                passwd=self.config['url_passwd'])
                self.config.update(xml.getSWDownloadDetails())
            elif self.config['repo_option'] == Package.__repoOnline:
                for line in self.imcl_getAvailablePackages(self.config['target_loc']).split("\n"):
                    if line == '': continue
                    (repo,packageid_ver,displayName,displayVersion) = line.split(" : ")
                    if displayVersion == self.version and str(displayName) == self.config['pkg_name']:
                        self.config['packagename'], self.config['packagebuild'] = packageid_ver.split('_',1)
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
                    self.config['packagename'] = packageid_ver.split('_',1)[0]
                    self.config['packagebuild'] = None

        Package.imcl_rollback(self.config['imcl'], self.config['install_root'],
                self.config['packagename'], self.config['packagebuild']
                )

    def copy_package(self, packageName):
        xml = diomreader.XMLReader(url=self.config['url'], file=self.config['dm_file'],
                                sysName=self.sysName,sysBit=self.machine,vendorName=self.config['vendorname'],
                                packageName=packageName, version=self.version,
                                realm=self.config['url_realm'], user=self.config['url_user'],
                                passwd=self.config['url_passwd'])
        self.config.update(xml.getSWDownloadDetails())
        download.Download(self.config['url'], self.config['fileName'], self.config['target_loc'],
                          realm=self.config['url_realm'],user=self.config['url_user'], passwd=self.config['url_passwd'])
        Package.pucl_copy(os.path.join(self.config['install_root'], 'PUCL'), 'copy',
                    os.path.join(self.config['target_loc'],self.config['fileName'].rstrip('.zip')),
                    os.path.join(self.config['pu_local_target'],self.config['packagename']),
                    self.config['packagename'], self.config['packagebuild']
                    )

    def delete_package(self, packageName):
        for line in self.imcl_getAvailablePackages \
                    (os.path.join(self.config['pu_local_target'],
                                  packageName)).split("\n"):
            if line == '': continue
            (repo,packageid_ver,displayName,displayVersion) = line.split(" : ")
            if displayVersion == self.version:
                self.config['packagename'], self.config['packagebuild'] = packageid_ver.split('_',1)

        Package.pucl_delete(os.path.join(self.config['install_root'], 'PUCL'), 'delete',
                    os.path.join(self.config['pu_local_target'],self.config['packagename']),
                    self.config['packagename'], self.config['packagebuild']
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
                packagename, packagebuild=None, offering_features=None,
                offering_properties=None, offering_preferences=None):
        logger.debug("Setting up cmd")
        offering_str = packagename
        if packagebuild != None:
            offering_str += '_' + packagebuild
        if offering_features != None:
            offering_str += ',' + offering_features
        cmd =   ( exec_script +
                " install " + offering_str +
                " -repositories " + repository +
                " -installationDirectory " + install_root +
                " -sharedResourcesDirectory " + imshared_root +
                " -acceptLicense"
                )
        if offering_properties != None:
            cmd = cmd + ' -properties ' + offering_properties
        if offering_preferences != None:
            cmd = cmd + ' -preferences ' + offering_preferences
        (ret_code, output) = shell.Shell.runCmd(cmd)

    @staticmethod
    def imcl_rollback(exec_script, install_root,
                packagename, packagebuild=None, offering_features=None):
        logger.debug("Setting up cmd")
        offering_str = packagename
        if packagebuild != None:
            offering_str += '_' + packagebuild
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
    def imcl_uninstall(exec_script, install_root, packagename, packagebuild=None, offering_features=None):
        offering_str = packagename
        if packagebuild != None:
            offering_str += '_' + packagebuild
        if offering_features != None:
            offering_str += ',' + offering_features
        cmd =   (exec_script +
                " uninstall " + offering_str +
                " -installationDirectory " + install_root
                )
        (ret_code, output) = shell.Shell.runCmd(cmd)

    @staticmethod
    def pucl_copy(exec_script, command, repository, target, packagename=None, packagebuild=None):
        offering_str = ""
        if packagename != None:
            offering_str = packagename
            if packagebuild != None:
                offering_str += '_' + packagebuild
        cmd =   (exec_script +
                " " + command + " " + offering_str +
                " -repositories " + repository +
                " -target " + target +
                " -acceptLicense"
                )
        (ret_code, output) = shell.Shell.runCmd(cmd)

    @staticmethod
    def pucl_delete(exec_script, command, target, packagename, packagebuild=None):
        offering_str = packagename
        if packagebuild != None:
            offering_str += '_' + packagebuild
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
