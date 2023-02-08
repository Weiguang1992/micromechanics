#!/usr/bin/python3
import sys, os, subprocess
import configparser


def get_version():
  """
  Get current version number from git-tag

  Returns:
    string: v0.0.0
  """
  result = subprocess.run(['git','tag'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
  versionList= result.stdout.decode('utf-8').strip()
  versionList= [i[1:] for i in versionList.split('\n')]
  if versionList == ['']:  #default
    return 'v0.0.1'
  versionList.sort(key=lambda s: list(map(int, s.split('.'))))
  return 'v'+versionList[-1]


def newVersion(level=2, message=''):
  """
  Create a new version

  Args:
    level (int): which number of the version to increase 0=mayor,1=minor,2=sub
    message (str): what is the name/message
  """
  #get old version number
  version = [int(i) for i in get_version()[1:].split('.')]
  #create new version number
  version[level] += 1
  for i in range(level+1,3):
    version[i] = 0
  version = '.'.join([str(i) for i in version])
  print('======== Version '+version+' =======')
  #update python files
  filesToUpdate = {'micromechanics/__init__.py':'__version__ = ', 'docs/source/conf.py':'version = '}
  for path in filesToUpdate:
    with open(path, encoding='utf-8') as fIn:
      fileOld = fIn.readlines()
    fileNew = []
    for line in fileOld:
      line = line[:-1]  #only remove last char, keeping front part
      if line.startswith(filesToUpdate[path]):
        line = filesToUpdate[path]+'"'+version+'"'
      fileNew.append(line)
    with open(path,'w', encoding='utf-8') as fOut:
      fOut.write('\n'.join(fileNew)+'\n')
  #execute git commands: move tests away and back
  os.system('git mv pasta_eln/Tests Tests')
  os.system('git commit -a -m "'+message+'"')
  os.system('git tag -a v'+version+' -m "Version '+version+'"')
  os.system('git push')
  os.system('git push origin v'+version)
  os.system('git mv Tests pasta_eln/Tests')
  os.system('git commit -a -m "Added Tests back into distribution"')
  return


def createRequirementsFile():
  """
  Create a requirements.txt file from the setup.cfg information
  """
  config = configparser.ConfigParser()
  config.read('setup.cfg')
  requirements = config['options']['install_requires'].split('\n')
  # Linux
  requirementsLinux = [i for i in requirements if i!='' and 'Windows' not in i]
  with open('requirements-linux.txt','w', encoding='utf-8') as req:
    req.write('#This file is autogenerated by commit.py from setup.cfg. Change content there\n')
    req.write('\n'.join(requirementsLinux))
  # Windows
  requirementsWindows = [i for i in requirements if i!='']
  requirementsWindows = [i.split(';')[0] if 'Windows' in i else i for i in requirementsWindows]
  with open('requirements-windows.txt','w', encoding='utf-8') as req:
    req.write('#This file is autogenerated by commit.py from setup.cfg. Change content there\n')
    req.write('\n'.join(requirementsWindows))
  return


if __name__=='__main__':
  createRequirementsFile()
  if len(sys.argv)==1:
    print("**Require more arguments for creating new version 'message' 'level (optionally)' ")
    level = None
  elif len(sys.argv)==2:
    level=2
  else:
    level = int(sys.argv[2])
  if level is not None:
    message = sys.argv[1]
    newVersion(level, message)
