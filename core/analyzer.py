import copy
import gzip
import io
import os
import tarfile
import logging
from typing import Any
from util import enumtypes
import fnmatch

logger=logging.getLogger(__name__)
class Analyzer():
    def last_x_lines_in_file(self, gzfilepath:str,targetfilepath:str|list[str],numberoflines=100) -> list[str]|None:
        res=[]
        with tarfile.open(gzfilepath, 'r:gz') as tar:
            try:
                if isinstance(targetfilepath, str):
                    target_file=tar.getmember(targetfilepath)
                    file_obj=tar.extractfile(target_file)
                    if file_obj:
                        lines=file_obj.readlines()
                        for line in lines[-numberoflines:]:
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
                                    for line in lines[-numberoflines:]:
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
    
    def recursive_analyze(self, currenttarfileinfo:tarfile.TarFile, tasks:tuple, currentdict:dict[str,dict|None|list[str]], numberoflines=100): #targetfilepath：当前文件下的任务目标：文件解析和递归目录解析
        for task in tasks:
            logger.debug(f"current task:{task}")
            if len(task)!=2:
                logger.error(f"预定义的路径格式不正确{task}")
                continue
            if isinstance(task[1],enumtypes.AnalyzerType):
                for member in currenttarfileinfo.getmembers():
                    if fnmatch.fnmatch(member.name, task[0]):
                        if task[1]==enumtypes.AnalyzerType.Analyze:
                            final_text_file=currenttarfileinfo.extractfile(member)
                            res:list[str]=[]
                            if final_text_file:
                                lines=final_text_file.readlines()
                                for line in lines[-numberoflines:]:
                                    res.append(line.decode('utf-8').strip())
                            else:
                                logger.info("File open failed")
                            currentdict[os.path.basename(member.name)]=res
                        elif task[1]==enumtypes.AnalyzerType.DisplayOnly:
                            currentdict[os.path.basename(member.name)]=None
                        else:
                            logger.error("不支持的任务类型")
                logger.debug(f"finished task: {task}")
            else:
                for member in currenttarfileinfo.getmembers():
                    logger.debug(f"current member:{member.name}")
                    if fnmatch.fnmatch(member.name, task[0]):
                        currentdict[os.path.basename(member.name)]={}
                        if member.name.endswith("gz"):
                            inner_tarfileinfo=tarfile.open(fileobj=currenttarfileinfo.extractfile(member),mode='r:gz')
                        elif member.name.endswith("bz2"):
                            inner_tarfileinfo=tarfile.open(fileobj=currenttarfileinfo.extractfile(member),mode='r:bz2')
                        else:
                            logger.error("不是支持的文件类型")
                        try:
                            self.recursive_analyze(inner_tarfileinfo,task[1],currentdict[os.path.basename(member.name)],numberoflines)
                        finally:
                            inner_tarfileinfo.close()
