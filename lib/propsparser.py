import logging
import ConfigParser as configparser
#import configparser #Use this for python3

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt="")
logger = logging.getLogger("swinstall.propsparser")

def ini(file, scope=['ALL']):
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
            logger.exception("Scope %s not found in %s", eachscope, file)
        except:
            logger.exception("Unknown Error has occured")

    logger.debug("Loaded %s config: %s", scope, dicta)
    return dicta

