; Author: Victor Hugo Garcia de Oliveira
; Date: 2025-12-21
;
; This Source Code Form is subject to the terms of the Mozilla Public
; License, v. 2.0. If a copy of the MPL was not distributed with this
; file, You can obtain one at https://mozilla.org/MPL/2.0/.
;
; Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
; License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
; arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.

; Script gerado para Inno Setup
; Consulte a documentação em http://www.jrsoftware.org/ishelp/

#define MyAppName "Profgent"
#define MyAppVersion "1.0"
#define MyAppPublisher "Victor Hugo Garcia de Oliveira"
#define MyAppURL "https://github.com/seu-repo/profgent"
#define MyAppExeName "Profgent.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
OutputDir=..\..\dist\installers
OutputBaseFilename=Profgent_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Nota: Este script assume que você rodou o 'scripts/build_executable.py' e gerou a versão OneDir.
; Ajuste o caminho 'Source' se necessário.
Source: "..\..\dist\onedir\Profgent\Profgent.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\onedir\Profgent\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
