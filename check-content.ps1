param ($url, $noclear)
if ($noclear -ne "true") {
	Clear-Host
}

filter ColorWord2 {
	param($kw )
	$lines = ($_ -split "[\r\n]+")
	Foreach($line in $lines)
	{
		$index = $line.IndexOf($kw, [System.StringComparison]::InvariantCultureIgnoreCase)                            
		while($index -ge 0){
			Write-Host $line.Substring(0,$index) -NoNewline   -ForegroundColor 'DarkGray'    
			Write-Host $line.Substring($index, $kw.Length).Trim() -NoNewline -ForegroundColor 'White' -BackgroundColor 'DarkRed'
			$used =$kw.Length + $index
			$remain = $line.Length - $used
			$line =$line.Substring($used, $remain)
			$index = $line.IndexOf($kw, [System.StringComparison]::InvariantCultureIgnoreCase)
		}
		Write-Host $line -ForegroundColor 'DarkGray'    
	}
}


Write-Host "===================================================================" -ForegroundColor 'White'
Write-Host "=                       HTTP HTMLContent check                    =" -ForegroundColor 'White'
Write-Host "===================================================================" -ForegroundColor 'White'

$Config = Get-Content '.\content-config.json' | Out-String | ConvertFrom-Json


$exp = $Config.Expires -as [datetime] 
$today = Get-Date
Write-Host "Version : ".PadLeft(15) -NoNewline
Write-Host $Config.Version -ForegroundColor 'Green'

Write-Host "Expire : ".PadLeft(15) -NoNewline
Write-Host $exp.ToString('dd/MM/yyyy')  " | " -NoNewline
if($exp -le $today)
{
	Write-Host " Expired !" -ForegroundColor 'Red'
}
else
{
	Write-Host " Valid" -ForegroundColor 'Green'
}


while ($null -eq $url -or $url -eq "") {
	Write-Host ""
	Write-Host "url parameter is not specified."
	$url = Read-Host "Enter url to check (ex. https://www.mysite.com) or 'exit' to terminate this script "
	if ($url -eq "exit") { exit }
}

Write-Host "Checking : ".PadLeft(15) -NoNewline
Write-Host $url -ForegroundColor 'Green'
Write-Host "===================================================================" -ForegroundColor 'White'

if($exp -le $today)
{
	Write-Host " "
	Write-Host " -------------------------------------------" -ForegroundColor 'Red'
	Write-Host " >> Please update 'headers-config.json' file" -ForegroundColor 'Red'
	Write-Host " -------------------------------------------" -ForegroundColor 'Red'
	Write-Host " Last version :" -ForegroundColor 'Yellow'
	Write-Host " https://capgemini.sharepoint.com/:f:/r/sites/CyberSecurityFR2/Shared%20Documents/General/PowerShell%20Scripts?csf=1&web=1&e=0rbJMN" -ForegroundColor 'Yellow'
}

$result = Invoke-webrequest -Uri $url -Method Get -UseBasicParsing



$html = $result.ToString()


Write-Host ""
Write-Host ""
Write-Host "== Important findings =="  -ForegroundColor 'Red'
$hashit = "false"
Foreach($tr in $Config.Errors)
{
	$matchItems =  [regex]::matches($html, $tr.Value)
	Foreach ($mt in $matchItems) 
	{
		$hashit = "true"
		Write-Host $tr.Label -NoNewline
		if($mt.Groups['Keyword'].Value)
		{
			Write-Host " '" -NoNewline
			Write-Host $mt.Groups['Keyword'].Value -NoNewline -ForegroundColor 'Red'
			Write-Host "'" -NoNewline
		}
		Write-Host " : " -NoNewline
		$str = $mt -replace "`n"," " -replace "`r"," " -replace ('\s+', ' ')
		$str = $str.Trim()
		if($mt.Groups['Keyword'].Value)
		{
			"[...]" + $str + "[...]" | ColorWord2 -words $mt.Groups['Keyword'].Value
		}
		else {
			"[...]" + $str + "[...]" | ColorWord2 -words $str 
		}
		Write-Host "     -> " $tr.Description  -ForegroundColor 'DarkGray'
		Write-Host " "
		
	}
}

if($hashit -eq "false")
{
	Write-Host "None  - No action required" -ForegroundColor 'DarkGray'
}

Write-Host ""
Write-Host "== Warning findings =="  -ForegroundColor 'Magenta'
$hashit = "false"
Foreach($tr in $Config.Warnings)
{
	$matchItems =  [regex]::matches($html, $tr.Value)
	Foreach ($mt in $matchItems) 
	{
		$hashit = "true"
		Write-Host $tr.Label -NoNewline
		if($mt.Groups['Keyword'].Value)
		{
			Write-Host " '" -NoNewline
			Write-Host $mt.Groups['Keyword'].Value -NoNewline -ForegroundColor 'Magenta'
			Write-Host "'" -NoNewline
		}		
		Write-Host " : " -NoNewline
		$str = $mt -replace "`n"," " -replace "`r"," " -replace ('\s+', ' ')
		$str = $str.Trim()
		if($mt.Groups['Keyword'].Value)
		{
			"[...]" + $str + "[...]"  | ColorWord2  $mt.Groups['Keyword'].Value
		}
		else {
			"[...]" + $str + "[...]"  | ColorWord2  $str
		}
		Write-Host "     -> " $tr.Description  -ForegroundColor 'DarkGray'
		Write-Host " "
	}
}

if($hashit -eq "false")
{
	Write-Host "None  - No action required" -ForegroundColor 'DarkGray'
}


Write-Host ""
Write-Host ""
Write-Host "--- End  ---" -ForegroundColor 'Green'
if ($PSBoundParameters.Keys.Count -eq 0) {
	write-host "Press any key to continue..."
	[void][System.Console]::ReadKey($true)
}