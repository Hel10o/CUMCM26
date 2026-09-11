param([switch]$RefreshAssets)
$ErrorActionPreference = 'Stop'
$paperDirectory = $PSScriptRoot
$projectDirectory = Split-Path (Split-Path $paperDirectory -Parent) -Parent
$assetPython = Join-Path $projectDirectory 'review_q1_20260910/.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $assetPython)) {
    throw '未找到项目科学 Python；请在含 NumPy、Matplotlib、pypdf 的环境中运行构建和校验脚本。'
}
if ($RefreshAssets) {
    & $assetPython -X utf8 -B (Join-Path $paperDirectory 'build_q2_assets.py')
    if ($LASTEXITCODE -ne 0) { throw '第二问图表生成失败。' }
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
    Copy-Item -LiteralPath 'build/main.pdf' -Destination '第一二问论文阶段稿.pdf' -Force
    & $assetPython -X utf8 -B (Join-Path $paperDirectory 'validate_paper.py')
    if ($LASTEXITCODE -ne 0) { throw 'PDF 内容核验失败，请查看检查输出。' }
    Write-Output (Join-Path $paperDirectory '第一二问论文阶段稿.pdf')
} finally {
    Pop-Location
}
