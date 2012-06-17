import logging
import sys
import os
import urllib.request
from xml.dom.minidom import parse, parseString

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("utils.urlutils")

class XMLReader():
    def __init__(self, url, file, sysName,vendorName, productName, version=None):
        self.sysName  = sysName
        self.url = url
        self.file = file
        self.vendorName = vendorName
        self.productName = productName
        self.version = version
        try:
            httpfile = urllib.request.urlopen(os.path.join(url, file))
            self.data = httpfile.read()
            httpfile.close()
        except (urllib.error.HTTPError):
            logger.exception("Problems while getting file %(s)" %(file))

    def getOSNode_Text(self, node):
        dicta = {}
        for osNode in node:
            if osNode.nodeName == 'OS':
                if osNode.getAttribute('TYPE') == self.sysName:
                    fileName = XMLReader._getTextData(osNode.getElementsByTagName('FILENAME')[0].childNodes)
                    location = XMLReader._getTextData(osNode.getElementsByTagName('LOCATION')[0].childNodes)
                    dicta['fileName'] = fileName
                    dicta['url'] = os.path.join(self.url, location, fileName)
                    #dicta['version'] = dict_temp['VERSION']
                    #dicta['offering_version'] = dict_temp['OFFERING_VERSION']
                    #dicta['offering_id'] = dict_temp['OFFERING_ID']
        return dicta


    def getSWDownloadDetails(self):
        swDownloadURL = ""
        dicta = {}
        dom = parseString(self.data)
        dm = dom.getElementsByTagName('dm')[0]
        for vendorNode in dm.childNodes:
            if vendorNode.nodeName == self.vendorName:
                for productNode in vendorNode.childNodes:
                    if productNode.nodeName == self.productName:
                        dict_temp = dict(productNode.attributes.items())
                        dicta['version'] = dict_temp['VERSION']
                        dicta['offering_version'] = dict_temp['OFFERING_VERSION']
                        dicta['offering_id'] = dict_temp['OFFERING_ID']
                        if not self.version:
                            if dict_temp['default'] == 'true':
                                dicta.update(self.getOSNode_Text(productNode.childNodes))
                        elif dict_temp['VERSION'] == self.version:
                            dicta.update(self.getOSNode_Text(productNode.childNodes))
        return dicta

    @staticmethod
    def _getTextData(nodeList):
        for node in nodeList:
            if node.nodeType == node.TEXT_NODE:
                return node.data


class Download():
    def __init__(self):
        pass

    @staticmethod
    def software(url, dl_loc):
        try:
            fileName = url.split('/')[-1]
            data = None
            handle = urllib.request.urlopen(url)
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
            logger.info("%s - successfully downloaded" %(os.path.join(dl_loc,fileName)))
        except (urllib.request.URLError):
            try:
                fo.close()
            except:
                pass
            logger.exception("Download failed")  
