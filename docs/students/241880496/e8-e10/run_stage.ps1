param(
    [Parameter(Mandatory)][string]$Stage,
    [Parameter(Mandatory)][string]$Track
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$sid = (git config --local user.name).Trim()
$image = "course-e8e10:$sid"
docker image inspect $image --format '{{.Id}}' | Out-Null
if ($LASTEXITCODE -ne 0) { throw "missing image $image; run python run_lab.py build first" }

$suffix = -join (1..6 | ForEach-Object { [char]((48..57) + (97..122) | Get-Random) })
$out = "work/$Stage-$Track-manual.$suffix"
if (Test-Path $out) { throw "OUT already exists: $out" }
New-Item -ItemType Directory -Path $out | Out-Null
New-Item -ItemType Directory -Path "$out/steps" | Out-Null
git rev-parse HEAD | Set-Content -Path "$out/student-source-commit.txt" -Encoding ascii
docker image inspect $image --format '{{.Id}}' | Set-Content -Path "$out/environment-image-id.txt" -Encoding ascii
Set-Content -Path "work/last-$Stage-$Track.path" -Value $out -Encoding ascii
Write-Output "仓库=$root"
Write-Output "学号=$sid"
Write-Output "镜像=$image"
Write-Output "OUT=$out"

$utf8 = New-Object System.Text.UTF8Encoding($false)
$seq = 0
foreach ($f in Get-ChildItem -Path "work/_steps/$Stage" -File | Sort-Object Name) {
    $seq++
    $label = "STEP {0:d2} {1}" -f $seq, $f.Name
    Write-Output "=== $label ==="
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $log = "$out/steps/$stamp-{0:d2}.log" -f $seq
    if ($f.Extension -eq '.py') {
        $source = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
        $output = ($source | docker run --rm -i --network none --cap-add SYS_PTRACE -e HOME=/tmp -e PYTHONPATH=/course/labs/e8e10:/app -v "${root}:/course" -w /course $image python3 - $out 2>&1) | Out-String
    }
    else {
        $script = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
        $output = (docker run --rm --network none --cap-add SYS_PTRACE -e HOME=/tmp -e "OUT=$out" -v "${root}:/course" -w /course $image bash -c $script 2>&1) | Out-String
    }
    $code = $LASTEXITCODE
    Write-Output $output.TrimEnd()
    Write-Output "STEP_EXIT_CODE=$code"
    $text = $output.TrimEnd() + "`n" + "STEP_EXIT_CODE=$code" + "`n"
    [System.IO.File]::WriteAllText((Join-Path $root $log), $text, $utf8)
    if ($code -ne 0) {
        Write-Output "STEP_FAILED=$($f.Name)"
        exit $code
    }
}
Write-Output "STAGE_DONE=$Stage-$Track OUT=$out"
