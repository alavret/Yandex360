'Скрипт выполняет сканирование профилей Outlook и замену значений в профиле после выполнения автоконфигурации фейковым сервисом
'Autodiscovery для настройки сервисов Яндекс 360.
'например, профиль был настроен с адресом @360.contoso.com, скрипт заменит первую метку домена и сделает адрес в домене @contoso.com
'Также скрипт устанавливает LDAP адресную книгу и коннектор в Outlook

'приставка в сервисном домене, котроая должна быть удалена
strDomainToCut = "360."
'полный имя сервисного домена
strServiceDomain = "@360.contoso.com"
'визуальное название LDAP адресной книги в профиле Outlook
LDAPdisplayname = "LDAP"
'Сервер для загрузки LDAP адресной книги
LDAPserver = "dc01.contoso.com"
'Порт
LDAPport = "389"
'Стартовая локация для поиска данных в каталоге
LDAPsearchbase = "ou=Office,dc=contoso,dc=com"
'адрес установочного файла коннектора
strConnectorMSIPath = "\\dc01.contoso.com\Orgfiles\Y360ConnectorSetup_x86.msi"

'Функция получения DisplayName атрибута пользователя из AD
Function GetUserFulleName( )
  Set objSysInfo = CreateObject("ADSystemInfo")
  strUser = objSysInfo.UserName
  Set objUser = GetObject("LDAP://" & strUser)
  GetUserFulleName = objUser.Get("displayName")
  Exit Function
End Function

'Функция получения UPN атрибута пользователя из AD
Function GetUserUPN( )
  Set objSysInfo = CreateObject("ADSystemInfo")
  strUser = objSysInfo.UserName
  Set objUser = GetObject("LDAP://" & strUser)
  strUPN = objUser.Get("userPrincipalName")
  GetUserUPN = strUPN
End Function

'Функция устновки ДВФЗ адресной книги, код из ИНтернета
Sub SetLdap (strRegistryFolder, strUserName)
  const HKEY_CURRENT_USER = &H80000001
  strComputer = "."
  Set oReg=GetObject( "winmgmts:{impersonationLevel=impersonate}!\\" & strComputer & "\root\default:StdRegProv")

  
  If oReg.EnumKey(HKEY_CURRENT_USER, strRegistryFolder & "\9375CFF0413111d3B88A00104B2A6676\00000003", "") = 0 Then 
      wscript.echo "LDAP address book for " & strRegistryFolder & " already exist."
      Exit Sub
      Else
        wscript.echo "Setiing up LDAP address book for " & strRegistryFolder & "."
  End If
  
  'Add Ldap Type Key
  sKeyPath = strRegistryFolder & "e8cb48869c395445ade13e3c1c80d154\"
  oReg.CreateKey HKEY_CURRENT_USER, sKeyPath 
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "00033009", Array(0,0,0,0)
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "00033e03", Array(&H23,0,0,0)
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e3001", "Microsoft LDAP Directory"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e3006", "Microsoft LDAP Directory"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e300a", "EMABLT.DLL"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e3d09", "EMABLT"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e3d13", "{6485D268-C2AC-11D1-AD3E-10A0C911C9C0}"
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "01023d0c", Array(&H5c,&Hb9,&H3b,&H24,&Hff,&H71,&H07,&H41,&Hb7,&Hd8,&H3b,&H9c,&Hb6,&H31,&H79,&H92)
  
  'Add Ldap connection settings key
  sKeyPath = strRegistryFolder & "5cb93b24ff710741b7d83b9cb6317992\"
  oReg.CreateKey HKEY_CURRENT_USER, sKeyPath
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath,  "001e6602", strUserName 
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "00036623", Array(0,0,0,0)
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "00033009", Array(&H20,0,0,0)
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "000b6613", Array(0,0)
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "000b6615", Array(&H01,&H00)
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "000b6622", Array(&H01,&H00)
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e3001", LDAPdisplayname
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e3d09", "EMABLT"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e3d0a", "BJABLR.DLL"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e3d0b", "ServiceEntry"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e3d13", "{6485D268-C2AC-11D1-AD3E-10A0C911C9C0}"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6600", LDAPserver
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6601", LDAPport
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6603", LDAPsearchbase
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6604", "(&(mail=*)(|(mail=%s*)(|(cn=%s*)(|(sn=%s*)(givenName=%s*)))))"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6605", "SMTP"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6606", "mail"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6607", "60"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6608", "100"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6609", "120"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e660a", "15"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e660b", ""
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e660c", "OFF"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e660d", "OFF"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e660e", "NONE"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e660f", "OFF"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6610", "postalAddress"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6611", "cn"
  oReg.SetStringValue HKEY_CURRENT_USER, sKeyPath , "001e6612", "1"
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "001e67f1", Array(&H0a)
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "01023615", Array(&H50,&Ha7,&H0a,&H61,&H55,&Hde,&Hd3,&H11,&H9d,&H60,&H00,&Hc0,&H4f,&H4c,&H8e,&Hfa)
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "01023d01", Array(&He8,&Hcb,&H48,&H86,&H9c,&H39,&H54,&H45,&Had,&He1,&H3e,&H3c,&H1c,&H80,&Hd1,&H54)
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "01026631", Array(&H98,&H17,&H82,&H92,&H5b,&H43,&H03,&H4b,&H99,&H5d,&H5c,&Hc6,&H74,&H88,&H7b,&H34)
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "101e3d0f", Array(&H02,&H00,&H00,&H00,&H0c,&H00,&H00,&H00,&H17,&H00,&H00,&H00,&H45,&H4d,&H41,&H42,&H4c,&H54,&H2e,&H44,&H4c,&H4c,&H00,&H42,&H4a,&H41,&H42,&H4c,&H52,&H2e,&H44,&Hc,&H4c,&H00)
  
  'Append to Backup Key for ldap types
  sKeyPath = strRegistryFolder & "9207f3e0a3b11019908b08002b2a56c2\"
  oReg.getBinaryValue HKEY_CURRENT_USER,sKeyPath, "01023d01",Backup
  Dim oldLength
  oldLength = UBound (Backup)
  ReDim Preserve Backup(oldLength+16)
  Backup(oldLength+1) = &He8
  Backup(oldLength+2) = &Hcb
  Backup(oldLength+3) = &H48
  Backup(oldLength+4) = &H86
  Backup(oldLength+5) = &H9c
  Backup(oldLength+6) = &H39
  Backup(oldLength+7) = &H54
  Backup(oldLength+8) = &H45
  Backup(oldLength+9) = &Had
  Backup(oldLength+10) = &He1
  Backup(oldLength+11) = &H3e
  Backup(oldLength+12) = &H3c
  Backup(oldLength+13) = &H1c
  Backup(oldLength+14) = &H80
  Backup(oldLength+15) = &Hd1
  Backup(oldLength+16) = &H54
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "01023d01", Backup
  
  
  'Append to Backup Key for ldap connection settings
  sKeyPath = strRegistryFolder & "9207f3e0a3b11019908b08002b2a56c2\"
  oReg.getBinaryValue HKEY_CURRENT_USER,sKeyPath, "01023d0e",Backup
  oldLength = UBound (Backup)
  ReDim Preserve Backup(oldLength+16)
  Backup(oldLength+1) = &H5c
  Backup(oldLength+2) = &Hb9
  Backup(oldLength+3) = &H3b
  Backup(oldLength+4) = &H24
  Backup(oldLength+5) = &Hff
  Backup(oldLength+6) = &H71
  Backup(oldLength+7) = &H07
  Backup(oldLength+8) = &H41
  Backup(oldLength+9) = &Hb7
  Backup(oldLength+10) = &Hd8
  Backup(oldLength+11) = &H3b
  Backup(oldLength+12) = &H9c
  Backup(oldLength+13) = &Hb6
  Backup(oldLength+14) = &H31
  Backup(oldLength+15) = &H79
  Backup(oldLength+16) = &H92
  oReg.SetBinaryValue HKEY_CURRENT_USER, sKeyPath,  "01023d0e", Backup


  
  'Delete Active Books List Key
  'sKeyPath = RegistryFolder & "9375CFF0413111d3B88A00104B2A6676\{ED475419-B0D6-11D2-8C3B-00104B2A6676}"
  'oReg.DeleteKey HKEY_CURRENT_USER, sKeyPath'
End Sub

'Функциия установки коннектора в Outlook
Sub InstallConnector(strFilePath, CheckRegistryForExist)
  'Проверка, установлен ли уже этот коннектор
  Set oReg = GetObject("winmgmts:{impersonationLevel=impersonate}!\\" & strComputer & "\root\default:StdRegProv")
  If oReg.EnumKey(HKEY_CURRENT_USER, CheckRegistryForExist, "") = 0 Then
      wscript.echo "Yandex Connector for Outlook already installed."
      Exit Sub
      Else
        wscript.echo "Installing Yandex Connector..."
  End If
  Dim objShell
  Set objShell = Wscript.CreateObject ("Wscript.Shell")
  'Устнаовка клиента
  objShell.Run "cmd /c msiexec " & "/i " & Chr(34) & strFilePath & Chr(34) & " /quiet" & " /norestart"
  'Небольшая задержка перед выходом
  WScript.Sleep(3000)
  wscript.echo "Yandex Connector Installed."
End Sub

' Основаная часть прораммы

' Переменные для работы программы (настраивать нет неободимости)
Const HKEY_CURRENT_USER   = &H80000001
strComputer = "."
strStartSearch = "SOFTWARE\Microsoft\Office\"
strConnectorMSIRegistryPath = "SOFTWARE\Microsoft\Installer\Products\F997B29B009A2294DB2D92D4510DAC9C"
strNewDisplayName = GetUserFulleName()

'Листинг реестра на поиск ключей, соответстующим настроенным профилям Outlook и модификация отдельных значений в профиле
wscript.echo "Modifying Profiles..."
Set oReg = GetObject("winmgmts:{impersonationLevel=impersonate}!\\" & strComputer & "\root\default:StdRegProv")
oReg.EnumKey HKEY_CURRENT_USER, strStartSearch, arrSubKeys
For Each strSubkey In arrSubKeys
  If oReg.EnumKey(HKEY_CURRENT_USER, strStartSearch & strSubkey & "\Outlook\Profiles", "") = 0 Then 
    oReg.EnumKey HKEY_CURRENT_USER, strStartSearch & strSubkey & "\Outlook\Profiles", arrProfileKeys
    For Each strProfile In arrProfileKeys
      oReg.EnumKey HKEY_CURRENT_USER, strStartSearch & strSubkey & "\Outlook\Profiles\" & strProfile & "\9375CFF0413111d3B88A00104B2A6676", arrSubProfileKeys
      For Each strTempKey In arrSubProfileKeys
        'wscript.echo strTempKey
        If oReg.EnumKey(HKEY_CURRENT_USER, strTempKey, "") = 0 Then
          oReg.GetStringValue HKEY_CURRENT_USER, strTempKey, "Account Name", strAccountName
          'Если значние вида 360.contoso.com меняем на contoso.com
          If Not IsNull(strAccountName) Then
            if InStr(strAccountName, strServiceDomain) > 0 Then
              wscript.echo "Modifying " & strTempKey & ". ""Account Name"" was " & strAccountName & ", set to " & Replace(strAccountName, strDomainToCut, "")
              oReg.SetStringValue HKEY_CURRENT_USER, strTempKey, "Account Name", Replace(strAccountName, strDomainToCut, "")
            End If
          End If
          oReg.GetStringValue HKEY_CURRENT_USER, strTempKey, "Email", strMail
          'Если значние вида 360.contoso.com меняем на contoso.com
          If Not IsNull(strMail) Then
            if InStr(strMail, strServiceDomain) > 0 Then
              wscript.echo "Modifying " & strTempKey & ". ""Email"" was " & strAccountName & ", set to " & Replace(strMail, strDomainToCut, "")
              oReg.SetStringValue HKEY_CURRENT_USER, strTempKey, "Email", Replace(strMail, strDomainToCut, "")
            End If
          End If
          oReg.GetStringValue HKEY_CURRENT_USER, strTempKey, "Display Name", strDisplayName  
          If Not IsNull(strDisplayName) Then      
            intCompare = StrComp(strDisplayName, strNewDisplayName, vbTextCompare)
            'Меняем email на Display Name (если Display Name на русскром, то в консоли в диагностическом выводе может не выводится, т.к. вывод зависит от локали консоли)
            if intCompare <> 0 Then 
                wscript.echo "Modifying " & strTempKey & ". ""Display Name"" was " & strDisplayName & ", set to " & strNewDisplayName
                oReg.SetStringValue HKEY_CURRENT_USER, strTempKey, "Display Name",  strNewDisplayName
            End If
          End If
          'Если профиль настроен на IMAP сервер, запускаем настройку LDAP адресной книги
          oReg.GetStringValue HKEY_CURRENT_USER, strTempKey, "IMAP Server", strIMAP
          if Not IsNull(strIMAP) Then
            SetLdap strStartSearch & strSubkey & "\Outlook\Profiles\" & strProfile & "\",  GetUserUPN()
          End If        
        End If
      Next
    Next
  End If
Next
'Устанавливаем коннектор Yandex в Outlook
InstallConnector strConnectorMSIPath, strConnectorMSIRegistryPath


