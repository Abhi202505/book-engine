@echo off
REM Run this from anywhere; it switches to the repo root and starts Celery.
pushd %~dp0
"%~dp0.venv\Scripts\python.exe" "%~dp0celery_worker.py"
popd
