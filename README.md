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

CI собирает оба пакета, проверяет тесты `patrol` и отчёт ПР03.
Отчёт ПР02 проверяется на его коммите сдачи, поскольку после него
в репозитории появилась реализация следующей практики.
