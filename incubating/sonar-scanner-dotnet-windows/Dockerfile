FROM mcr.microsoft.com/windows/servercore:ltsc2019

#SHELL ["powershell", "-command"]

# Install Chocolatey and some required packages
#RUN Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
RUN powershell -NoProfile -ExecutionPolicy Bypass -Command \
    $Env:chocolateyVersion = '0.10.15' ; \
    $Env:chocolateyUseWindowsCompression = 'false' ; \
    "[Net.ServicePointManager]::SecurityProtocol = \"tls12, tls11, tls\"; iex ((New-Object System.Net.WebClient).DownloadString('http://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

RUN choco install nuget.commandline -y

RUN powershell -NoProfile -ExecutionPolicy Bypass -Command \
    choco install git -y --debug

RUN choco install vim -y

RUN choco install netfx-4.8 -y

RUN choco install netfx-4.8-devpack -y

RUN choco install visualstudio2019buildtools -y

# Install Sonarqube Windows Scanner

RUN powershell -Command \
    New-Item -Path c:\ -Name ZipFolder -ItemType directory; \
    New-Item -Path c:\ -Name Extracted -ItemType directory; \
    $Url = 'https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip'; \
    $Destination= 'C:\Extracted\'; \
    $ZipFile = 'C:\ZipFolder\' + $(Split-Path -Path $Url -Leaf); \
    Invoke-WebRequest -Uri $Url -OutFile $ZipFile; \
    Expand-Archive -Path $ZipFile -DestinationPath $Destination; \
    Get-ChildItem $Destination;

ENTRYPOINT ["powershell"]