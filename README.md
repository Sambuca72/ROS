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
- [Использование ИИ](AI_USAGE.md)

Локальная проверка:

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```

[GitHub Actions](.github/workflows/ci.yml) собирает пакет без GUI, проверяет
установку launch-файла и evidence с закреплённым course-kit `v1-w03`.
Результаты запуска
CI можно получить только после push.
