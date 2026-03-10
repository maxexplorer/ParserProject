# command_processor.py

from typing import List, Tuple
from macros import macros


class CommandProcessor:
    """
    Класс для обработки команд CSV и генерации блоков G-кода.

    Атрибуты:
        blocks (List[str]): Список строк G-кода для текущей строки CSV.
        commands_in_row (List[str]): Список обработанных команд в строке.
        last_y (float): Последнее значение Y для вычисления остатка длины.
    """

    def __init__(self) -> None:
        self.blocks: List[str] = []
        self.commands_in_row: List[str] = []
        self.last_y: float | None = None

    def process(self, commands_with_delta: List[Tuple[str, float]]) -> None:
        """
        Обрабатывает список команд с дельтами Y.
        END_TRUSS в начале строки вставляет START, обычные команды вставляются через macros.

        Args:
            commands_with_delta (List[Tuple[str, float]]): Список кортежей (command, delta_y)
        """
        for i, (command, delta_y) in enumerate(commands_with_delta):
            cmd = command.strip().upper()

            # игнорируем неизвестные команды, кроме END_TRUSS
            if cmd not in macros and cmd != 'END_TRUSS':
                continue

            # END_TRUSS в начале строки
            if cmd == 'END_TRUSS' and i == 0:
                self.blocks.extend(macros['END_TRUSS_START'](delta_y).splitlines())
                self.commands_in_row.append(cmd)
                continue

            # обычная команда
            self.blocks.extend(macros[cmd](delta_y).splitlines())
            self.commands_in_row.append(cmd)
            self.last_y = delta_y

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
            self.blocks.extend(macros['END_TRUSS_FINISH'](remaining_length).splitlines())
            self.blocks.extend(macros['CUT_LENGTH'](length).splitlines())
        else:
            self.blocks.extend(macros['CUT'](remaining_length).splitlines())