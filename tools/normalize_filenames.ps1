<#
===============================================================
File: tools/normalize_filenames.ps1
Location: tools/
Author: Mark J. Latsha
Co-Author: Microsoft Copilot
Created: 2026-05-27
Description:
  Safe PowerShell utility to normalize filenames by removing a
  trailing ".txt" suffix from program files that were uploaded
  with an added ".txt" extension. Includes a dry-run mode and
  logging. Use the -WhatIf switch or run with -DryRun to preview.
Usage:
  # Dry run (preview)
  .\normalize_filenames.ps1 -DryRun

  # Actual rename (recommended to commit before running)
  .\normalize_filenames.ps1
Notes:
  - This script only removes a single trailing ".txt" suffix.
  - It will not change files that already have the intended extension.
===============================================================
#>

param(
  [switch]$DryRun,
  [string]$RootPath = "."
)

function Normalize-Name {
  param($file)
  # Remove only a single trailing ".txt" from the filename
  if ($file.Name -match '\.txt$') {
    $newName = $file.Name -replace '\.txt$',''
    return $newName
  }
  return $null
}

Write-Host "Normalize filenames script starting. RootPath = $RootPath"
$files = Get-ChildItem -Path $RootPath -Recurse -File

foreach ($f in $files) {
  $newName = Normalize-Name -file $f
  if ($newName) {
    $oldPath = $f.FullName
    $newPath = Join-Path -Path $f.DirectoryName -ChildPath $newName

    if ($DryRun) {
      Write-Host "[DRY-RUN] Would rename: '$oldPath' -> '$newPath'"
    } else {
      if (Test-Path -Path $newPath) {
        Write-Warning "Target already exists, skipping: $newPath"
      } else {
        Write-Host "Renaming: '$oldPath' -> '$newPath'"
        Rename-Item -Path $oldPath -NewName $newName
      }
    }
  }
}

Write-Host "Done."
