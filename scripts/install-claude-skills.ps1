[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir '..')
$SkillsSrc = Join-Path $RepoRoot 'skills'
$SkillsDst = Join-Path $RepoRoot '.claude\skills'
$AgentLabel = 'Claude Code'

if (-not (Test-Path $SkillsSrc)) {
    Write-Error "No se encontro la carpeta de skills en: $SkillsSrc"
    exit 1
}

if (-not (Test-Path $SkillsDst)) {
    New-Item -ItemType Directory -Path $SkillsDst -Force | Out-Null
    Write-Host "Creada carpeta destino para ${AgentLabel}: $SkillsDst"
}

function Get-DirHash {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    $files = Get-ChildItem -Path $Path -Recurse -File | Sort-Object FullName
    if (-not $files) { return '' }
    $sb = New-Object System.Text.StringBuilder
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($Path.Length).TrimStart('\','/')
        $h = (Get-FileHash -Path $f.FullName -Algorithm SHA256).Hash
        [void]$sb.AppendLine("$rel|$h")
    }
    return $sb.ToString()
}

$skillDirs = Get-ChildItem -Path $SkillsSrc -Directory
if (-not $skillDirs) {
    Write-Warning "No hay skills para instalar en $SkillsSrc"
    exit 0
}

foreach ($skill in $skillDirs) {
    $srcPath = $skill.FullName
    $dstPath = Join-Path $SkillsDst $skill.Name

    $srcHash = Get-DirHash -Path $srcPath
    $dstHash = Get-DirHash -Path $dstPath

    if ((Test-Path $dstPath) -and ($srcHash -eq $dstHash)) {
        Write-Host "[skip] $($skill.Name): ya esta instalada y al dia."
        continue
    }

    if ((Test-Path $dstPath) -and -not $Force) {
        Write-Warning "[advertencia] $($skill.Name): ya existe en destino con contenido diferente. Usa -Force para sobrescribir."
        continue
    }

    if (Test-Path $dstPath) {
        Remove-Item -Path $dstPath -Recurse -Force
        Write-Host "[sobrescribiendo] $($skill.Name) en ${AgentLabel}"
    }

    Copy-Item -Path $srcPath -Destination $dstPath -Recurse -Force
    Write-Host "[instalada] $($skill.Name) -> $dstPath"
}

Write-Host ""
Write-Host "Instalacion de skills para ${AgentLabel} completada en: $SkillsDst"
