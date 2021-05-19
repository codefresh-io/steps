FROM mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019

SHELL ["powershell", "-command"]

RUN choco install jdk8 -y

RUN New-Item -Path c:\ -Name ZipFolder -ItemType directory; \
    New-Item -Path c:\ -Name Extracted -ItemType directory; \
    $Url = 'https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip'; \
    $Destination= 'C:\Extracted\'; \
    $ZipFile = 'C:\ZipFolder\' + $(Split-Path -Path $Url -Leaf); \
    Invoke-WebRequest -Uri $Url -OutFile $ZipFile; \
    Expand-Archive -Path $ZipFile -DestinationPath $Destination; \
    Get-ChildItem $Destination;

ENTRYPOINT ["powershell"]