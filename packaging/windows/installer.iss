; ImageTrim Windows 安装程序脚本
; 使用 Inno Setup 编译

#define MyAppName "ImageTrim"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "BlueRainCoat"
#define MyAppURL "https://github.com/blueraincoatli/DeDupImg"
#define MyAppExeName "ImageTrim.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{A3B3C3D3-E3F3-G3H3-I3J3-K3L3M3N3O3P3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
InfoBeforeFile=packaging\windows\preinstall.txt
InfoAfterFile=packaging\windows\postinstall.txt
OutputDir=dist
OutputBaseFilename=ImageTrim-{#MyAppVersion}-installer
SetupIconFile=app\resources\icons\imageTrim256px.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
WizardImageFile=app\resources\icons\imagetrim_final.svg
WizardSmallImageFile=app\resources\icons\imageTrim256px.png
ChangesAssociations=yes

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "app\resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "packaging\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\resources\icons\imageTrim256px.ico"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\BlueRainCoat\ImageTrim"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\BlueRainCoat\ImageTrim"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// 添加文件关联
procedure RegisterFileTypes();
begin
  // 关联图片文件类型
  RegWriteStringValue(HKEY_CLASSES_ROOT, '.jpg', '', 'ImageTrim.File');
  RegWriteStringValue(HKEY_CLASSES_ROOT, '.jpeg', '', 'ImageTrim.File');
  RegWriteStringValue(HKEY_CLASSES_ROOT, '.png', '', 'ImageTrim.File');
  RegWriteStringValue(HKEY_CLASSES_ROOT, '.gif', '', 'ImageTrim.File');
  RegWriteStringValue(HKEY_CLASSES_ROOT, '.bmp', '', 'ImageTrim.File');
  RegWriteStringValue(HKEY_CLASSES_ROOT, '.webp', '', 'ImageTrim.File');
  RegWriteStringValue(HKEY_CLASSES_ROOT, '.avif', '', 'ImageTrim.File');

  // 设置默认程序
  RegWriteStringValue(HKEY_CLASSES_ROOT, 'ImageTrim.File', '', 'Image File');
  RegWriteStringValue(HKEY_CLASSES_ROOT, 'ImageTrim.File\DefaultIcon', '', '{app}\resources\icons\imageTrim256px.ico,0');
  RegWriteStringValue(HKEY_CLASSES_ROOT, 'ImageTrim.File\shell\open\command', '', '"{app}\{#MyAppExeName}" "%1"');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    RegisterFileTypes();

    // 添加到PATH环境变量
    Exec('powershell.exe', '-Command "[Environment]::SetEnvironmentVariable(''PATH'', [Environment]::GetEnvironmentVariable(''PATH'', ''User'') + '';'' + ExpandConstant(''{app}''), ''User'")', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // 从PATH中移除
    Exec('powershell.exe', '-Command "$path = [Environment]::GetEnvironmentVariable(''PATH'', ''User''); $newPath = $path -replace [Regex]::Escape('';'' + ExpandConstant(''{app}'')), ''''; [Environment]::SetEnvironmentVariable(''PATH'', $newPath, ''User'')"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;