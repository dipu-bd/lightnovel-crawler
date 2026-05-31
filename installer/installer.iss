; Lightnovel Crawler - Windows Installer
; Compile: ISCC installer.iss /DMyAppVersion=X.Y.Z
; Requires: Inno Setup 6 (https://jrsoftware.org/isinfo.php)

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

#define MyAppName      "Lightnovel Crawler"
#define MyAppPublisher "LNCrawl"
#define MyAppURL       "https://github.com/lncrawl/lightnovel-crawler"
#define MyAppExeName   "lncrawl.exe"
; Stable AppId — never change this GUID, it identifies the app for upgrades/uninstalls
#define MyAppID        "{{4A2E8B3D-7F1C-4E6A-9D5B-2C0F8A3E7B1D}"

[Setup]
AppId={#MyAppID}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Per-user install by default (no UAC prompt); user can switch to machine-wide via dialog
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline dialog
ChangesEnvironment=yes
OutputDir=..\dist
OutputBaseFilename=lncrawl
SetupIconFile=..\res\lncrawl.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardStyle=modern
Compression=lzma2/ultra64
SolidCompression=yes
; Require Windows 10 or later
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "addtopath";   Description: "Add {#MyAppName} to PATH (for command-line use)"; GroupDescription: "Additional tasks:"; Flags: unchecked

[Files]
Source: "..\dist\lncrawl\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}";                          Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}";    Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}";                    Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Add install dir to current-user PATH when "addtopath" task is selected
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
  ValueData: "{olddata};{app}"; Check: PathEntryMissing('{app}'); Tasks: addtopath

[Code]
function PathEntryMissing(Entry: string): boolean;
var
  CurrentPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', CurrentPath) then
  begin
    Result := True;
    Exit;
  end;
  Result := Pos(';' + Lowercase(Entry) + ';',
                ';' + Lowercase(CurrentPath) + ';') = 0;
end;

[Run]
Filename: "{app}\{#MyAppExeName}"; \
  Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; \
  Flags: nowait postinstall skipifsilent
