@echo off

REM Définir les chemins de répertoire en relatif
set SOURCE_DIR=.
set DEST_DIR=%SOURCE_DIR%\lambda_deploy
set ZIP_EXE="C:\Program Files\7-Zip\7z.exe"
set OUTPUT_ZIP=%SOURCE_DIR%\lambda_deploy.zip

REM Créer le répertoire de destination s'il n'existe pas déjà
if not exist "%DEST_DIR%" (
    mkdir "%DEST_DIR%"
)

REM Copier tous les fichiers .py vers le répertoire lambda_deploy
xcopy "%SOURCE_DIR%\*.py" "%DEST_DIR%\" /Y

REM Vérifier si la copie a réussi
if %errorlevel% neq 0 (
    echo Erreur lors de la copie des fichiers .py.
    exit /b 1
)

REM Compresser le répertoire lambda_deploy en lambda_deploy.zip
%ZIP_EXE% a -tzip "%OUTPUT_ZIP%" "%DEST_DIR%\*"

REM Vérifier si la compression a réussi
if %errorlevel% neq 0 (
    echo Erreur lors de la compression en ZIP.
    exit /b 1
)

echo Opération terminée avec succès.
exit /b 0
