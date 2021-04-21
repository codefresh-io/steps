FROM mcr.microsoft.com/windows/servercore:1809

RUN powershell -Command "$Url = 'https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/5.2.0.29862/sonar-scanner-msbuild-5.2.0.29862-net46.zip'; \
      $ZipFile = 'C:\ZipFolder\' + $(Split-Path -Path $Url -Leaf); \
      $Destination= 'C:\SonarSource\';  \
      Invoke-WebRequest -Uri $Url -OutFile $ZipFile; \
      $ExtractShell = New-Object -ComObject Shell.Application;\
      $Files = $ExtractShell.Namespace($ZipFile).Items();\
      $ExtractShell.NameSpace($Destination).CopyHere($Files); \
      Start-Process $Destination;"