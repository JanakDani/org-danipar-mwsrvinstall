import logging
import sys
import os
import stat
import optparse
import configparser
import zipfile
from mwsrvinstall.utils import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("websphere.im")


class InstallationManager():
    def __init__(self):
        pass

    @staticmethod
    def install(swdir, version, im_install_root, imdl_install_root, im_shared_root, 
                offering_profile, offering_features, offering_id, offering_version):
        logger.debug("Setting up imcl cmd")
        cmd = ( os.path.join(swdir, 'tools', 'imcl') + 
                            " install " + offering_id +
                            " -repositories " + os.path.join(swdir, 'repository.config') + 
                            " -installationDirectory " + os.path.join(im_install_root, 'eclipse') + 
                            " -dataLocation " + imdl_install_root + 
                            " -sharedResourcesDirectory " + im_shared_root + 
                            #" -installFixes all " + 
                            " -nl en " + 
                            " -acceptLicense" )
        (ret_code, output) = shell.Shell.runCmd(cmd) 

    @staticmethod
    def uninstall(imdl_install_root):
        cmd = ( os.path.join(imdl_install_root, 'uninstall', 'uninstallc') +
                " -silent" )
        (ret_code, output) = shell.Shell.runCmd(cmd)

class _ConfigParser():
    def __init__(self):
        pass

    @staticmethod
    def _getConfig(file, scope=['ALL']):
        config = configparser.ConfigParser() 
        config.read(file)
        try:
            scope.index('ALL')
            scope = config.sections()
        except:
            pass

        dicta = {}
        for eachscope in scope:
            try:
                config.has_section(eachscope)
                dicta[eachscope] = dict(config.items(eachscope))
            except (NoSectionError):
                logger.exception("Scope %s not found in %s" %(eachscope, file))
            except:
                logger.exception("Unknown Error has occured")
        return dicta


class _ArgParser():
    def __init__(self, sysargv):
        mandatories = ['action', 'scope', 'configfile']
        parser = optparse.OptionParser(option_class=extoptparse.extOption, usage='\n  %prog [options] <arg>')
        parser.add_option("--action", dest="action", help="supported action(s): install, remove")
        parser.add_option("--scope", dest="scope", help="use \"im\" as a scope")
        parser.add_option("--version", dest="version", default=None, help="provide installation version")
        parser.add_option("--config", dest="configfile", help="absolute path of config file")
        (self.options, self.args) = parser.parse_args(sysargv)

        for m in mandatories:
            if self.options.__dict__[m] == None:
                print("Mandatory option \"%s\" is missing" %(m))
                print(parser.print_help())
                parser.exit()

        
def main(inargs):
    logger.debug("Input arguments: %s" %(inargs))
    input = _ArgParser(inargs)
    (sysName, nodeName, release, version, machine) = os.uname()
    logger.info("System Information: %s(OS), %s(HOST), %s(Release), %s(ARCH)" %(sysName, nodeName, release, machine))
    rootConfig = _ConfigParser._getConfig(input.options.configfile, scope=['Root'])['Root']
    logger.debug("Root Config: %s" %(rootConfig))
    config = _ConfigParser._getConfig(input.options.configfile, scope=['InstallationManager'])['InstallationManager']
    config['user'] = rootConfig['user']
    config['group'] = rootConfig['group']

    if input.options.action == 'install':
        xml = urlutils.XMLReader(url=rootConfig['url'], file=rootConfig['dm_file'], 
                                sysName=sysName, vendorName='WebSphere', 
                                productName='InstallationManager', version=input.options.version)
        config.update(xml.getSWDownloadDetails())
        config.update(_ConfigParser._getConfig(input.options.configfile, 
                        scope=['InstallationManager_Offering_0'])['InstallationManager_Offering_0'])
        logger.info("Config information \n%s" %(config))
        urlutils.Download.software(config['url'], config['im_dl_loc'])
        config['file'] = os.path.join(config['im_dl_loc'], config['fileName'])
        if zipfile.is_zipfile(config['file']):
            logger.info("Extracting software %s. please wait" %(config['file']))
            zip = zip = zipfile.ZipFile(config['file'])
            zip.extractall(path=config['im_dl_loc'])
            logger.info("Extracted to %s" %(config['im_dl_loc']))
            for dirpath,dirs,fileNames in os.walk(config['im_dl_loc']):
                for fileName in fileNames:
                    file = os.path.join(dirpath, fileName)
                    os.chmod(file, stat.S_IRWXU)

        InstallationManager.install(config['im_dl_loc'], config['version'], config['im_install_root'],
                                config['imdl_install_root'], config['imshared_root'],
                                config['offering_profile'], config['offering_features'],
                                config['offering_id'], config['offering_version'])
    elif input.options.action == 'remove':
        InstallationManager.uninstall(config['imdl_install_root'])

if __name__ == '__main__':
    main(sys.argv)
