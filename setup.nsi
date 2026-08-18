Name "Horarios Escolares"
OutFile "InstaladorHorariosEscolares.exe"
InstallDir "$PROGRAMFILES\HorariosEscolares"

Section
  SetOutPath $INSTDIR
  File /r "dist\HorariosEscolares\*"
  CreateShortcut "$DESKTOP\Horarios Escolares.lnk" "$INSTDIR\HorariosEscolares.exe"
  CreateShortcut "$SMPROGRAMS\Horarios Escolares.lnk" "$INSTDIR\HorariosEscolares.exe"
SectionEnd
