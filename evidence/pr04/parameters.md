# ПР04: параметризуем движение

## Реализация

Продолжен существующий пакет `patrol` из ПР03. Подписка сохраняет последнюю
позу, таймер публикует `Twist` в относительный `cmd_vel`; remap связывает
его с `/turtle1/cmd_vel`. До первой позы все компоненты команды нулевые.
После позы `linear.x` и `angular.z` берутся из текущих параметров.

| Параметр | По умолчанию | Допустимые значения | Влияние |
| --- | --- | --- | --- |
| `linear_speed` | `0.5` | конечные, 0–1 м/с | `Twist.linear.x` |
| `turn_rate` | `0.3` | конечные, −1–1 рад/с | `Twist.angular.z` |
| `publish_hz` | `10.0` | конечные, 1–30 Гц | период таймера `1/publish_hz` |

Параметры объявлены как ROS double; в CLI используйте `5.0`, а не `5`.
Чистая функция `updated_settings` создаёт проверенный неизменяемый
кандидат. Неверные границы, NaN и ±Inf приводят к `ValueError`.
`validate_parameters` возвращает `SetParametersResult(successful=False)`
без изменения состояния. Принятые значения применяет post-set callback,
после успеха всех валидаторов. При смене частоты он отменяет старый таймер,
создаёт новый и удаляет прежний. При неизменной частоте таймер не заменяется.
Executor остаётся однопоточным; одновременно работающих таймеров нет.
Переопределения параметров при запуске тоже проверяются до создания таймера.

## Окружение и запуск

Выполнено из корня workspace:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
export ROS_DOMAIN_ID=16
export ROS_LOG_DIR=/tmp/pr04-ros-logs
```

В двух процессах этого окружения запущены:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
QT_QPA_PLATFORM=offscreen ros2 run turtlesim turtlesim_node
```

## Реальные параметры и поток

Ниже фактические команды и вывод завершённого исправного опыта.
Наблюдатель `/pr04_monitor` подписан на команду и позу; он не публикует
команды. Перед каждым окном измерения он обрабатывает очередь старых
сообщений; затем считает только новые поступления по монотонным часам.
`ros2 topic hz` работает параллельно и останавливается SIGINT через 6 с.
Оценка по интервалам: `(число сообщений − 1)/(последнее время − первое)`.

```text
$ ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
Before the first pose: all received commands are zero.
$ ros2 run turtlesim turtlesim_node
$ ros2 topic type /turtle1/pose --no-daemon --spin-time 2
turtlesim/msg/Pose
$ ros2 param get /patrol linear_speed
Double value is: 0.5
$ ros2 param get /patrol turn_rate
Double value is: 0.3
$ ros2 param get /patrol publish_hz
Double value is: 10.0
$ ros2 topic hz /turtle1/cmd_vel
average rate: 10.003
	min: 0.100s max: 0.100s std dev: 0.00020s window: 11
average rate: 10.001
	min: 0.100s max: 0.100s std dev: 0.00015s window: 22
average rate: 10.001
	min: 0.100s max: 0.101s std dev: 0.00020s window: 33
average rate: 10.000
	min: 0.100s max: 0.101s std dev: 0.00018s window: 43
default: 60 messages in 6 s; interval rate 9.9997 Hz
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful
$ ros2 param get /patrol publish_hz
Double value is: 5.0
$ ros2 topic hz /turtle1/cmd_vel
average rate: 5.000
	min: 0.200s max: 0.200s std dev: 0.00020s window: 6
average rate: 5.000
	min: 0.200s max: 0.200s std dev: 0.00027s window: 12
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00032s window: 18
changed: 30 messages in 6 s; interval rate 5.0004 Hz
$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be finite and in [1.0, 30.0]
$ ros2 param get /patrol publish_hz
Double value is: 5.0
$ ros2 topic hz /turtle1/cmd_vel
average rate: 5.001
	min: 0.199s max: 0.201s std dev: 0.00038s window: 6
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00037s window: 12
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00033s window: 18
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00031s window: 24
rejected-zero: 30 messages in 6 s; interval rate 4.9996 Hz
$ ros2 param set /patrol linear_speed 0.8
Set parameter successful
$ ros2 param set /patrol turn_rate -0.4
Set parameter successful
Accepted speeds: command linear.x=0.8, angular.z=-0.4; pose velocities=0.800000011920929, -0.4000000059604645
$ ros2 service call /clear std_srvs/srv/Empty {}
waiting for service to become available...
requester: making request: std_srvs.srv.Empty_Request()

response:
std_srvs.srv.Empty_Response()
$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
PASS: live parameter updates, measured stream, rejected zero, clear and action discovery.
```

| Этап | Сообщений за 6 с | Частота по интервалам |
| --- | --- | --- |
| Начальные 10 Гц | 60 | 9.9997 Гц |
| После установки 5.0 | 30 | 5.0004 Гц |
| После отклонения 0.0 | 30 | 4.9996 Гц |

Отклонение нуля не изменило значение `5.0`, не прекратило поток и не
удвоило его. Смена скорости и поворота подтверждена и командами, и
скоростями в сообщениях позы. После опыта процессы остановлены SIGINT.

## Намеренный дефект и исправление

Дефект сохранён в отдельном коммите и локальной ветке `pr04-defect`:
`b05bb9188db07bd76f83cbf988f5423469fff2b9`.
Он входит также в историю `main`, за ним следует восстановление проверки:
`054cbe59e7d1f049a3d7b7a09695084e4e747e8f`.
В дефектном коммите в цикле проверки `settings.py` добавлены только строки:

```python
if name == 'publish_hz':
    continue
```

Дефектный код запускался из отдельного worktree `/tmp/ros-pr04-defect`.
Сначала выполнен неизменённый тест, который на исправной версии проходит:

```bash
cd /tmp/ros-pr04-defect
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=17
export ROS_LOG_DIR=/tmp/pr04-defect-logs
export PYTHONPATH="/tmp/ros-pr04-defect/src/patrol:$PYTHONPATH"
python3 -m pytest 'src/patrol/test/test_parameters.py::test_invalid_frequency_preserves_state[0.0]' -v
```

Фактический результат: `1 failed`, `ZeroDivisionError: float division by zero`
в `apply_parameters`, строка `1.0 / candidate.publish_hz`.
Полный вывод этого ожидаемого провала сохранён в `tests.txt`.
Затем отдельно запущена дефектная нода:

```bash
python3 -m patrol.patrol
```

В другом процессе с тем же доменом и базовой ROS выполнена та же команда,
что в исправном опыте:

```bash
ros2 param set /patrol publish_hz 0.0
```

До запроса наблюдатель получил 17 команд. После запроса процесс завершился
с кодом `1`; клиент пришлось прервать через 6 с, так как сервер упал до
отправки ответа. Конец фактического traceback:

```text
  File "/tmp/ros-pr04-defect/src/patrol/patrol/patrol.py", line 72, in apply_parameters
    1.0 / candidate.publish_hz, self.on_timer)
    ~~~~^~~~~~~~~~~~~~~~~~~~~~
ZeroDivisionError: float division by zero

Broken patrol process exit code: 1
After failure: 0 commands in a fresh 1-second observation window.
```

Причина: без проверки частота `0.0` принимается параметрическим сервисом;
post-set callback отменяет старый таймер и делит на ноль при создании
нового. Активное состояние уже разрушено, нода прекращает публикацию.
После возврата проверки тот же запрос возвращает явный отказ, параметр
остаётся `5.0`, поток — около 5 Гц (см. исправный опыт выше). Тот же тест
нулевой частоты входит в итоговые `40 passed`. Чистые тесты отдельно
проверяют 10 -> 5 Гц, ноль, отрицательное значение и NaN, границы и +-Inf.
ROS-тесты дополнительно подтверждают неизменность таймера при отказе,
атомарность смешанного запроса и отсутствие побочных эффектов при отказе
другого валидатора.

Для повторения дефекта после нового клонирования можно создать worktree
по сохранённому SHA (выберите свободный путь):

```bash
git worktree add --detach /tmp/ros-pr04-defect b05bb9188db07bd76f83cbf988f5423469fff2b9
```

Не выполняйте этот запуск одновременно с исправной нодой в одном домене.

## Сервис и действие: два предложения

Запрос сервиса `/clear` выполняет одну короткую операцию и возвращает один
ответ, без промежуточного feedback и отмены выполняющегося запроса.
Цель действия `/turtle1/rotate_absolute` описывает длительный поворот:
клиент может получать feedback, запросить отмену и затем получить результат.

## Course-kit и сдача

https://ros.lms.ci.nsu.ru/downloads/robotics-course-kit-v1-w07-9b7fdd5424d3.tar.gz.
SHA256 проверена по опубликованному файлу:
`9b7fdd5424d3d97e47d51dbe23064934585e62135dc2902844dd679529bda929`.

```bash
python3 -m pytest src/patrol/test -v
python3 .course-kit/v1/tools/check_practice.py PR04 --submission .
```
