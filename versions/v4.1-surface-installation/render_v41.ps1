$ErrorActionPreference = 'Stop'
$slopeRoot = $PSScriptRoot
$slopeQa = Join-Path $slopeRoot '_qa/render'
New-Item -ItemType Directory -Force -Path $slopeQa | Out-Null
$slopeWord = New-Object -ComObject Word.Application
$slopeWord.Visible = $false
$slopeWord.DisplayAlerts = 0
try {
  $slopeFile = Get-Item -LiteralPath (Join-Path $slopeRoot '边坡类型表面防护与贴附光纤试验方案.docx')
  $slopeDoc = $null
  try {
    $slopeDoc = $slopeWord.Documents.Open($slopeFile.FullName, $false, $true, $false)
    $slopeDoc.Repaginate()
    $slopePdf = Join-Path $slopeQa 'report.pdf'
    $slopeDoc.ExportAsFixedFormat($slopePdf, 17)
    [pscustomobject]@{file=$slopeFile.Name;pages=$slopeDoc.ComputeStatistics(2);pdf=$slopePdf} | ConvertTo-Json -Compress
  } finally { if ($null -ne $slopeDoc) { $slopeDoc.Close(0) } }
} finally { $slopeWord.Quit() }
