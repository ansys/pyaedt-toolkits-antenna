; NSIS script for Antenna Toolkit installer

; Set the name, version, and output path of the installer
!define LICENSE_FILE "LICENSE"
!define PRODUCT_NAME "Antenna Toolkit"
!define /file PRODUCT_VERSION "VERSION"
!define OUTFILE_NAME "Antenna-Toolkit-v${PRODUCT_VERSION}.exe"

Name "${PRODUCT_NAME}"
OutFile "dist\${OUTFILE_NAME}"
VIProductVersion "${PRODUCT_VERSION}"

; Multi-user & UI
!define MULTIUSER_EXECUTIONLEVEL Highest
!define MULTIUSER_MUI
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!include MultiUser.nsh
!include MUI2.nsh
!include InstallOptions.nsh

!define MUI_PAGE_CUSTOMFUNCTION_PRE oneclickpre
!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
!insertmacro MUI_PAGE_INSTFILES
!include "uninstall.nsi"

Function CreateDesktopShortCut
  CreateShortCut "$desktop\${PRODUCT_NAME}.lnk" "$INSTDIR\AntennaToolkit.exe"
FunctionEnd

!define MUI_FINISHPAGE_RUN "$INSTDIR\AntennaToolkit.exe"
!define MUI_FINISHPAGE_SHOWREADME
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION "CreateDesktopShortCut"
!insertmacro MUI_PAGE_FINISH

Function .onInit
  !insertmacro MULTIUSER_INIT
FunctionEnd

Function un.onInit
  !insertmacro MULTIUSER_UNINIT
FunctionEnd

Section "MainApp" SEC01
  SetOutPath "$PROGRAMFILES64\${PRODUCT_NAME}"
  File /r "build\exe.win-amd64-3.10\*"

  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\AntennaToolkit.exe"

  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
SectionEnd

Icon "cx\splash_icon.ico"
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"

InstProgressFlags smooth
Function oneclickpre
  !insertmacro MUI_HEADER_TEXT "Installing ${PRODUCT_NAME}" "Please wait while installation completes."
  HideWindow
FunctionEnd

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE English
