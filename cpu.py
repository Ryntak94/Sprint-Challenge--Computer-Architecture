import sys

class CPU:
    """Main CPU class."""


    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.reg = [0]*8
        self.HALT = 0b00000001
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.pc = 0
        self.running = True
        self.MUL = 0b10100010
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.RET = 0b00010001
        self.ADD = 0b10100000
        self.FL = self.reg[4]
        self.CMP = 0b10100111
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""
        address = 0
        f = open(sys.argv[1], "r")
        for i in f:
            if i[0] == "0" or i[0] == "1":
                self.ram_write(int("0b"+i[0:8],2), address)
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while self.running:
            command = self.ram_read(self.pc)
            ops = command>>6
            # print(ops)
            if command == self.LDI:
                address = self.ram_read(self.pc + 1)
                value = self.ram_read(self.pc + 2)
                self.pc += 3
                self.reg[address] = value

            elif command == self.PRN:
                address = self.ram_read(self.pc + 1)
                self.pc += 2
                print(self.reg[address])

            elif command == self.ADD:
                address1 = self.ram_read(self.pc + 1)
                address2 = self.ram_read(self.pc + 2)
                self.alu("ADD", address1, address2)
                print(self.reg[self.pc + 1])
                self.pc += 3

            elif command == self.MUL:
                address1 = self.ram_read(self.pc + 1)
                address2 = self.ram_read(self.pc + 2)
                self.alu("MUL", address1, address2)
                print(self.reg[self.pc + 1])
                self.pc += 3

            elif command == self.PUSH:
                self.reg[7] -= 1
                SP = self.reg[7]

                reg_address = self.ram_read(self.pc + 1)
                value = self.reg[reg_address]

                self.ram_write(value, SP)
                self.pc += 2

            elif command == self.POP:
                SP = self.reg[7]
                value = self.ram_read(SP)
                reg_address = self.ram_read(self.pc + 1)
                self.reg[reg_address] = value

                self.reg[7] += 1
                self.pc += 2

            elif command == self.CALL:
                reg_address = self.ram_read(self.pc + 1)
                address_to_jump_to = self.reg[reg_address]

                next_instruction_address = self.pc + 2
                self.reg[7] - (self.reg[7] - 1) % 255
                SP = self.reg[7]
                self.ram_write(next_instruction_address, SP)

                self.pc = address_to_jump_to

            elif command == self.RET:
                SP = self.reg[7]
                address_to_return_to = self.ram_read(SP)

                self.pc = address_to_return_to

            elif command == self.CMP:
                address1 = self.ram_read(self.pc + 1)
                address2 = self.ram_read(self.pc + 2)
                self.alu("CMP", address1, address2)
                self.pc += 3

            elif command == self.JMP:
                self.pc = self.reg[self.ram_read(self.pc+1)]

            elif command == self.JEQ:
                if self.FL == 0b00000001:
                    self.pc = self.reg[self.ram_read(self.pc+1)]
                else:
                    self.pc += 2

            elif command == self.JNE:
                if self.FL != 0b00000001:
                    self.pc = self.reg[self.ram_read(self.pc+1)]
                else:
                    self.pc += 2

            elif command == self.HALT:
                self.running = False

            else:
                print('command not recognized: {}'.format(command))
                self.running = False
