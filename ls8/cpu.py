"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xf4  # stack pointer

    @property
    def sp(self):
        return self.reg[7]

    @sp.setter
    def sp(self, value):
        self.reg[7] = value

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def load(self, path):
        """Load a program into memory."""

        address = 0
        program = []

        try:
            with open(path) as f:
                for line in f:
                    instr = line.split('#', 1)[0].strip()
                    if len(instr):
                        program.append(int(instr, 2))
        except FileNotFoundError:
            print(f"No file {path}, exiting")
            sys.exit(2)

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]

        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        def halt():
            self.running = False

        def load_immediate():
            self.reg[operand_a] = operand_b

        def print_numeric():
            print(self.reg[operand_a])

        def store():
            self.ram[operand_a] = self.reg[operand_b]

        def add():
            self.alu("ADD", operand_a, operand_b)

        def sub():
            self.alu("SUB", operand_a, operand_b)

        def multiply():
            self.alu("MUL", operand_a, operand_b)

        def push_stack():
            self.sp -= 1
            self.ram[self.sp] = self.reg[operand_a]

        def pop_stack():
            self.reg[operand_a] = self.ram[self.sp]
            self.sp += 1

        def call():
            self.sp -= 1
            self.ram[self.sp] = self.ram[self.pc + 1]
            self.pc = self.reg[operand_a]

        def call_return():
            self.pc = self.ram[self.sp]
            self.sp += 1

        def jump():
            self.pc = self.reg[operand_a]

        def bitwise_and():
            self.alu("AND", operand_a, operand_b)

        def bitwise_or():
            self.alu("OR", operand_a, operand_b)

        bt = {
            0b00000001: halt,               # HTL
            0b10000010: load_immediate,     # LDI
            0b01000111: print_numeric,      # PRN
            0b10000100: store,              # ST
            0b10100000: add,                # ADD
            0b10100001: sub,                # SUB
            0b10100010: multiply,           # MUL
            0b01000101: push_stack,         # PUSH
            0b01000110: pop_stack,          # POP
            0b01010000: call,               # CALL
            0b00010001: call_return,        # RET
            0b01010100: jump,               # JMP
            0b10101000: bitwise_and,        # AND
            0b10101010: bitwise_or,         # OR
        }

        while self.running:
            IR = self.ram[self.pc]
            op_count = (IR & 0b11000000) >> 6
            sets_pc = (IR & 0b00010000) >> 4
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]

            command = bt.get(IR)

            if not command:
                print(f'Unknown instruction {IR:0b}')
                sys.exit(1)

            command()
            if not sets_pc:
                self.pc += (op_count + 1)
