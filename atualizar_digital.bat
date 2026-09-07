@echo off
pushd "%~dp0"
if not exist logs mkdir logs

set LOG=logs\daily_sync.log
echo. >> "%LOG%"
echo ====================================================================== >> "%LOG%"
echo [%date% %time%] INICIANDO ATUALIZACAO AUTOMATICA - CATEGORIAS DIGITAL >> "%LOG%"
echo ====================================================================== >> "%LOG%"

echo ======================================================================
echo INICIANDO ATUALIZACAO AUTOMATICA - CATEGORIAS DIGITAL
echo ======================================================================

echo [1/5] Processando Metas e Curva de Diarizacao...
python -u load_metas_digital.py >> "%LOG%" 2>&1
if errorlevel 1 goto :erro

echo.
echo [2/4] Sincronizando com Qlik Sense Enterprise...
python -u extract_qlik_digital.py >> "%LOG%" 2>&1

echo.
echo [3/4] Executando Motor Analitico (Desvios, Evolucao, Projecoes)...
python -u process_digital_analytics.py >> "%LOG%" 2>&1
if errorlevel 1 goto :erro

echo.
echo [4/5] Compilando Dashboard Executivo (index.html)...
python -u build_dashboard.py >> "%LOG%" 2>&1
if errorlevel 1 goto :erro

echo.
echo [5/5] Publicando Atualizacoes no Git (GitHub Pages ^& Gitea)...
git add index.html data/*.json data/*.parquet *.py >nul 2>&1
git diff --staged --quiet
if errorlevel 1 (
    git commit -m "Auto-sync Qlik Sense Digital (%date% %time%)" >> "%LOG%" 2>&1
    git push github main --quiet >> "%LOG%" 2>&1
    git push github HEAD:gh-pages --quiet >> "%LOG%" 2>&1
    git push origin HEAD:main --quiet >> "%LOG%" 2>&1
    echo Atualizacoes enviadas para o GitHub Pages e Gitea!
    echo [%date% %time%] Atualizacoes enviadas com sucesso! >> "%LOG%"
) else (
    echo Nenhum arquivo alterado para publicacao.
    echo [%date% %time%] Nenhum arquivo alterado para publicacao. >> "%LOG%"
)

echo.
echo ======================================================================
echo ATUALIZACAO CONCLUIDA COM SUCESSO!
echo Dashboard atualizado localmente e online no GitHub Pages:
echo https://lukasg64-png.github.io/dashboard-categorias-digital/
echo ======================================================================
echo [%date% %time%] ATUALIZACAO CONCLUIDA COM SUCESSO! >> "%LOG%"
popd
exit /b 0

:erro
echo.
echo ======================================================================
echo ERRO NA ATUALIZACAO DO DASHBOARD DIGITAL
echo ======================================================================
echo [%date% %time%] ERRO NA ATUALIZACAO DO DASHBOARD DIGITAL >> "%LOG%"
popd
exit /b 1
