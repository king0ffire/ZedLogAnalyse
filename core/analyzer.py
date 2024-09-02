import gzip
import io
import os
import tarfile
import logging

logger=logging.getLogger(__name__)
class Analyzer():
    def last_20_lines_in_file(self, gzfilepath:str,targetfilepath:str|list[str]) -> list[str]|None:
        res=[]
        with tarfile.open(gzfilepath, 'r:gz') as tar:
            try:
                if isinstance(targetfilepath, str):
                    target_file=tar.getmember(targetfilepath)
                    file_obj=tar.extractfile(target_file)
                    if file_obj:
                        lines=file_obj.readlines()
                        for line in lines[-20:]:
                            res.append(line.decode('utf-8').strip())
                    else:
                        logger.info("File open failed")
                        return None
                else:
                    target_file=tar.getmember(targetfilepath[0])
                    inner_tar_obj=tar.extractfile(target_file)
                    if inner_tar_obj:
                        with tarfile.open(fileobj=inner_tar_obj,mode= 'r:gz') as inner_tar:
                            try:
                                target_file=inner_tar.getmember(targetfilepath[1])
                                file_obj=inner_tar.extractfile(target_file)
                                if file_obj:
                                    lines=file_obj.readlines()
                                    for line in lines[-20:]:
                                        res.append(line.decode('utf-8').strip())
                                else:
                                    logger.info("File open failed")
                                    return None
                            except Exception as e:
                                logger.error(f"error during open inner tarfile: {e}")
                                raise e
                                return None
            except KeyError as e:
                logger.error(f"error during get member: {e}")
                return None
            except Exception as e:
                logger.error(f"error during open tarfile: {e}")
                raise e
                return None
        return res