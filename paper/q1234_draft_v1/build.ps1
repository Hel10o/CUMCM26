param([switch]$BodyOnly)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
        throw 'TeX Live with latexmk and XeLaTeX is required.'
    }
    New-Item -ItemType Directory -Force -Path 'build' | Out-Null
    $paperSource = if ($BodyOnly) { 'body_preview.tex' } else { 'main.tex' }
    & latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build $paperSource
    if ($LASTEXITCODE -ne 0) { throw 'Paper compilation failed.' }
    if (-not $BodyOnly) {
        & latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build ai_details.tex
        if ($LASTEXITCODE -ne 0) { throw 'AI details compilation failed.' }
        Copy-Item -LiteralPath 'build/main.pdf' -Destination '四问论文初稿_v1.pdf' -Force
        Copy-Item -LiteralPath 'build/ai_details.pdf' -Destination 'AI工具使用详情.pdf' -Force
    }
} finally { Pop-Location }
