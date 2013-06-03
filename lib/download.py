import logging
import sys
import os
import zipfile
import stat
import urllib2 ##remove this for python3
##import urllib.request use this for python3

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("swinstall.download")

class Download():
    def __init__(self, url, fileName, target_loc, realm=None,user=None, passwd=None):
        if fileName:
            file = os.path.join(target_loc, fileName)
            if not os.path.isfile(file):
                Download.software(url, target_loc, realm=realm, user=user, passwd=passwd)
            Download.extract(file, target_loc)
            Download.setPermissions(target_loc)
        else:
            logger.exception("fileName not found in configuration")

    @staticmethod
    def setPermissions(target_loc):
        logger.info("Setting up permissions on %s", target_loc)
        for dirpath,dirs,fileNames in os.walk(target_loc):
            for fileName in fileNames:
                file = os.path.join(dirpath, fileName)
                os.chmod(file, stat.S_IRWXU)

    @staticmethod
    def extract(file, target_loc):
        logger.info("Extracting software %s. please wait...", file)
        if file.rsplit('.')[-1] == 'zip':
            if not os.path.isdir(file.rstrip('.zip')):
                if zipfile.is_zipfile(file):
                    logger.info("Zip file found. please wait...")
                    zip = zipfile.ZipFile(file)
                    zip.extractall(path=target_loc)
                    logger.info("Software extracted to %s", target_loc)
            else:
                logger.debug("Software %s already found. Skipping unzip ...", file)
        else:
            logger.warning("File extension not supported for file %s", file)

    @staticmethod
    def software(url, dl_loc, realm=None, user=None, passwd=None):
        ## auth
        if user != None and passwd != None:
            auth = urllib2.HTTPBasicAuthHandler()
            auth.add_password(
                            realm=realm,
                            uri=url,
                            user='%s'%user,
                            passwd=passwd
                            )
            opener = urllib2.build_opener(auth)
            urllib2.install_opener(opener)
        try:
            fileName = url.split('/')[-1]
            data = None
            handle = urllib2.urlopen(url)
            if not os.path.isdir(dl_loc):
                os.mkdir(dl_loc)
            fo = open(os.path.join(dl_loc, fileName), "wb")
            size = int(handle.info()["Content-Length"])
            type = str(handle.info()["Content-Type"])
            dlSize = 0
            blockSize = 8*1024
            previous_percent = 0
            while True:
                buffer = handle.read(blockSize)
                dlSize += len(buffer)
                if not buffer:
                    break

                fo.write(buffer)
                percent = int(dlSize*100/size)
                if previous_percent != percent:
                    previous_percent = percent
                    sys.stdout.write("\r%2d%% - [%d,%s]" %(percent, dlSize, fileName))
            fo.close()
            sys.stdout.write("\n")
            logger.info("%s - successfully downloaded", os.path.join(dl_loc,fileName))
        except urllib2.HTTPError, e:
            if e.code == 401:
                logger.exception("Authorization Failed - %s" %(e.code))
            else:
                logger.exception("Download failed")
        except:
            logger.exception("Download failed")
        finally:
            try:
                fo.close()
            except:
                pass
