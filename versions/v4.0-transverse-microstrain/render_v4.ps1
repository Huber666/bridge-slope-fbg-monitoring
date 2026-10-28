param([string]$DocumentFilter = '0*.docx')
$ErrorActionPreference = 'Stop'
$v4Root = $PSScriptRoot
$v4Qa = Join-Path $v4Root '_qa/word_render'
New-Item -ItemType Directory -Force -Path $v4Qa | Out-Null
$v4Word = New-Object -ComObject Word.Application
$v4Word.Visible = $false
$v4Word.DisplayAlerts = 0
try {
  foreach ($v4File in Get-ChildItem -LiteralPath $v4Root -Filter $DocumentFilter | Sort-Object Name) {
    $v4Doc = $null
    try {
      $v4Doc = $v4Word.Documents.Open($v4File.FullName, $false, $true, $false)
      $v4Doc.Repaginate()
      $v4Pdf = Join-Path $v4Qa ($v4File.BaseName + '.pdf')
      $v4Doc.ExportAsFixedFormat($v4Pdf, 17)
      [pscustomobject]@{file=$v4File.Name;pages=$v4Doc.ComputeStatistics(2);pdf=$v4Pdf} | ConvertTo-Json -Compress
    } finally { if ($null -ne $v4Doc) { $v4Doc.Close(0) } }
  }
} finally { $v4Word.Quit() }
