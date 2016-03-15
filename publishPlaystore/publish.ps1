param (
    [string]$jsonFile = $(throw "-jsonFile is required."),
    [string]$apkPath = $(throw "-apkPath is required."),
	[string]$packageName = $(throw "-packageName is required."),
    [string]$locale = $(throw "-locale is required."),
    [string]$message = $(throw "-message is required."),
    [string]$track = $(throw "-track is required.")
)

Add-Type -AssemblyName System.IO.Compression.FileSystem

function Expand-ZipFile()
{
    [CmdletBinding()]
    Param(
        [Parameter(Mandatory = $true,Position = 0)][string]$SourcePath,
        [Parameter(Mandatory = $true,Position = 1)][string]$DestinationPath
    )

    [System.IO.Compression.ZipFile]::ExtractToDirectory($SourcePath, $DestinationPath)
}

echo $packageName;
echo $apkPath

$pythonVersion = "3.5.1"
$pythonFileName = "python-$($pythonVersion)-embed-win32"
$pythonFileNameWithExtension = "$($pythonFileName).zip"

$currentPath = (Get-Item -Path ".\" -Verbose).FullName;

if(Test-Path -Path $pythonFileName)
{
    $path = $currentPath + "\$($pythonFileName)"
}
else
{
    $pythonExists = Get-Command python -ErrorAction SilentlyContinue

    if($pythonExists)
    {
        $currentPythonVersion = [string](python --version 2>&1) -replace "Python ", ""
    }

    if(!$pythonExists -or $currentPythonVersion -lt $pythonVersion)
    {
        echo "Downloading Python $($pythonVersion)"
        $pythonUrl = 'https://www.python.org/ftp/python/{0}/{1}' -f $pythonVersion, $pythonFileNameWithExtension
		$zipPath = $currentPath + '\' + $pythonFileNameWithExtension
        Invoke-WebRequest $pythonUrl -OutFile $zipPath
		
        mkdir $pythonFileName
        
        $zipExtractPath = $currentPath + '\' + $pythonFileName
        Expand-ZIPFile -SourcePath $zipPath -DestinationPath $zipExtractPath
        Rename-Item "$($zipExtractPath)\python35.zip" "python35_.zip"
        mkdir "$($zipExtractPath)\python35.zip"
        Expand-ZIPFile -SourcePath "$($zipExtractPath)\python35_.zip" -DestinationPath "$($zipExtractPath)\python35.zip"

        $path = $currentPath + '\' + $pythonFileName
    }
    else
    {
        $path = Split-Path -parent $pythonExists.Definition
    }
}

$env:path="$env:Path;$path"

$p = "$path\python.exe"

. $p --version

$pip = "$path\scripts\pip.exe"

echo $p
echo $pip

((new-object net.webclient).DownloadString('https://bootstrap.pypa.io/get-pip.py')) | . $p

. $pip install --upgrade google-api-python-client

$uploadApkPath = "$($currentPath)\upload_apks_with_listing.py"

. $p $uploadApkPath $packageName $apkPath -language $locale -jsonFile $jsonFile -message $message -track $track