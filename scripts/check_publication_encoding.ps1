param(
    [string]$ArticlePath = "docs/publications/articles"
)

$ErrorActionPreference = "Stop"
$repo = (Get-Location).Path
$target = Join-Path $repo $ArticlePath
if (-not (Test-Path -LiteralPath $target)) { throw "Publication path not found: $target" }

$files = if ((Get-Item -LiteralPath $target).PSIsContainer) {
    Get-ChildItem -LiteralPath $target -Filter *.md -File
} else {
    @(Get-Item -LiteralPath $target)
}

$failures = @()
foreach ($file in $files) {
    $bytes = [IO.File]::ReadAllBytes($file.FullName)
    try {
        $utf8 = New-Object Text.UTF8Encoding($false, $true)
        $text = $utf8.GetString($bytes)
    } catch {
        $failures += "$($file.Name): invalid UTF-8"
        continue
    }
    if (-not $text.StartsWith("---`r`n") -and -not $text.StartsWith("---`n")) {
        $failures += "$($file.Name): YAML front matter must begin at byte 1"
    }
    if ($text -match 'Ã|Â|â|�|ƒ') {
        $failures += "$($file.Name): mojibake character detected"
    }
}

if ($failures.Count) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}
Write-Output "Publication encoding check passed for $($files.Count) Markdown file(s)."
