FROM mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019

SHELL ["powershell", "-command"]

# Install Chocolatey and JAVA package
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

RUN choco install jdk8 -y

# Install Sonarqube Windows Scanner

RUN New-Item -Path c:\ -Name ZipFolder -ItemType directory; \
    New-Item -Path c:\ -Name Extracted -ItemType directory; \
    $Url = 'https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip'; \
    $Destination= 'C:\Extracted\'; \
    $ZipFile = 'C:\ZipFolder\' + $(Split-Path -Path $Url -Leaf); \
    Invoke-WebRequest -Uri $Url -OutFile $ZipFile; \
    Expand-Archive -Path $ZipFile -DestinationPath $Destination; \
    Get-ChildItem $Destination;

ENTRYPOINT ["powershell"]