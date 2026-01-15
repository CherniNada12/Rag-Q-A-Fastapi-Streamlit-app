@echo off
chcp 65001 >nul
cls

echo ========================================
echo 🚀 Learning Assistant RAG - Démarrage
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

REM Créer l'environnement virtuel si nécessaire
if not exist "venv\" (
    echo ⚠️  Environnement virtuel non trouvé
    echo Création de l'environnement virtuel...
    python -m venv venv
    echo ✅ Environnement virtuel créé
)

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo ✅ Environnement activé

REM Installer les dépendances
if not exist "venv\.dependencies_installed" (
    echo Installation des dépendances...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo. > venv\.dependencies_installed
    echo ✅ Dépendances installées
)

REM Créer les dossiers
echo Vérification de la structure...
if not exist "data\documents" mkdir data\documents
if not exist "data\chunks" mkdir data\chunks
if not exist "data\index" mkdir data\index
echo ✅ Dossiers vérifiés

REM Vérifier .env
if not exist ".env" (
    echo ⚠️  Fichier .env non trouvé
    echo Création du fichier .env...
    (
        echo # Configuration Learning Assistant RAG
        echo EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
        echo LLM_MODEL="gpt2"
        echo CHUNK_SIZE=500
        echo CHUNK_OVERLAP=50
        echo TOP_K_RESULTS=5
        echo API_HOST="0.0.0.0"
        echo API_PORT=8000
        echo OPENAI_API_KEY=""
    ) > .env
    echo ✅ Fichier .env créé
)

echo.
echo ========================================
echo 🎓 Learning Assistant RAG est prêt !
echo ========================================
echo.

REM Menu de démarrage
echo Choisissez le mode de démarrage :
echo 1) API seulement (FastAPI)
echo 2) Interface seulement (Streamlit)
echo 3) Les deux (recommandé)
echo.
set /p choice="Votre choix (1/2/3): "

if "%choice%"=="1" goto start_api
if "%choice%"=="2" goto start_streamlit
if "%choice%"=="3" goto start_both
echo Choix invalide
pause
exit /b 1

:start_api
echo.
echo 🚀 Démarrage de l'API FastAPI...
cd src\api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
goto end

:start_streamlit
echo.
echo 🚀 Démarrage de Streamlit...
cd src\frontend
streamlit run learning_app.py
goto end

:start_both
echo.
echo 🚀 Démarrage de l'API et de Streamlit...
echo.

REM Démarrer l'API dans une nouvelle fenêtre
start "FastAPI Server" cmd /k "cd src\api && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Attendre que l'API démarre
echo Attente du démarrage de l'API...
timeout /t 5 /nobreak >nul

REM Démarrer Streamlit
cd src\frontend
streamlit run learning_app.py

:end
echo.
echo Arrêt du Learning Assistant RAG...
pause