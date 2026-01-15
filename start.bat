@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Systeme RAG - FastAPI + Streamlit
echo ========================================
echo.

REM Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe
    pause
    exit /b 1
)

echo [OK] Python detecte

REM Creer l'environnement virtuel si necessaire
if not exist "venv" (
    echo [INFO] Creation de l'environnement virtuel...
    python -m venv venv
    echo [OK] Environnement virtuel cree
)

REM Activer l'environnement virtuel
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer les dependances si necessaire
if not exist "venv\installed" (
    echo [INFO] Installation des dependances...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo installed > venv\installed
    echo [OK] Dependances installees
)

REM Creer les repertoires necessaires
if not exist "data\documents" mkdir data\documents
if not exist "data\chunks" mkdir data\chunks
if not exist "data\index" mkdir data\index

REM Verifier le fichier .env
if not exist ".env" (
    echo [INFO] Creation du fichier .env...
    (
        echo PROJECT_NAME="RAG FastAPI Streamlit"
        echo ENVIRONMENT="development"
        echo DATA_DIR="./data"
        echo DOCUMENTS_DIR="./data/documents"
        echo CHUNKS_DIR="./data/chunks"
        echo INDEX_DIR="./data/index"
        echo CHUNK_SIZE=500
        echo CHUNK_OVERLAP=50
        echo TOP_K_RESULTS=5
        echo EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
        echo LLM_MODEL="gpt2"
        echo OPENAI_API_KEY=""
        echo API_HOST="0.0.0.0"
        echo API_PORT=8000
        echo STREAMLIT_PORT=8501
    ) > .env
    echo [OK] Fichier .env cree
)

echo.
echo ========================================
echo    Systeme pret a demarrer!
echo ========================================
echo.
echo Que voulez-vous demarrer ?
echo.
echo 1) API FastAPI uniquement
echo 2) Interface Streamlit uniquement
echo 3) Les deux (API + Streamlit)
echo 4) Tests avec Jupyter Notebook
echo 5) Quitter
echo.

set /p choice="Votre choix (1-5): "

if "%choice%"=="1" (
    echo [INFO] Demarrage de l'API FastAPI...
    cd src\api
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
    cd ..\..
) else if "%choice%"=="2" (
    echo [INFO] Demarrage de Streamlit...
    cd src\frontend
    streamlit run app.py
    cd ..\..
) else if "%choice%"=="3" (
    echo [INFO] Demarrage de l'API et Streamlit...
    echo [INFO] API sur http://localhost:8000
    echo [INFO] Streamlit sur http://localhost:8501
    
    REM Demarrer l'API dans une nouvelle fenetre
    start "API FastAPI" cmd /k "cd src\api && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    
    REM Attendre 3 secondes
    timeout /t 3 /nobreak >nul
    
    REM Demarrer Streamlit
    cd src\frontend
    streamlit run app.py
    cd ..\..
) else if "%choice%"=="4" (
    echo [INFO] Demarrage de Jupyter Notebook...
    jupyter notebook notebooks\
) else if "%choice%"=="5" (
    echo Au revoir!
    exit /b 0
) else (
    echo [ERREUR] Choix invalide
    pause
    exit /b 1
)

pause