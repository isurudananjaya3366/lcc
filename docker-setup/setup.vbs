' ============================================================
' LankaCommerce Cloud - Docker Setup Launcher
' ============================================================
' Double-click this file on Windows to launch the Setup Tool.
' Requirements: Python 3.8 or later must be installed.
'
' If Python is not installed, download it from:
'   https://www.python.org/downloads/
'   (Check "Add Python to PATH" during installation)
' ============================================================

Option Explicit

Dim oShell, oFSO, oEnv
Dim scriptDir, pyScript
Dim pythonExe, pyCheck
Dim result

Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")
Set oEnv   = oShell.Environment("PROCESS")

' ── Resolve paths ──────────────────────────────────────────────
scriptDir = oFSO.GetParentFolderName(WScript.ScriptFullName)
pyScript  = scriptDir & "\setup.py"

If Not oFSO.FileExists(pyScript) Then
    MsgBox "setup.py not found next to this script." & vbCrLf & _
           "Expected: " & pyScript, vbCritical, "LankaCommerce Setup"
    WScript.Quit 1
End If

' ── Find Python (py launcher > python > python3) ───────────────
pythonExe = ""

' Try Windows Python Launcher first (most reliable on Windows)
On Error Resume Next
result = oShell.Run("py --version", 0, True)
If Err.Number = 0 And result = 0 Then
    pythonExe = "py"
End If
Err.Clear
On Error GoTo 0

' Try 'python'
If pythonExe = "" Then
    On Error Resume Next
    result = oShell.Run("python --version", 0, True)
    If Err.Number = 0 And result = 0 Then
        pythonExe = "python"
    End If
    Err.Clear
    On Error GoTo 0
End If

' Try 'python3'
If pythonExe = "" Then
    On Error Resume Next
    result = oShell.Run("python3 --version", 0, True)
    If Err.Number = 0 And result = 0 Then
        pythonExe = "python3"
    End If
    Err.Clear
    On Error GoTo 0
End If

If pythonExe = "" Then
    MsgBox "Python 3 is required but was not found on this computer." & vbCrLf & vbCrLf & _
           "Please install Python 3.8 or later:" & vbCrLf & _
           "  https://www.python.org/downloads/" & vbCrLf & vbCrLf & _
           "IMPORTANT: During installation, check:" & vbCrLf & _
           "  [x] Add Python to PATH" & vbCrLf & vbCrLf & _
           "Then run this script again.", _
           vbCritical, "Python Not Found - LankaCommerce Setup"
    WScript.Quit 1
End If

' ── Launch the GUI (pythonw = no console window on Windows) ────
' Use pythonw for a cleaner experience (no black terminal window)
Dim launchCmd
If pythonExe = "py" Then
    ' py launcher: use -3 to ensure Python 3
    launchCmd = "pythonw -3 """ & pyScript & """"
    ' Fallback: some systems have py but not pythonw
    On Error Resume Next
    oShell.Run launchCmd, 0, False
    If Err.Number <> 0 Then
        Err.Clear
        launchCmd = "py -3 """ & pyScript & """"
        oShell.Run launchCmd, 1, False
    End If
    On Error GoTo 0
Else
    ' Direct python / python3
    Dim pythonwExe
    pythonwExe = Replace(pythonExe, "python3", "pythonw")
    pythonwExe = Replace(pythonwExe, "python",  "pythonw")

    On Error Resume Next
    oShell.Run pythonwExe & " """ & pyScript & """", 0, False
    If Err.Number <> 0 Then
        Err.Clear
        oShell.Run pythonExe & " """ & pyScript & """", 1, False
    End If
    On Error GoTo 0
End If

Set oShell = Nothing
Set oFSO   = Nothing
