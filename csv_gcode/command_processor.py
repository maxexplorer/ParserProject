# command_processor.py

from macros import macros, command_map


class CommandProcessor:
    """
    Класс для обработки команд CSV и генерации блоков G-кода.

    Атрибуты:
        blocks (List[str]): Список строк G-кода для текущей строки CSV.
        commands_in_row (List[str]): Список обработанных команд в строке.
        last_y (float): Последнее значение Y для вычисления остатка длины.
    """

    def __init__(self) -> None:
        self.blocks: list[str] = []
        self.commands_in_row: list[str] = []
        self.last_y: float | None = None

    def process(self, commands_with_delta: list[tuple[str, float]]) -> None:
        """
        Обрабатывает список команд с дельтами Y.
        END_TRUSS в начале строки вставляет START, обычные команды вставляются через macros.

        Args:
            commands_with_delta (List[Tuple[str, float]]): Список кортежей (command, delta_y)
        """
        for i, (command, delta_y) in enumerate(commands_with_delta):
            cmd = command.strip().upper()

            if cmd not in command_map:
                continue

            macro_key = command_map[cmd]

            # команда имеет tuple (start_macro, finish_macro)
            if isinstance(macro_key, tuple):
                start_macro, finish_macro = macro_key

                # первая команда — START
                if i == 0:
                    self.blocks.extend(macros[start_macro](delta_y).splitlines())
                # последняя команда — FINISH
                elif i == len(commands_with_delta) - 1:
                    self.blocks.extend(macros[finish_macro](delta_y).splitlines())

            # обычная команда
            else:
                self.blocks.extend(macros[macro_key](delta_y).splitlines())

            self.commands_in_row.append(cmd)

    def finalize(self, length: float) -> None:
        """
        Завершает блок строки: вставляет CUT или END_TRUSS_FINISH + CUT_LENGTH
        в зависимости от последней команды.

        Args:
            length (float): Полная длина детали для корректного расчета CUT.
        """
        last_command = self.commands_in_row[-1] if self.commands_in_row else None
        remaining_length = length - self.last_y if self.last_y is not None else length

        if last_command == 'END_TRUSS':
            # END_TRUSS в конце строки
            self.blocks.extend(macros['CUT_LENGTH']().splitlines())
        else:
            self.blocks.extend(macros['CUT'](remaining_length).splitlines())
