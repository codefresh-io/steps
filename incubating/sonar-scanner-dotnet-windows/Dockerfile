FROM mcr.microsoft.com/windows/servercore:1809

RUN powershell.exe $Url = 'https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip'
RUN powershell.exe $ZipFile = 'C:\\ZipFolder\\' + $(Split-Path -Path $Url -Leaf)
RUN powershell.exe $Destination= 'C:\\Extracted\\'
RUN powershell.exe Invoke-WebRequest -Uri $Url -OutFile $ZipFile
RUN powershell.exe $ExtractShell = New-Object -ComObject Shell.Application
RUN powershell.exe $Files = $ExtractShell.Namespace($ZipFile).Items()
RUN powershell.exe $ExtractShell.NameSpace($Destination).CopyHere($Files)
    #Start-Process $Destination

# RUN powershell -Command $Url = "https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip"
# RUN powershell -Command $ZipFile = C:\ZipFolder\ + $(Split-Path -Path $Url -Leaf)
# RUN powershell -Command $Destination = C:\SonarSource\
# RUN powershell -Command Invoke-WebRequest -Uri $Url -OutFile $ZipFile
# RUN powershell -Command $ExtractShell = New-Object -ComObject Shell.Application
# RUN powershell -Command $Files = $ExtractShell.Namespace($ZipFile).Items()
# RUN powershell -Command $ExtractShell.NameSpace($Destination).CopyHere($Files)
# RUN powershell -Command Start-Process $Destination