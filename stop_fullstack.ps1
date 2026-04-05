$ErrorActionPreference = "SilentlyContinue"

$ports = @(3000, 8000)
$killed = @()

foreach ($port in $ports) {
  $lines = netstat -ano | Select-String ":$port\s"
  foreach ($line in $lines) {
    $parts = ($line -split "\s+") | Where-Object { $_ -ne "" }
    if ($parts.Count -gt 0) {
      $pid = $parts[-1]
      if ($pid -match "^\d+$" -and $pid -ne "0") {
        Stop-Process -Id $pid -Force
        $killed += "$pid (port $port)"
      }
    }
  }
}

if ($killed.Count -eq 0) {
  Write-Host "No PathMind server process found on ports 3000/8000."
} else {
  $unique = $killed | Sort-Object -Unique
  Write-Host "Stopped process IDs:"
  $unique | ForEach-Object { Write-Host " - $_" }
}
