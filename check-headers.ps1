param ($url,$noclear)
if($noclear -ne "true")
{
	Clear-Host
}

Write-Host "===================================================================" -ForegroundColor 'White'
Write-Host "=                       HTTP Headers check                        =" -ForegroundColor 'White'
Write-Host "===================================================================" -ForegroundColor 'White'
while($null -eq $url -or $url -eq "")
{
   	Write-Host ""
    Write-Host "url parameter is not specified."
    $url = Read-Host "Enter url to check (ex. https://www.mysite.com) or 'exit' to terminate this script "
    if($url -eq "exit") {exit}
}


try {
	$r = Invoke-WebRequest $url	-Headers @{"Cache-Control"="no-cache"}
}
catch {
	Write-Host "-------------------------------------------" -ForegroundColor 'Red'
	Write-Host " Error while requesting url " $url -ForegroundColor 'Red'
	Write-Host " >> " -ForegroundColor 'Red' -NoNewline
	Write-Host $_.Exception.Message  -ForegroundColor 'Red'
	Write-Host "-------------------------------------------" -ForegroundColor 'Red'
	exit
}

$Config = Get-Content '.\headers-config.json' | Out-String | ConvertFrom-Json

$exp = $Config.Expires -as [datetime] 
$today = Get-Date
Write-Host " "
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

Write-Host "Checking : ".PadLeft(15) -NoNewline
Write-Host $url -ForegroundColor 'Green'

if($exp -le $today)
{
	Write-Host " "
	Write-Host " -------------------------------------------" -ForegroundColor 'Red'
	Write-Host " >> Please update 'headers-config.json' file" -ForegroundColor 'Red'
	Write-Host " -------------------------------------------" -ForegroundColor 'Red'
	Write-Host " Last version :" -ForegroundColor 'Yellow'
	Write-Host " https://capgemini.sharepoint.com/:f:/r/sites/CyberSecurityFR2/Shared%20Documents/General/PowerShell%20Scripts?csf=1&web=1&e=0rbJMN" -ForegroundColor 'Yellow'
}

Write-Host ""
Write-Host "===================================================================" -ForegroundColor 'White'
Write-Host "=                            Raw view                             =" -ForegroundColor 'White'
Write-Host "===================================================================" -ForegroundColor 'White'
Write-Host ""
Foreach($h in $r.Headers.Keys)
{
	Write-Host $h ": " -NoNewline -ForegroundColor 'White'
	Write-Host $r.Headers[$h]  -ForegroundColor 'DarkGray'
}
Write-Host ""

Write-Host ""
Write-Host "===================================================================" -ForegroundColor 'White' -BackgroundColor 'DarkGreen'
Write-Host "=                        Consider to ADD Header                   =" -ForegroundColor 'White' -BackgroundColor 'DarkGreen'
Write-Host "===================================================================" -ForegroundColor 'White' -BackgroundColor 'DarkGreen'

$hashit = "false"
Foreach($ha in $Config.ToVerify)
{
	$present = "false"
	Foreach($h in $r.Headers.Keys)
	{
		if($ha.name -eq $h)
		{
			$present = "true"
		}
	}
	if($present -eq "false")
	{
		$hashit = "true"
		Write-Host ""
		Write-Host $ha.Name -ForegroundColor 'White' -BackgroundColor 'DarkGreen'

		Foreach($ms in $ha.RequiredValues)
		{
				Write-Host "Required : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
				Write-Host $ms.Label -ForegroundColor 'Red'
				if($ms.Description -ne "")
				{
					Write-Host " ".PadLeft(20) -NoNewline -ForegroundColor 'DarkGray'
					Write-Host $ms.Description -ForegroundColor 'DarkGray'
				}
				if ($ms.Links -ne "") {
					$splittedLinks = $ms.Links.Split("|")
					Write-Host "See : ".PadLeft(26) -NoNewline -ForegroundColor 'DarkGray'
					$firstlink = $true
					Foreach ($url in $splittedLinks) {
						if($firstlink -ne $true) {Write-Host "".PadLeft(26) -NoNewline}
						Write-Host $url -ForegroundColor 'DarkGray'
						$firstlink = $false
					}		
				}
		}

		Foreach($rv in $ha.RecommandedValues)
		{
			$hashit = "true"
			Write-Host "Recommanded : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
			Write-Host $rv.Label -ForegroundColor 'Magenta'			
			if($rv.Description -ne "")
			{
				Write-Host " ".PadLeft(20) -NoNewline -ForegroundColor 'DarkGray'
				Write-Host $rv.Description -ForegroundColor 'DarkGray'
			}
			if ($rv.Links -ne "") {
				$splittedLinks = $rv.Links.Split("|")
				Write-Host "See : ".PadLeft(26) -NoNewline -ForegroundColor 'DarkGray'
				$firstlink = $true
				Foreach ($url in $splittedLinks) {
					if($firstlink -ne $true) {Write-Host "".PadLeft(26) -NoNewline}
					Write-Host $url -ForegroundColor 'DarkGray'
					$firstlink = $false
				}		
			}
		}
		Write-Host " "
		Write-Host "Suggested : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
		Write-Host $ha.SuggestedValue  -ForegroundColor 'DarkGray'
	}
}
if($hashit -eq "false")
{
	Write-Host "None - No action required" -ForegroundColor 'DarkGray'
}

Write-Host ""
Write-Host ""
Write-Host "==================================================================="  -ForegroundColor 'White' -BackgroundColor 'DarkCyan'
Write-Host "=                       Consider to VERIFY Value                  ="  -ForegroundColor 'White' -BackgroundColor 'DarkCyan'
Write-Host "==================================================================="  -ForegroundColor 'White' -BackgroundColor 'DarkCyan'
$hashit = "false"
$nothingToWrite = "true"
Foreach($ha in $Config.ToVerify)
{
	$present = "false"
	Foreach($h in $r.Headers.Keys)
	{
		if($ha.name -eq $h)
		{
			$present = "true"
			$Actualvalue = $r.Headers[$h]
		}
	}
	$hashit = "false"
	if($present -eq "true")
	{
		$nothingToWrite = "false"
		Write-Host ""
		Write-Host $ha.name -ForegroundColor 'White' -BackgroundColor 'DarkCyan'
		Write-Host "Actual : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
		Write-Host $r.Headers[$ha.name]  -ForegroundColor 'Yellow'
		
		Foreach($ms in $ha.RequiredValues)
		{
			if($Actualvalue -notmatch $ms.Value)
			{
				$hashit = "true"
				Write-Host "Required : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
				Write-Host $ms.Label -ForegroundColor 'Red'
				if($ms.Description -ne "")
				{
					Write-Host " ".PadLeft(20) -NoNewline -ForegroundColor 'DarkGray'
					Write-Host $ms.Description -ForegroundColor 'DarkGray'
				}
				if ($ms.Links -ne "") {
					$splittedLinks = $ms.Links.Split("|")
					Write-Host "See : ".PadLeft(26) -NoNewline -ForegroundColor 'DarkGray'
					$firstlink = $true
					Foreach ($url in $splittedLinks) {
						if($firstlink -ne $true) {Write-Host "".PadLeft(26) -NoNewline}
						Write-Host $url -ForegroundColor 'DarkGray'
						$firstlink = $false
					}		
				}
			}
		}
		Foreach($fv in $ha.ForbidenValues)
		{
			if($Actualvalue -match $fv.Value)
			{
				$hashit = "true"
				Write-Host "Forbiden : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
				Write-Host $fv.Label -ForegroundColor 'Red'
				if($fv.Description -ne "")
				{
					Write-Host " ".PadLeft(20) -NoNewline -ForegroundColor 'DarkGray'
					Write-Host $fv.Description -ForegroundColor 'DarkGray'
				}
				if ($fv.Links -ne "") {
					$splittedLinks = $fv.Links.Split("|")
					Write-Host "See : ".PadLeft(26) -NoNewline -ForegroundColor 'DarkGray'
					$firstlink = $true
					Foreach ($url in $splittedLinks) {
						if($firstlink -ne $true) {Write-Host "".PadLeft(26) -NoNewline}
						Write-Host $url -ForegroundColor 'DarkGray'
						$firstlink = $false
					}		
				}
			}
		}

		Foreach($rv in $ha.RecommandedValues)
		{
			if($Actualvalue -notmatch $rv.Value)
			{
				$hashit = "true"
				Write-Host "Recommanded : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
				Write-Host $rv.Label -ForegroundColor 'Magenta'			
				if($rv.Description -ne "")
				{
					Write-Host " ".PadLeft(20) -NoNewline -ForegroundColor 'DarkGray'
					Write-Host $rv.Description -ForegroundColor 'DarkGray'
				}
				if ($rv.Links -ne "") {
					$splittedLinks = $rv.Links.Split("|")
					Write-Host "See : ".PadLeft(26) -NoNewline -ForegroundColor 'DarkGray'
					$firstlink = $true
					Foreach ($url in $splittedLinks) {
						if($firstlink -ne $true) {Write-Host "".PadLeft(26) -NoNewline}
						Write-Host $url -ForegroundColor 'DarkGray'
						$firstlink = $false
					}		
				}
			}
		}

		Foreach($nrv in $ha.NotRecommandedValues)
		{
			if($Actualvalue -match $nrv.Value)
			{
				$hashit = "true"
				Write-Host "Not recommanded : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
				Write-Host $nrv.Label -ForegroundColor 'Magenta'
				if($nrv.Description -ne "")
				{
					Write-Host " ".PadLeft(20) -NoNewline -ForegroundColor 'DarkGray'
					Write-Host $nrv.Description -ForegroundColor 'DarkGray'
				}
				if ($nrv.Links -ne "") {
					$splittedLinks = $nrv.Links.Split("|")
					Write-Host "See : ".PadLeft(26) -NoNewline -ForegroundColor 'DarkGray'
					$firstlink = $true
					Foreach ($url in $splittedLinks) {
						if($firstlink -ne $true) {Write-Host "".PadLeft(26) -NoNewline}
						Write-Host $url -ForegroundColor 'DarkGray'
						$firstlink = $false
					}		
				}
			}
		}
		
		Foreach($wrnv in $ha.Warnings)
		{
			if($Actualvalue -match $wrnv.Value)
			{
				$hashit = "true"
				Write-Host "Warning : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
				Write-Host $wrnv.Label -ForegroundColor 'DarkYellow' 
				if($wrnv.Description -ne "")
				{
					Write-Host " ".PadLeft(20) -NoNewline -ForegroundColor 'DarkGray'
					Write-Host $wrnv.Description -ForegroundColor 'DarkGray'
				}
				if ($wrnv.Links -ne "") {
					$splittedLinks = $wrnv.Links.Split("|")
					Write-Host "See : ".PadLeft(26) -NoNewline -ForegroundColor 'DarkGray'
					$firstlink = $true
					Foreach ($url in $splittedLinks) {
						if($firstlink -ne $true) {Write-Host "".PadLeft(26) -NoNewline}
						Write-Host $url -ForegroundColor 'DarkGray'
						$firstlink = $false
					}		
				}
			}
		}

		if($hashit -eq "false")
		{
			Write-Host "Status : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
			Write-Host "Ok - No action required" -ForegroundColor 'Green'
		}
		else
		{
			Write-Host " "
			Write-Host "Suggested : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
			Write-Host $ha.SuggestedValue  -ForegroundColor 'DarkGray'
		}
	}
}

if($nothingToWrite -eq "true")
{
	Write-Host "None." -ForegroundColor 'DarkGray'
}

Write-Host ""
Write-Host ""
Write-Host "==================================================================="  -ForegroundColor 'White' -BackgroundColor 'DarkRed'
Write-Host "=                       Consider to REMOVE Header                 ="  -ForegroundColor 'White' -BackgroundColor 'DarkRed'
Write-Host "==================================================================="  -ForegroundColor 'White' -BackgroundColor 'DarkRed'
$hashit = "false"
Foreach($hr in $Config.ToRemove)
{
	$present = "false"
	Foreach($h in $r.Headers.Keys)
	{
		if($hr.Name -eq $h)
		{
			$present = "true"
		}
	}
	if($present -eq "true")
	{
		$hashit = "true"
		Write-Host ""
		Write-Host $hr.Name -ForegroundColor 'White' -BackgroundColor 'DarkRed'
		Write-Host "Actual : ".PadLeft(20) -NoNewline -ForegroundColor 'White'
		Write-Host $r.Headers[$hr.name]  -ForegroundColor 'Yellow'
		if($hr.Description -ne "")
		{
			Write-Host " ".PadLeft(20) -NoNewline -ForegroundColor 'DarkGray'
			Write-Host $hr.Description -ForegroundColor 'DarkGray'
		}

		if ($hr.Links -ne "") {
			$splittedLinks = $hr.Links.Split("|")
			Write-Host "See : ".PadLeft(26) -NoNewline -ForegroundColor 'DarkGray'
			$firstlink = $true
			Foreach ($url in $splittedLinks) {
				if($firstlink -ne $true) {Write-Host "".PadLeft(26) -NoNewline}
				Write-Host $url -ForegroundColor 'DarkGray'
				$firstlink = $false
			}		
		}

	}
}

if($hashit -eq "false")
{
	Write-Host "None - No action required"  -ForegroundColor 'DarkGray'
}

Write-Host ""
Write-Host ""
Write-Host "--- End ---" -ForegroundColor 'Green'

if($PSBoundParameters.Keys.Count -eq 0)
{
	write-host "Press any key to continue..."
	[void][System.Console]::ReadKey($true)
}