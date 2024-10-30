@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=_build

REM This LOCs are used to uninstall and install specific package(s) during CI/CD
for /f %%i in ('pip freeze ^| findstr /c:"vtk-osmesa"') do set is_vtk_osmesa_installed=%%i
if NOT "%is_vtk_osmesa_installed%" == "vtk-osmesa" if "%ON_CI%" == "true" (
	@ECHO ON
	echo "Removing vtk to avoid conflicts with vtk-osmesa"
	@ECHO OFF
	pip uninstall --yes vtk
	@ECHO ON
	echo "Installing vtk-osmesa"
	@ECHO OFF
	pip install --extra-index-url https://wheels.vtk.org vtk-osmesa)

if "%1" == "" goto help
if "%1" == "clean" goto clean
if "%1" == "pdf" goto pdf

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:clean
rmdir /s /q %BUILDDIR% > /NUL 2>&1 
for /d /r %SOURCEDIR% %%d in (_autosummary) do @if exist "%%d" rmdir /s /q "%%d"
goto end

:pdf
echo Building PDF pages
%SPHINXBUILD% -M latex %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
cd "%BUILDDIR%\latex"
for %%f in (*.tex) do (
xelatex "%%f" --interaction=nonstopmode)
echo "Build finished. The PDF pages are in %BUILDDIR%."
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
