# command_processor.py

from macros import macros


class CommandProcessor:
    def __init__(self):
        self.blocks = []
        self.commands_in_row = []
        self.last_y = None

    def process(self, commands_with_delta):
        for i, (command, delta_y) in enumerate(commands_with_delta):
            cmd = command.strip().upper()

            if cmd not in macros and cmd != 'END_TRUSS':
                continue

            # END_TRUSS в начале
            if cmd == 'END_TRUSS' and i == 0:
                self.blocks.extend(macros['END_TRUSS_START'](delta_y).splitlines())
                self.commands_in_row.append(cmd)
                continue

            # обычная команда
            self.blocks.extend(macros[cmd](delta_y).splitlines())
            self.commands_in_row.append(cmd)
            self.last_y = delta_y

    def finalize(self, length):
        last_command = self.commands_in_row[-1] if self.commands_in_row else None
        remaining_length = length - self.last_y if self.last_y is not None else length

        if last_command == 'END_TRUSS':
            # END_TRUSS в конце строки
            self.blocks.extend(macros['END_TRUSS_FINISH'](remaining_length).splitlines())
            self.blocks.extend(macros['CUT_LENGTH'](length).splitlines())
        else:
            self.blocks.extend(macros['CUT'](remaining_length).splitlines())