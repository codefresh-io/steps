FROM mcr.microsoft.com/windows/servercore:1809


# RUN powershell.exe -Command Invoke-WebRequest "https://www.python.org/ftp/python/3.5.1/python-3.5.1.exe" -OutFile c:\python-3.5.1.exe
# RUN powershell.exe -Command Start-Process c:\python-3.5.1.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait
# RUN Start-Process $Destinatio
# RUN powershell.exe -Command Remove-Item c:\python-3.5.1.exe -Force

RUN powershell -Command "$Url = 'https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip'; \
      powershell -Command $ZipFile = 'C:\ZipFolder\' + $(Split-Path -Path $Url -Leaf); \
      powershell -Command $Destination= 'C:\SonarSource\';  \
      powershell -Command Invoke-WebRequest -Uri $Url -OutFile $ZipFile; \
      powershell -Command $ExtractShell = New-Object -ComObject Shell.Application;\
      powershell -Command $Files = $ExtractShell.Namespace($ZipFile).Items();\
      powershell -Command $ExtractShell.NameSpace($Destination).CopyHere($Files); \
      powershell -Command Start-Process $Destination;"