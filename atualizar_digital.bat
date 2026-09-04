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
echo [4/4] Compilando Dashboard Executivo (index.html)...
python -u build_dashboard.py
if errorlevel 1 goto :erro

echo.
echo ======================================================================
echo ATUALIZACAO CONCLUIDA COM SUCESSO!
echo Dashboard atualizado: index.html
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
