# Руководство по добавлению DisplayName в атрибуты пользователя Яндекс 360
Один из способов решения проблемы с различным отображением Имени, Фамилии, Отчества в сервисах Яндекс 360 - реплицировать вместо трёх атрибутов по отдельности один атрибут, например, displayName, в атрибут PropertyLastName, содержащий фамилию. Остальные атрибуты необходимо очистить от данных.
> [!WARNING] 
> Решение требует тестирования в контексте удобства поиска контактной информации в различных приложениях Яндекс 360 (Почта, Мессенджер)

## Реализация
Для реализации используем конфигурационный файл SCIM утилиты, который располагается по адресу `C:\ProgramData\Yandex\YandexADSCIM\AD_Users.config`. Модифицируем блок, отвечающий за передачу атрибутов пользователей:
```
PropertyFirstName = extensionAttribute4
PropertyMiddleName = extensionAttribute4
PropertyLastName = displayName
```
Наличие строки с установкой значения неиспользуемого атрибута обязательно, иначе система возьмёт для закомментированного атрибута значение по умолчанию (например, для атрибута `PropertyFirstName` будет использоваться атрибут AD `givenName`).
Если раньше в неиспользуемых в новой конфигурации атрибутах было какое-либо значние, то для гарантированной записи в этот атрибут пустого значения необходимо передать, как минимум, один пробел.
Т.е. если в предыдущей конфигурации синхронизации был реплирован из AD атрибут `givenName` в качестве `PropertyFirstName`, то установка в новой конфигурации атрибута `extensionAttribute4` для `PropertyFirstName` будет недостаточно - у пользователя в Яндекс 360 в поле `FirstName` останется старое значение (каталог Яндекс 360 не принимает пустой строки для модификации этого значения). Поэтому для всех реплицируемых пользователей в атрибут `extensionAttribute4` нужно добавить один пробел. После первичной репликации пробел можно удалить из значения атрибута `extensionAttribute4`.