"""IBM Middleware product installation. Supports for Installation manager, Packaging utility and other products.
"""
import logging
import sys
import os
import stat
from lib import *
import diomreader
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("oracle.oracle")


class Package():
    """Install/rollback/uninstall Packages
    For Packaging utility, copy or delete packages
    """
    __repoOnline = 'Online_Repo'
    __repoLocal = 'Local_Repo'
    """
    __profileIM = 'InstallationManager'
    __pkg_nameIM = 'com.ibm.cic.agent'
    __pkg_namePU = 'com.ibm.cic.packagingUtility'
    """

    def __init__(self, vendorname, profile, configFile, version=None, isPatchUpgrade=False):
        self.profile = profile
        self.configFile = configFile
        self.version = version
        self.setConfig(vendorname)
        self.isPatchUpgrade = isPatchUpgrade

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

    def install(self):
        #print self.config
        if self.config['repo_option'] == Package.__repoLocal:
            download.Download(self.config['url'], self.config['fileName'],
                              self.config['target_loc'], realm=self.config['url_realm'],
                              user=self.config['url_user'], passwd=self.config['url_passwd'])

        if not self.isPatchUpgrade:
            if self.config['repo_option'] == Package.__repoLocal:
                download.Download(self.config['url'], self.config['fileName'],
                              self.config['target_loc'], realm=self.config['url_realm'],
                              user=self.config['url_user'], passwd=self.config['url_passwd'])
            ## check if silent file location is correct
            if not os.path.isfile(self.config['silent_file']):
                logger.critical("Silent file %s not found. Exiting ...", self.config['silent_file'])
                sys.exit()
            else:
                logger.info("Silent file %s found", self.config['silent_file'])

            ## check if java_home location is correct
            if not os.path.isdir(self.config["java_home"]):
                logger.critical("java home %s not found. Exiting ...", self.config['java_home'])
                sys.exit()
            else:
                logger.info("java home %s found", self.config['java_home'])

            ## generate silent xml file
            silent_file = os.path.join(self.config['target_loc'], os.path.basename(self.config['silent_file']))
            logger.info("Generating silent xml file %s", silent_file)
            output = open(silent_file, 'w')
            data = open(self.config['silent_file']).read()
            data = re.sub("REPL_BEAHOME",os.path.dirname(self.config['install_root']), data)
            data = re.sub("REPL_WLS_INSTALL_DIR",self.config['install_root'], data)
            data = re.sub("REPL_COMPONENT_PATHS",self.config['offering_features'], data)
            output.write(data)
            output.close()
            Package.new_install(os.path.join(self.config['java_home'], 'bin/java'),
                            self.config['java_args'],
                            os.path.join(self.config['target_loc'], self.config['fileName']),
                            silent_file)
        else:
            mw_home = os.path.dirname(self.config['install_root'])
            cache_dir = os.path.join(mw_home, 'utils/bsu/cache_dir')
            if self.config['repo_option'] == Package.__repoLocal:
                download.Download(self.config['url'], self.config['fileName'],
                              cache_dir, realm=self.config['url_realm'],
                              user=self.config['url_user'], passwd=self.config['url_passwd'])
            patchlist = self.config['packageversion']
            prod_dir = self.config['install_root']
            logger.info("Deleting %s file", os.path.join(cache_dir, self.config['fileName']))
            os.remove(os.path.join(cache_dir, self.config['fileName']))
            Package.patch_install(mw_home, cache_dir, patchlist,
                                  prod_dir)

    def uninstall(self):
        uninstall_sh = os.path.join(os.path.dirname(self.config['install_root']), 'utils/uninstall/uninstall.sh')
        if os.path.isfile(uninstall_sh):
            cmd = ( uninstall_sh +
                    " -mode=silent"
                  )
            (ret_code, output) = shell.Shell.runCmd(cmd)
        else:
            logger.error("Cannot find installation at %s", os.path.dirname(self.config['install_root']))

    def remove(self):
        print self.config
        mw_home = os.path.dirname(self.config['install_root'])
        patchlist = self.version
        prod_dir = self.config['install_root']
        Package.patch_remove(mw_home, patchlist, prod_dir)

    def imcl_getAvailablePackages(self, repo):
        cmd =   (self.config['imcl'] +
                " listAvailablePackages " +
                " -repositories " + repo +
                " -long"
                )
        (ret_code, output) = shell.Shell.runCmd(cmd)
        return output

    @staticmethod
    def new_install(java_exec, java_args, installer_jar, silent_file):
        cmd = ( java_exec + " " +
                java_args +
                " -jar " + installer_jar +
                " -mode=silent" +
                " -silent_xml=" + silent_file
              )
        (ret_code, output) = shell.Shell.runCmd(cmd,silent='on')

    @staticmethod
    def patch_install(mw_home, patch_download_dir, patchlist, prod_dir):
        curr_dir = os.getcwd()
        os.chdir(os.path.join(mw_home, 'utils/bsu'))
        cmd = ( "./bsu.sh" +
                " -install " +
                " -patch_download_dir=" + patch_download_dir +
                " -patchlist=" + patchlist +
                " -prod_dir=" + prod_dir +
                " -verbose"
              )
        (ret_code, output) = shell.Shell.runCmd(cmd)
        os.chdir(curr_dir)

    @staticmethod
    def patch_remove(mw_home, patchlist, prod_dir):
        curr_dir = os.getcwd()
        os.chdir(os.path.join(mw_home, 'utils/bsu'))
        cmd = ( "./bsu.sh" +
                " -remove " +
                " -patchlist=" + patchlist +
                " -prod_dir=" + prod_dir +
                " -verbose"
              )
        (ret_code, output) = shell.Shell.runCmd(cmd)
        os.chdir(curr_dir)
