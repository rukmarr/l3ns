# L3 Network Simulator repository
Данная библотека предназначена для описания и запуска виртуальных сетей из Docker-контейнеров 
с помощью скриптов написанных на Python. 


### Installation

1. Для работы L3NS необходим Docker (https://docs.docker.com/engine/install/)
2. Для с Docker и L3NS без sudo нужна дополнительнпя настройка (https://docs.docker.com/engine/install/linux-postinstall/)
3. `pip3 install l3ns`


### First look

В папке [examples](examples) представлены примеры использования библиотеки. 
Для того, чтобы получить общее представление о библиотеке лучше всего подходит [этот пример](examples/simple/basic_docker_lab.py).

```python
from l3ns.ldc import DockerNode
from l3ns import defaults

n1 = DockerNode('test1', image='alpine', command='tail -f /dev/null')
n2 = DockerNode('test2', image='alpine', command='tail -f /dev/null')

n1.connect_to(n2)

print(n1.get_ip())
print(n2.get_ip())

defaults.network.start(interactive=True)
```

Запустить скрипт можно с помощью `python3`. 

```
    # python3 basic_docker_lab.py
    10.0.0.1
    10.0.0.2 
```

В ходе работы скрипта docker создаст два контейнера (`test1` и `test2`) из docker-образа `alpine`, 
в которых будет запущена команда `tail -f /dev/null`. Это команда не делает ничего 
и позволяет контейнеру работать неограниченное время до ручного завершения. 
Оба контейнера будут подключены к одной подсети, а их IP-адреса были выведены в ходе работы скрипта.
Вы можете подтвердить это запустив `ping` в любом из контейнеров: 

```
    docker exec -it node1 ping 10.0.0.2
```

Если вы увидете оттклик, значит IP-пакеты могут свободно перемещатся между узлами.


### Introduction

Работа L3NS построена вокруг трех типов объектов - `Node` (узел эмулируемой сети), `Subnet` (IP-подсеть эмулируемой сети), 
`Network` (отдельная эмулируемая сеть, локальная - LAN, или глобальная - WAN). Все подсети принадлежат одной сети, 
узлы могут принадлежать одной глобальной сети и нескольким локальным. 

L3NS предоставляет несколько реализаций узлов, 
подсетей и сетей, которые отличаются друг от друга сферой применения, но предоставляют одинаковый API.
Абстрактные классы, описываюшие общий API находятся в подмодуле [l3ns.base](l3ns/base). 
На данный момент L3NS предоставляет две реализации: 
[l3ns.ldc](l3ns/ldc) (Local Docker Container) и 
[l3ns.cluster](l3ns/cluster).

### Basic API outline




### Cluster requirements (Не актуальные)
* Всё запускается от рута
* У рута должен быть доступ без пароля на руты всех узлов кластера
* wg
* /tmp/l3ns



#### Generate docs on win:
```
chcp 65001
set PYTHONIOENCODING=utf-8
pdoc --pdf l3ns >> test.md
```
