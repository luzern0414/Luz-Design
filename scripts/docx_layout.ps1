param([string]$In, [string]$Pdf, [string]$Json)
$app = New-Object -ComObject KWPS.Application
$app.Visible = $false
$doc = $app.Documents.Open($In)
$doc.Repaginate()
$result = [ordered]@{ pages = $doc.ComputeStatistics(2); tables = @(); headings = @() }
foreach ($t in $doc.Tables) {
  $rows = @()
  for ($i = 1; $i -le $t.Rows.Count; $i++) { $rows += [int]$t.Rows.Item($i).Range.Information(3) }
  $result.tables += ,$rows
}
foreach ($p in $doc.Paragraphs) {
  $lvl = [int]$p.OutlineLevel
  if ($lvl -ge 1 -and $lvl -le 2) {
    $txt = $p.Range.Text.Trim()
    $result.headings += ,@($lvl, $txt, [int]$p.Range.Information(3))
  }
}
try { $doc.ExportAsFixedFormat($Pdf, 17) } catch { $doc.SaveAs2($Pdf, 17) }
$doc.Close(0)
$app.Quit()
$result | ConvertTo-Json -Depth 5 -Compress | Out-File -Encoding utf8 $Json
