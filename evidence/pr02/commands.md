# ПР02: команды, наблюдения и объяснения

Опыт выполнен локально на Ubuntu 24.04 / ROS 2 Jazzy,
`ROS_DOMAIN_ID=16`, с одной нодой turtlesim и без teleop.

## 1. Создание и первая сборка пустого пакета

Из корня репозитория:

```bash
cd src
ros2 pkg create --build-type ament_python --license Apache-2.0 \
  turtle_bringup --dependencies launch launch_ros turtlesim
cd ..
cat src/turtle_bringup/package.xml
```

- `package.xml` описывает имя и зависимости пакета.
- `setup.py` задаёт установку Python-модулей и ресурсов.
- `setup.cfg` задаёт каталог исполняемых скриптов, когда они появятся.
- `resource/turtle_bringup` — стандартный пустой маркер индекса пакетов ament.
- `turtle_bringup/__init__.py` — стандартный пустой Python-модуль; своей ноды нет.

В отдельном терминале, подключив только `/opt/ros/jazzy/setup.bash`:

```bash
set -o pipefail
colcon build --symlink-install --packages-select turtle_bringup \
  2>&1 | tee evidence/pr02/build-empty.txt
```

`colcon` собирает workspace; `--packages-select` выбирает один пакет;
`--symlink-install` использует ссылки на исходники там, где это поддерживается.
Первоначальный лог, когда launch-файла ещё не было:

```text
Starting >>> turtle_bringup
Finished <<< turtle_bringup [1.85s]

Summary: 1 package finished [2.14s]
```

В новом терминале запуска:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 pkg prefix turtle_bringup
ros2 node list --no-daemon --spin-time 2
```


Список нод пуст. Пакет установлен и найден, но процессы ещё не запущены.
`--no-daemon` запрашивает граф без фонового CLI-кэша;
`--spin-time 2` даёт две секунды на обнаружение участников.

## 2. Launch-файл, установка и управление процессом

Создан `src/turtle_bringup/launch/sim.launch.py`. Функция
`generate_launch_description()` возвращает `LaunchDescription` с одним
действием `Node(package='turtlesim', executable='turtlesim_node', output='screen')`.
Это описание запуска готового процесса, а не реализация собственной ROS-ноды.
В `setup.py` добавлены `glob` и запись
`('share/' + package_name + '/launch', glob('launch/*.launch.py'))`.
Записи маркера ament и `package.xml` сохранены.

Повторная сборка в свежем терминале с базовой ROS:

```bash
set -o pipefail
colcon build --symlink-install --packages-select turtle_bringup \
  2>&1 | tee evidence/pr02/build.txt
```

```text
Starting >>> turtle_bringup
Finished <<< turtle_bringup [1.34s]

Summary: 1 package finished [1.46s]
```

Терминал A, корень workspace:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 pkg prefix turtle_bringup
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
ros2 launch turtle_bringup sim.launch.py
```

В установленном каталоге найден `sim.launch.py`; проверка синтаксиса успешна.
В другом терминале `ros2 node list --no-daemon --spin-time 2` показала только:

```text
/turtlesim
```

После Ctrl+C команда `ros2 node list --no-daemon --spin-time 2`
вернула пустой список; процесса
`/opt/ros/jazzy/lib/turtlesim/turtlesim_node` нет.
Затем launch запущен снова для опыта с сообщениями. В конце опыта он тоже
остановлен через Ctrl+C. Фактический журнал второго запуска и остановки:

```text
1790586203.4223759 [INFO] [launch]: All log files can be found below /home/bottega_boy/.ros/log/2026-09-28-16-03-23-420247-Young-amadey-19708
1790586203.4226356 [INFO] [launch]: Default logging verbosity is set to INFO
1790586203.5158169 [INFO] [turtlesim_node-1]: process started with pid [19758]
1790586356.8998859 [WARNING] [launch]: user interrupted with ctrl-c (SIGINT)
1790586357.0600905 [INFO] [turtlesim_node-1]: process has finished cleanly [pid 19758]
```

После завершения опыта повторная проверка снова показала пустой список нод.
Запуск и завершение ноды проверены.

## 3. Доставка одной команды и изменение позы

В терминалах B/C подключена та же ROS и установлен `ROS_DOMAIN_ID=16`.
Teleop и другие издатели не работают; launch остаётся в A.

```bash
ros2 interface show geometry_msgs/msg/Twist
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
```

`interface show` выводит структуру сообщения, `topic type` — его тип,
`topic echo` подписывается и печатает сообщения. Для `echo --once` достаточно
одного полученного сообщения, затем команда завершается.
Фактический тип позы: `turtlesim/msg/Pose`.

Поза до команды:

```yaml
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
```

В B:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

`pub` создаёт издателя; здесь он отправляет одно сообщение.
Пропущенные компоненты векторов равны нулю.
Ожидаем движение вперёд с поворотом против часовой стрелки.
Реальный вывод издателя:

```text
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
```

После публикации в C снова выполнена `ros2 topic echo /turtle1/pose --once`:

```yaml
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
---
```

Координаты и угол изменились согласно ожидаемому движению. К моменту второго
снимка скорости нулевые: без новых команд turtlesim остановился.

## 4. Сбой имени: обнаружение без доставки

До сбоя `ros2 topic info /turtle1/cmd_vel --verbose` показала 0 издателей
и 1 подписчика `/turtlesim`.
В B запущена непрерывная публикация в другое полное имя:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

`--rate 1` — одно сообщение в секунду.
`--wait-matching-subscriptions 0` разрешает отправлять без подписчиков.
Для `pub --once` по умолчанию ожидается подписчик, поэтому ошибочная команда
с `--once` могла бы просто ждать; в опыте используем `--rate`.

Пока издатель работал, в C:

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
ros2 topic echo /turtle1/pose --once
```

Полный фактический вывод для ошибочного топика:

```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: _ros2cli_20258
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.8d.17.22.4f.7e.bf.00.00.00.00.00.00.07.03
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 0
```

Полный фактический вывод для топика, на который подписан turtlesim:

```text
Type: geometry_msgs/msg/Twist

Publisher count: 0

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 01.0f.8d.17.2e.4d.52.49.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

Поза во время сбоя:

```yaml
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
---
```

Она совпадает с позой после одиночной команды из раздела 4:
изменения координат и угла нет. Издатель существует и отправляет сообщения,
но подписчик turtlesim относится к другому имени.

Фрагмент фактического вывода ошибочного издателя (первые две публикации):

```text
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))

publishing #2: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
```

## 5. Исправление только имени

Ошибочный издатель остановлен Ctrl+C. Изменено только `/cmd_vel` на
`/turtle1/cmd_vel`; домен, тип, содержимое и частота остались прежними:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Пока издатель работал, снова выполнены:

```bash
ros2 topic info /turtle1/cmd_vel --verbose
ros2 topic echo /turtle1/pose --once
```

```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: _ros2cli_20521
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.8d.17.29.50.68.0c.00.00.00.00.00.00.07.03
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 01.0f.8d.17.2e.4d.52.49.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

Поза во время движения после исправления:

```yaml
x: 5.779031753540039
y: 9.529672622680664
theta: 3.0160000324249268
linear_velocity: 1.0
angular_velocity: 0.5
---
```

Ненулевые скорости и изменившиеся координаты подтверждают доставку команды.
После Ctrl+C у издателя и истечения тайм-аута turtlesim снята следующая поза:

```yaml
x: 7.417935848236084
y: 6.866191387176514
theta: 1.2208147048950195
linear_velocity: 0.0
angular_velocity: 0.0
---
```

| Этап | Топик издателя | Издатели / подписчики на нём | Наблюдение |
| --- | --- | --- | --- |
| До | `/turtle1/cmd_vel`, одна публикация | Подписчик `/turtlesim` присутствует | Поза изменилась, затем скорости стали нулевыми |
| Сбой | `/cmd_vel`, 1 Гц | 1 / 0 | Поза не изменилась |
| После | `/turtle1/cmd_vel`, 1 Гц | 1 / 1 | Скорости 1.0 и 0.5, поза меняется; после остановки издателя скорости нулевые |

Правильного типа недостаточно: для этого опыта издатель и подписчик должны
совпасть по полному имени топика и находиться в одном домене. В общем случае
также нужны совместимые QoS и работающая сеть/discovery.
**Обнаружение** показывает участников графа; **доставка** означает, что
подписчик получает сообщения. Наличие издателя в графе не доказывает доставку.

Файл launch на диске — описание действий; запущенная нода — процесс;
сообщение Twist — данные, которые этот процесс получает через топик.

## 6. Проверки и сдача

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```

Конфигурация `.github/workflows/ci.yml` подготовлена локально: сборка пакета,
наличие установленного launch-файла, проверка синтаксиса и checker PR02.