@echo off
pushd "%~dp0"

if not exist logs mkdir logs

echo ======================================================================
echo INICIANDO ATUALIZACAO AUTOMATICA - CATEGORIAS DIGITAL
echo ======================================================================

echo [1/4] Processando Metas e Curva de Diarizacao...
python -u load_metas_digital.py
if errorlevel 1 goto :erro

echo.
echo [2/4] Sincronizando com Qlik Sense Enterprise...
python -u extract_qlik_digital.py

echo.
echo [3/4] Executando Motor Analitico (Desvios, Evolucao, Projecoes)...
python -u process_digital_analytics.py
if errorlevel 1 goto :erro

echo.
echo [4/5] Compilando Dashboard Executivo (index.html)...
python -u build_dashboard.py
if errorlevel 1 goto :erro

echo.
echo [5/5] Publicando Atualizacoes no Git (GitHub Pages ^& Gitea)...
git add index.html data/*.json data/*.parquet >nul 2>&1
git diff --staged --quiet
if errorlevel 1 (
    git commit -m "Auto-sync Qlik Sense Digital (%date% %time%)"
    git push github main --quiet
    git push github HEAD:gh-pages --quiet
    git push origin HEAD:main --quiet
    echo Atualizacoes enviadas para o GitHub Pages e Gitea!
) else (
    echo Nenhum arquivo alterado para publicacao.
)

echo.
echo ======================================================================
echo ATUALIZACAO CONCLUIDA COM SUCESSO!
echo Dashboard atualizado localmente e online no GitHub Pages:
echo https://lukasg64-png.github.io/dashboard-categorias-digital/
echo ======================================================================
popd
exit /b 0

:erro
echo.
echo ======================================================================
echo ERRO NA ATUALIZACAO DO DASHBOARD DIGITAL
echo ======================================================================
popd
exit /b 1
