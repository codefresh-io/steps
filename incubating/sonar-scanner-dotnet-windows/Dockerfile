# FROM mcr.microsoft.com/windows/servercore:1809

# RUN powershell.exe -Command \
#     $Url = 'https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip'; \
#     $ZipFile = 'C:\ZipFolder\' + $(Split-Path -Path $Url -Leaf); \
#     $Destination= 'C:\Extracted\'; \
#     Invoke-WebRequest -Uri $Url -OutFile $ZipFile; \
#     $ExtractShell = New-Object -ComObject Shell.Application; \
#     $Files = $ExtractShell.Namespace($ZipFile).Items(); \
#     $ExtractShell.NameSpace($Destination).CopyHere($Files)
#     #Start-Process $Destination

FROM mcr.microsoft.com/windows/servercore:ltsc2019

# RUN powershell.exe -Command \
#   $ErrorActionPreference = 'Stop'; \
#   Invoke-WebRequest https://www.python.org/ftp/python/3.5.1/python-3.5.1.exe -OutFile c:\python-3.5.1.exe ; \
#   Start-Process c:\python-3.5.1.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; \
#   Remove-Item c:\python-3.5.1.exe -Force

RUN powershell.exe -Command \
    New-Item -Path c:\ -Name ZipFolder -ItemType directory; \
    $Url = 'https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip'; \
    echo "Url : $Url"; \
    $ZipFile = 'C:\ZipFolder\' + $(Split-Path -Path $Url -Leaf); \
    echo "ZipFile : $Zipfile"; \
    $Destination= 'C:\Extracted\'; \
    echo "Destination : $Destination"; \
    Invoke-WebRequest -Uri $Url -OutFile $ZipFile; \
    Get-ChildItem C:\ZipFolder\; \
    $ExtractShell = New-Object -ComObject Shell.Application; \
    Get-ChildItem C:\Destination\; \
    $ExtractShell.NameSpace($Destination).CopyHere($Zipfile)
     Get-ChildItem C:\Extracted\; \
    #Start-Process $Destination

# RUN powershell -Command $Url = "https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip"
# RUN powershell -Command $ZipFile = C:\ZipFolder\ + $(Split-Path -Path $Url -Leaf)
# RUN powershell -Command $Destination = C:\SonarSource\
# RUN powershell -Command Invoke-WebRequest -Uri $Url -OutFile $ZipFile
# RUN powershell -Command $ExtractShell = New-Object -ComObject Shell.Application
# RUN powershell -Command $Files = $ExtractShell.Namespace($ZipFile).Items()
# RUN powershell -Command $ExtractShell.NameSpace($Destination).CopyHere($Files)
# RUN powershell -Command Start-Process $Destination