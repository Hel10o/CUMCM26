param([switch]$RefreshAssets)
$ErrorActionPreference = 'Stop'
$paperDirectory = $PSScriptRoot
if ($RefreshAssets) {
    $assetPython = Join-Path (Split-Path $paperDirectory -Parent) 'review_q1_20260910/.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $assetPython)) { throw '请使用含 NumPy 和 Matplotlib 的 Python 运行 paper/build_assets.py。' }
    & $assetPython (Join-Path $paperDirectory 'build_assets.py')
    if ($LASTEXITCODE -ne 0) { throw '图表生成失败。' }
}
$latexCommand = Get-Command latexmk -ErrorAction Stop
Push-Location -LiteralPath $paperDirectory
try {
    & $latexCommand.Source -norc -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
    if ($LASTEXITCODE -ne 0) { throw 'LaTeX 编译失败，请查看 build/main.log。' }
    $compilationLog = Get-Content -LiteralPath 'build/main.log' -Raw -Encoding UTF8
    if ($compilationLog -match 'Overfull \\[hv]box|There were undefined references|LaTeX Warning: (Reference|Citation).+undefined|Missing character:') {
        throw '编译后仍有越界、缺字或未解析引用，请查看 build/main.log。'
    }
    Copy-Item -LiteralPath 'build/main.pdf' -Destination '第一问论文阶段稿.pdf' -Force
    Write-Output (Join-Path $paperDirectory '第一问论文阶段稿.pdf')
} finally {
    Pop-Location
}
