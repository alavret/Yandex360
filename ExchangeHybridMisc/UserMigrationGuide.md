# Инструкция по миграции пользователей из Exchange в Яндекс 360.
Данная инструкция описывает последовательность шагов по миграции пользователя из системы Exchange в Яндекс 360.

Предполагается, что эти почтовые системы сконфигурированы в режиме гибрида (часть пользователей почтового домена работает в Почте Яндекс 360, часть - в Exchange).

Из-за разницы между Exchange и IMAP сервисом Яндекс 360 Почта миграция состоит из двух независимых шагов - миграции почтовых сообщений и миграции событий календаря.
Каждый из этих шагов можно выполнить несколькими способами, в данной инструкции используется миграция почтовых сообщений через PST файл архива Outlook и миграция событий через файл формата ICS.
## Миграция почтовых сообщений (через PST архив).
Для выполнения этого шага необжодимо сформировать файловый архив писем в формате PST, где будут сообщения, которые необходимо мигрировать в Яндекс 360.
Создание такого архива реализуется несколькими способами:
- в Outlook, подключенного к Exchange, через меню Файл -> Открыть и Экспортировать -> Импорт и Экспорт.
- в Outlook, подключенного к Exchange, с помощью копирования сообщений из почтового ящика в подключённый в профиль файл архива.
- в Exchange сервере администратором.

> [!NOTE]
> При миграции/бэкапе в PST архив в процесс, как правило, включаются не только сообщения, но и события. Однако для дальнейшей работы события из PST архива в этой инструкции не испольлзуются. 

Справка:
- Создание PST файла - [Create an Outlook Data File](https://support.microsoft.com/en-us/office/create-an-outlook-data-file-pst-to-save-your-information-17a13ca2-df52-48e8-b933-4c84c2aabe7c)
- Автоархивация - [Archive older items automatically](https://support.microsoft.com/en-us/office/archive-older-items-automatically-25f44f07-9b80-4107-841c-41dc38296667)
- Экспорт и бэкап - [Export emails, contacts, and calendar items to Outlook using a .pst file](https://support.microsoft.com/en-us/office/export-emails-contacts-and-calendar-items-to-outlook-using-a-pst-file-14252b52-3075-4e9b-be4e-ff9ef1068f91)
- Экспорт в Exchange - [Procedures for mailbox exports to .pst files in Exchange Server](https://learn.microsoft.com/en-us/exchange/recipients/mailbox-import-and-export/export-procedures?view=exchserver-2019)

## Миграция событий
Для миграции событий будем использовать способ сохранения событий в виде ICS файла.

