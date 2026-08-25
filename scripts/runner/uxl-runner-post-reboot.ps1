$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$logPath = Join-Path $PSScriptRoot 'uxl-runner-post-reboot.log'
$dockerRoot = Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop'
$dockerDesktop = Join-Path $dockerRoot 'Docker Desktop.exe'
$dockerCli = Join-Path $dockerRoot 'resources\bin\docker.exe'
$distro = 'Ubuntu-24.04'
$runnerUser = 'uxlrunner'

function Invoke-WslRoot {
  param([Parameter(Mandatory)][string]$Command)
  & wsl.exe -d $distro -u root -- bash -lc $Command
  if ($LASTEXITCODE -ne 0) {
    throw "WSL root command failed with exit code $LASTEXITCODE"
  }
}

Start-Transcript -LiteralPath $logPath -Append
try {
  Write-Output '=== UXL post-reboot prerequisite setup ==='
  Get-Date -Format o

  wsl.exe --set-default-version 2
  if ($LASTEXITCODE -ne 0) { throw 'Could not set WSL default version to 2.' }

  & ubuntu2404.exe install --root
  if ($LASTEXITCODE -ne 0) { throw 'Ubuntu 24.04 initialization failed.' }

  wsl.exe --set-version $distro 2
  if ($LASTEXITCODE -ne 0) { throw 'Ubuntu 24.04 could not be set to WSL2.' }
  wsl.exe --set-default $distro
  if ($LASTEXITCODE -ne 0) { throw 'Ubuntu 24.04 could not be set as the default distribution.' }

  Invoke-WslRoot 'export DEBIAN_FRONTEND=noninteractive; apt-get update; apt-get install -y ca-certificates curl gpg wget git python3 python3-venv python3-pip pciutils clinfo'

  Invoke-WslRoot "id -u $runnerUser >/dev/null 2>&1 || useradd --create-home --shell /bin/bash $runnerUser; install -d -m 0750 -o $runnerUser -g $runnerUser /home/$runnerUser/uxl-runner"
  & ubuntu2404.exe config --default-user $runnerUser
  if ($LASTEXITCODE -ne 0) { throw 'Could not set the dedicated WSL default user.' }

  Invoke-WslRoot "install -d -m 0755 /usr/share/keyrings; wget -qO- https://repositories.intel.com/gpu/intel-graphics.key | gpg --yes --dearmor --output /usr/share/keyrings/intel-graphics.gpg; printf '%s\n' 'deb [arch=amd64 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu noble client' > /etc/apt/sources.list.d/intel-gpu-noble.list"
  Invoke-WslRoot 'wget -qO- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --yes --dearmor --output /usr/share/keyrings/oneapi-archive-keyring.gpg; printf "%s\n" "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" > /etc/apt/sources.list.d/oneAPI.list'
  Invoke-WslRoot 'export DEBIAN_FRONTEND=noninteractive; apt-get update; apt-get install -y libze1 intel-level-zero-gpu intel-opencl-icd libze-dev intel-ocloc intel-oneapi-compiler-dpcpp-cpp'

  Invoke-WslRoot "getent group render >/dev/null && usermod -aG render $runnerUser || true; getent group video >/dev/null && usermod -aG video $runnerUser || true"

  wsl.exe --shutdown
  Start-Sleep -Seconds 3

  Write-Output '=== WSL qualification evidence ==='
  wsl.exe -d $distro -- bash -lc 'uname -a; cat /etc/os-release; id; ls -l /dev/dxg /dev/dri 2>/dev/null || true; python3 --version; git --version'
  Write-Output '=== OpenCL enumeration ==='
  wsl.exe -d $distro -- bash -lc 'clinfo --list 2>&1 || true'
  Write-Output '=== SYCL enumeration ==='
  wsl.exe -d $distro -- bash -lc 'source /opt/intel/oneapi/setvars.sh >/dev/null 2>&1; sycl-ls 2>&1 || true'

  $wslWorkspace = (& wsl.exe -d $distro -- wslpath -a $PSScriptRoot).Trim()
  Write-Output '=== SYCL smoke test ==='
  wsl.exe -d $distro -- bash -lc "source /opt/intel/oneapi/setvars.sh >/dev/null 2>&1; ONEAPI_DEVICE_SELECTOR=level_zero:gpu icpx -fsycl '$wslWorkspace/uxl-sycl-smoke.cpp' -o /tmp/uxl-sycl-smoke && ONEAPI_DEVICE_SELECTOR=level_zero:gpu /tmp/uxl-sycl-smoke"
  Write-Output "SYCL smoke exit code: $LASTEXITCODE"

  Write-Output '=== Docker Desktop startup ==='
  if (-not (Test-Path -LiteralPath $dockerDesktop)) { throw 'Docker Desktop executable is missing.' }
  Start-Process -FilePath $dockerDesktop -WindowStyle Hidden

  $dockerReady = $false
  for ($attempt = 1; $attempt -le 60; $attempt++) {
    & $dockerCli info *> $null
    if ($LASTEXITCODE -eq 0) {
      $dockerReady = $true
      break
    }
    Start-Sleep -Seconds 5
  }
  if (-not $dockerReady) { throw 'Docker Desktop did not become ready within five minutes.' }

  & $dockerCli version
  & $dockerCli compose version
  & $dockerCli run --rm hello-world

  Write-Output '=== Docker integration inside Ubuntu ==='
  wsl.exe -d $distro -- bash -lc 'docker version; docker compose version'
  Write-Output "Docker-in-WSL exit code: $LASTEXITCODE"

  Write-Output '=== WSL Intel GPU container boundary probe ==='
  & $dockerCli run --rm --device /dev/dxg:/dev/dxg ubuntu:24.04 bash -lc 'ls -l /dev/dxg'
  Write-Output "Docker /dev/dxg probe exit code: $LASTEXITCODE"

  Write-Output '=== POST_REBOOT_SETUP_COMPLETE ==='
}
catch {
  Write-Error $_
  Write-Output '=== POST_REBOOT_SETUP_FAILED ==='
}
finally {
  Stop-Transcript
}
