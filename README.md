# l3ns

Welcome to the L3 Network Simulator repository.


## Cluster requirements
* Всё запускается от рута
* У рута должен быть доступ без пароля на руты всех узлов кластера
* wg
* /tmp/l3ns

#### TODO:
* Опциональный ввод пароля при подключении к хостам
* нужно убеждаться, что `detach=True`
* нормальные конфиги с учётом модулей
* проверить, что в iptables не остаётся мусора
* нормальные имена временных файлов по аналогии с именем wg-интерфейса
* адекватная работа со временными файлами
* заменить лок через `put_string` в `ldc.Node.start` на что-то адекватное
* общий интерфейс для файлов/строк
* переименовать `Subnet._nodes` чтобы было понятно, что это `dict`, наверное то же самое с `Node._interfaces`
* `WgSubnet.interface_name` могут меняться от запуска к запуску из-за кривого способа построения хэша
* Убрать конфиги в папки сетей для `WgSubnet` и убирать мусор в `WgSubnet.stop`
* connect_internet для wg-сетей
* настройка сети в `ldc.Node` не работает, если контейнер работает не с рутом
* окончателно убрасть параметр `dc` отовсюду
* нормальные логи
* тесты
* str для `ldc.Subnet`


#### Done:
* Модифицировать энтрипонт для ожидания сокета с учётом образа и аргуметов (ref: https://docs.docker.com/engine/reference/builder/#understand-how-cmd-and-entrypoint-interact)
* Загружать образ, если его нет
* нормальный `Subnet.get_gateway` и, видимо, нотация роутеров
