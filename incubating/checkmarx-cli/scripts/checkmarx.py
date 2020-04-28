import sys
import getopt
import os
import subprocess
import time
import json

def main(argv):
  cxserver = ''
  cxuser = ''
  cxpassword = ''
  projectname = ''
  locationtype = ''
  locationurl = ''
  locationbranch = ''
  working_directory = '/opt/checkmarx/checkmarxcli'
  try:
    opts, args = getopt.getopt(argv,"s:u:p:n:l:r:b:",["help","cxserver=","cxuser=","cxpassword=","projectname=","locationtype=","locationurl=","locationbranch="])
  except getopt.GetoptError:
    print('Unrecognized Argument, See Usage Below.')
    print('more information about arguments is available at https://checkmarx.atlassian.net/wiki/pages/viewpage.action?pageId=129702980 ')
    sys.exit(2)
  for opt,arg in opts:
    if opt == "--help":
      print('-s --CxServer - DNS name of checkmarx server')
      print('-u --CxUser - is username to login into checkmarx')
      print('-p --CxPassword - password for checkmarx')
      print('-n --Projectname - projectname of repo, if new give repo name')
      print('-l --locationtype - sourcetype location, would mostly be git')
      print('-r --locationurl -Source control URL, with token format')
      print('-b --locationbranch -branch to run the scan on')
      command = ['./runCxConsole.sh --help']
      proc = subprocess.Popen(command, shell=True, cwd=working_directory)
      stdout, stderr = proc.communicate()
      sys.exit()
    elif opt in ("-s", "-cxserver"):
      cxserver = arg
    elif opt in ("-u", "-Cxuser"):
      cxuser = arg
    elif opt in ("-p", "-cxpassword"):
      cxpassword = arg
    elif opt in ("-n", "-projectname"):
      projectname = arg
    elif opt in ("-l", "-locationtype"):
      locationtype = arg
    elif opt in ("-r", "-locationurl"):
      locationurl = arg
    elif opt in ("-b", "-locationbranch"):
      locationbranch = arg
  command = ['./runCxConsole.sh scan -CxServer "' + cxserver + '" -Cxuser "' + cxuser + '" -cxpassword "' + cxpassword + '" -projectname "' + projectname + '" -locationtype ' + locationtype + ' -locationurl "' + locationurl + '" -locationbranch "' + locationbranch + '" -ForceScan -v']
  proc = subprocess.Popen(command, shell=True, cwd=working_directory)
  stdout, stderr = proc.communicate()
if __name__ == "__main__":
  main(sys.argv[1:])
