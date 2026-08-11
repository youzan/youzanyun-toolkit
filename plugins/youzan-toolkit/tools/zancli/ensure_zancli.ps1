param(
  [switch]$Check,
  [switch]$PrintPath,
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Command
)

$ErrorActionPreference = "Stop"

$StableVersionUrl = if ($env:ZANCLI_STABLE_VERSION_URL) { $env:ZANCLI_STABLE_VERSION_URL } else { "https://yzy-static.yzcdn.cn/devtools/release/stable.txt" }
$RequiredVersion = if ($env:ZANCLI_REQUIRED_VERSION) { $env:ZANCLI_REQUIRED_VERSION } else { "1.0.18" }

function Write-Stderr {
  param([string]$Message)
  [Console]::Error.WriteLine($Message)
}

function Get-Semver {
  param([string]$Text)
  if ($Text -match "v?(\d+\.\d+\.\d+)") {
    return $Matches[1]
  }
  return ""
}

function Get-TargetVersion {
  try {
    $stable = Get-Semver ((curl.exe -fsSL $StableVersionUrl).Trim())
    if ($stable) {
      return $stable
    }
  } catch {
  }

  $required = Get-Semver $RequiredVersion
  if ($required) {
    return $required
  }
  return $RequiredVersion
}

function Find-Zancli {
  $commands = @("zancli.exe", "zancli")
  foreach ($name in $commands) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) {
      return $cmd.Source
    }
  }

  $candidates = @(
    (Join-Path $HOME "bin\zancli.exe"),
    (Join-Path $HOME "bin\zancli")
  )
  foreach ($candidate in $candidates) {
    if (Test-Path -Path $candidate -PathType Leaf) {
      return $candidate
    }
  }
  return $null
}

function Get-ZancliVersion {
  param([string]$Binary)
  if (-not $Binary) {
    return ""
  }

  foreach ($arg in @("--version", "version")) {
    try {
      $output = & $Binary $arg 2>$null
      $version = Get-Semver ($output -join "`n")
      if ($version) {
        return $version
      }
    } catch {
    }
  }
  return ""
}

function Install-Zancli {
  param([string]$Version)

  if ($env:PROCESSOR_ARCHITECTURE -notin @("AMD64", "x86_64") -and $env:PROCESSOR_ARCHITEW6432 -notin @("AMD64", "x86_64")) {
    throw "unsupported Windows architecture: $env:PROCESSOR_ARCHITECTURE; only AMD64 is available"
  }

  $installDir = Join-Path $HOME "bin"
  New-Item -ItemType Directory -Force -Path $installDir | Out-Null
  $output = Join-Path $installDir "zancli.exe"
  $url = "https://yzy-static.yzcdn.cn/devtools/release/v$Version/bin/windows/amd64/zancli.exe"

  Write-Stderr "Installing zancli $Version for Windows AMD64..."
  curl.exe -fL $url -o $output

  $env:Path = "$installDir;$env:Path"
  $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
  if (-not ($userPath -split ";" | Where-Object { $_ -eq $installDir })) {
    [Environment]::SetEnvironmentVariable("Path", "$installDir;$userPath", "User")
  }

  return $output
}

function Ensure-Zancli {
  $target = Get-TargetVersion
  $binary = Find-Zancli
  $current = Get-ZancliVersion $binary

  if ($binary -and $current -eq $target) {
    return $binary
  }

  if ($binary -and $current) {
    Write-Stderr "zancli $current does not match stable $target; installing stable..."
  } elseif ($binary) {
    Write-Stderr "zancli version cannot be detected; reinstalling stable $target..."
  }

  $binary = Install-Zancli $target
  $current = Get-ZancliVersion $binary
  if ($current -ne $target) {
    if ($current) {
      throw "zancli version is $current after installation, expected $target."
    }
    throw "zancli version cannot be detected after installation, expected $target."
  }
  return $binary
}

function Verify-Login {
  param(
    [string]$Binary,
    [bool]$CheckOnly
  )

  & $Binary whoami
  if ($LASTEXITCODE -eq 0) {
    Write-Stderr "zancli login verified."
    return 0
  }

  if ($CheckOnly) {
    Write-Stderr "zancli is not logged in. Run zancli login and try again."
    return $(if ($LASTEXITCODE) { $LASTEXITCODE } else { 1 })
  }

  Write-Stderr "zancli login is required. Complete the browser OAuth flow to continue."
  & $Binary login
  if ($LASTEXITCODE -ne 0) {
    return $LASTEXITCODE
  }

  & $Binary whoami
  if ($LASTEXITCODE -eq 0) {
    Write-Stderr "zancli login verified."
    return 0
  }
  return $(if ($LASTEXITCODE) { $LASTEXITCODE } else { 1 })
}

$binary = Ensure-Zancli
if ($PrintPath) {
  Write-Output $binary
}

if ($Check) {
  exit (Verify-Login $binary $true)
}

if ($Command -and $Command.Count -gt 0) {
  if ($Command[0] -eq "--") {
    if ($Command.Count -gt 1) {
      $Command = $Command[1..($Command.Count - 1)]
    } else {
      $Command = @()
    }
  }

  if ($Command.Count -gt 0) {
    $loginStatus = Verify-Login $binary $false
    if ($loginStatus -ne 0) {
      exit $loginStatus
    }

    if ([System.IO.Path]::GetFileName($Command[0]).ToLowerInvariant() -in @("zancli", "zancli.exe")) {
      $Command[0] = $binary
    }
    $env:Path = "$(Split-Path -Parent $binary);$env:Path"
    & $Command[0] @($Command | Select-Object -Skip 1)
    exit $LASTEXITCODE
  }
}

exit (Verify-Login $binary $false)
