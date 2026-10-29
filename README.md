# ROS

## PR01 — ROS 2

Материалы практической работы PR01: исследование графа ROS 2 и сбоя связи при разных значениях `ROS_DOMAIN_ID`.

Среда: Ubuntu 24.04, ROS 2 Jazzy, turtlesim. Основной домен — `16`, домен для воспроизведения сбоя — `17`.

## Материалы

- [Отчёт](evidence/pr01/report.json)
- [Описание графа и эксперимента](evidence/pr01/graph.md)
- [Сведения о среде](evidence/pr01/environment.json)
- [Диагностика ROS 2](evidence/pr01/doctor.txt)
- [Наблюдение при сбое](evidence/pr01/pose-broken.txt)
- [Наблюдение после восстановления](evidence/pr01/pose-fixed.txt)
- [Использование ИИ](AI_USAGE.md)

Course-kit, его архивы и каталоги сборки не включаются в репозиторий.

## PR02 — пакет и запуск turtlesim

Пакет `turtle_bringup` запускает одну готовую ноду turtlesim через
`sim.launch.py`. Среда: Ubuntu 24.04 / ROS 2 Jazzy, `ROS_DOMAIN_ID=16`.

Сборка из корня репозитория в терминале с базовой ROS:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup
```

Запуск в новом терминале A:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
```

`source` подключает окружение, `colcon` устанавливает пакет в workspace,
`ros2 launch` запускает описанный процесс. Завершение: Ctrl+C в A.
Для графического окна необходим работающий графический сеанс.

Проверка и одна команда движения в терминале B:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 node list --no-daemon --spin-time 2
ros2 topic echo /turtle1/pose --once
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
ros2 topic echo /turtle1/pose --once
```

Для повторения сбоя используйте непрерывную публикацию в `/cmd_vel` с
`--rate 1 --wait-matching-subscriptions 0`. Пока она работает, в отдельном
терминале сравните `ros2 topic info /cmd_vel --verbose` и
`ros2 topic info /turtle1/cmd_vel --verbose`. Остановите издателя через Ctrl+C,
замените только имя на `/turtle1/cmd_vel` и повторите. Не запускайте teleop
или второй turtlesim одновременно с этим опытом.

Материалы:

- [Команды с объяснениями и реальные результаты](evidence/pr02/commands.md)
- [Топики, типы и поля сообщений](evidence/pr02/types.md)
- [Отчёт](evidence/pr02/report.json)
- [Первоначальная сборка](evidence/pr02/build-empty.txt)
- [Итоговая сборка](evidence/pr02/build.txt)

Локальная проверка:

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```

[GitHub Actions](.github/workflows/ci.yml) собирает пакет без GUI, проверяет
установку launch-файла и evidence с закреплённым course-kit `v1-w03`.

## PR03 — своя нода: поза и команда

Пакет `patrol` для ROS 2 Jazzy хранит последнюю позу из `/turtle1/pose`.
Таймер каждые 0,1 секунды публикует `Twist` в относительный `cmd_vel`.
До первой позы команда нулевая; после — `linear.x=0.5`, `angular.z=0.3`.
Выбор команды вынесен в чистую функцию `command_for_pose`.

Сборка и тесты из корня workspace:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
python3 -m pytest src/patrol/test -v
```

В каждом терминале перед запуском:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
```

Терминал A — симулятор:

```bash
ros2 launch turtle_bringup sim.launch.py
```

Терминал B — правильный запуск:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Для воспроизведения дефекта остановите patrol в B через Ctrl+C и запустите
`ros2 run patrol patrol` без remap. Черепашка остановится: `/cmd_vel`
не совпадает с `/turtle1/cmd_vel`. Затем остановите эту ноду и верните remap.
Не запускайте teleop или второй patrol одновременно.

Терминал C — граф и реальная частота:

```bash
ros2 node info /patrol --no-daemon --spin-time 3
ros2 topic info /turtle1/cmd_vel --verbose --no-daemon --spin-time 3
timeout --signal=INT 10s ros2 topic hz /turtle1/cmd_vel
```

`timeout` завершает измерение через 10 секунд; код выхода 124 здесь ожидаем.
После Ctrl+C у patrol дождитесь нулевых скоростей в `/turtle1/pose`,
затем остановите симулятор в A. Завершение процесса не отправляет торможение.

Материалы ПР03:

- [Описание опыта и объяснение ROS](evidence/pr03/demo.md)
- [Результаты тестов](evidence/pr03/tests.txt)
- [Отчёт](evidence/pr03/report.json)

Проверка сдачи:

```bash
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

CI собирает оба пакета и проверяет текущие тесты `patrol`.
Отчёты предыдущих практик проверяются на их коммитах сдачи, поскольку
после них в репозитории появилась реализация следующей практики.


## PR04 — динамические параметры движения

Продолжение `patrol` из ПР03: параметры `linear_speed` (0–1 м/с),
`turn_rate` (−1–1 рад/с) и `publish_hz` (1–30 Гц) можно менять без
перезапуска. Значения по умолчанию: `0.5`, `0.3`, `10.0`. Все значения
должны быть конечными числами. До первой позы команда по-прежнему нулевая.

Сборка и тесты:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
python3 -m pytest src/patrol/test -v
```

В двух терминалах с подключёнными ROS и `install/setup.bash`, доменом `16`:

```bash
# A
ros2 launch turtle_bringup sim.launch.py
# B
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

В третьем терминале с тем же окружением:

```bash
ros2 param set /patrol publish_hz 5.0
ros2 param set /patrol publish_hz 0.0
ros2 param get /patrol publish_hz
ros2 topic hz /turtle1/cmd_vel
ros2 param set /patrol linear_speed 0.8
ros2 param set /patrol turn_rate -0.4
ros2 service call /clear std_srvs/srv/Empty '{}'
ros2 action list -t
```

`0.0` отклоняется: параметр остаётся `5.0`, поток — около 5 Гц.
Проверка кандидата не меняет состояние; post-set callback применяет
принятые значения, отменяет и удаляет старый таймер при смене частоты.

- [Параметры, дефект и реальные измерения](evidence/pr04/parameters.md)
- [Вывод сборки и тестов](evidence/pr04/tests.txt)
- [Отчёт ПР04](evidence/pr04/report.json)
- [Использование ИИ](AI_USAGE.md)

Для ПР04 нужен course-kit с манифестом PR04; использован закреплённый
`v1-w07` с проверенной SHA256 (ссылка и хеш в CI и отчёте).

```bash
python3 .course-kit/v1/tools/check_practice.py PR04 --submission .
```

ПР02 и ПР03 сохраняют свои исторические отчёты; CI проверяет их
на соответствующих коммитах с прежним course-kit `v1-w03`.

## PR05 — launch, QoS и повтор записи

`course_bringup` запускает один глобальный turtlesim и три ноды в
`/robot_a`: patrol, ретранслятор позы и подписчик сенсорного потока.
`pose_relay` передаёт позу без изменений с `best_effort`. Все имена
топиков внутри нод относительные; launch связывает вход позы и выход
команд с глобальными `/turtle1/pose` и `/turtle1/cmd_vel`.

Из корня репозитория:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol course_bringup
source install/setup.bash
export ROS_DOMAIN_ID=16
export ROS_LOG_DIR=/tmp/ros-pr05-logs
```

В каждом дополнительном терминале подключите оба `setup.bash` и задайте
тот же домен. Для запуска без окна можно задать `QT_QPA_PLATFORM=offscreen`.

1. В терминале A воспроизведите несовместимость без записи:

   ```bash
   ros2 launch course_bringup patrol.launch.py namespace:=robot_a \
     subscriber_reliability:=reliable record:=false
   ```

   В B топик виден, но `echo` завершается по таймауту с кодом 124:

   ```bash
   ros2 topic info /robot_a/sensor_pose --verbose
   timeout --signal=INT 4s ros2 topic echo /robot_a/sensor_pose \
     --qos-reliability reliable --once
   ```

2. Остановите A через Ctrl+C и запустите совместимый профиль с записью:

   ```bash
   ros2 launch course_bringup patrol.launch.py namespace:=robot_a \
     subscriber_reliability:=best_effort record:=true \
     bag_dir:=/tmp/pr05-new-bag
   ```

   В B проверьте доставку, затем остановите A через Ctrl+C:

   ```bash
   ros2 topic echo /robot_a/sensor_pose --qos-reliability best_effort --once
   ```

   Каталог `bag_dir` должен быть новым. По умолчанию запись выключена;
   при `record:=false` процесс recorder не создаётся (`IfCondition`).

3. При остановленной живой системе воспроизведите сохранённый bag:

   ```bash
   ros2 bag info /tmp/pr05-new-bag
   ros2 bag play /tmp/pr05-new-bag --loop \
     --qos-profile-overrides-path config/qos-overrides.yaml
   ```

   В B повторите оба `echo`: `reliable` снова даёт таймаут, а
   `best_effort` получает координаты. `--loop` позволяет успеть выполнить
   обе проверки на одной короткой записи; завершение — Ctrl+C.
   MCAP хранится локально и в сдачу не включается. Сохранённая запись
   выполненного опыта находится в игнорируемом `.local/pr05/bag`.

Проверка тестов и контракта сдачи:

```bash
colcon test --event-handlers console_direct+
colcon test-result --verbose
python3 .course-kit/v1/tools/check_practice.py PR05 --submission .
```

42 теста `patrol` включают две проверки реальной DDS-доставки: независимый
`best_effort`-наблюдатель получает неизменённую позу в обоих опытах,
а тестируемый подписчик — только с совместимым QoS.
Два интеграционных теста `course_bringup` проверяют запуск с обоими
значениями `record`, другой namespace, содержимое MCAP и завершение
всех процессов после SIGINT.

- [Диагностика несовместимости](evidence/pr05/qos-before.txt)
- [Исправление, запись и обе проверки replay](evidence/pr05/qos-after.txt)
- [Метаданные MCAP](evidence/pr05/bag-metadata.yaml)
- [Сборка и тесты — в конце диагностики](evidence/pr05/qos-after.txt)
- [Отчёт](evidence/pr05/report.json)
