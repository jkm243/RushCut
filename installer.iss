; RushCut - Script Inno Setup (https://jrsoftware.org)
[Setup]
AppName=RushCut
AppVersion=1.0
AppPublisher=RushCut
DefaultDirName={autopf}\RushCut
DefaultGroupName=RushCut
OutputDir=installer
OutputBaseFilename=RushCut-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
SetupIconFile=
DisableProgramGroupPage=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un icône sur le bureau"; GroupDescription: "Icônes :"

[Files]
Source: "dist\RushCut.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\RushCut"; Filename: "{app}\RushCut.exe"
Name: "{autodesktop}\RushCut"; Filename: "{app}\RushCut.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RushCut.exe"; Description: "Lancer RushCut"; Flags: nowait postinstall skipifsilent
