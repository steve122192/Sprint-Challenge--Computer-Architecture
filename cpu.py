"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.ram = [None] * 256
        self.FL = 0b00000000
        
        # Command Translations
        self.SAVE = 0b10000010
        self.PRINT_REG = 0b01000111
        self.HALT = 0b00000001
        self.MULT = 0b10100010
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.RET = 0b00010001
        self.ADD = 0b10100000
        self.CMP = 0b10100111
        self.JEQ = 0b01010101
        self.JNE = 0b01010110
        self.JMP = 0b01010100

    def ram_read(self, address):
        return bin(self.ram[address])

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        address = 0

        program = [
            # From print8.ls8
            self.SAVE, # LDI R0,8
            0b00000000,
            0b00001000,
            self.PRINT_REG, # PRN R0
            0b00000000,
            self.HALT, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def load_from_file(self):
        file_name = sys.argv[1]
        try:
            address = 0
            with open(file_name) as file:
                for line in file:
                    split_line = line.split('#')[0]
                    command = split_line.strip()

                    if command == '':
                        continue

                    instruction = int(command, 2)
                    self.ram[address] = instruction

                    address += 1

        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} file was not found')
            sys.exit()

        if len(sys.argv) < 2:
            print("Please pass in a second filename: python3 in_and_out.py second_filename.py")
            sys.exit()


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        if op == 'CMP':
            a = self.reg[reg_a]
            b = self.reg[reg_b]
            if a == b:
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
        self.pc = 0  # program counter
        running = True
        while running:
            command = self.ram[self.pc]

            # SAVE
            if command == self.SAVE:
                reg = self.ram[self.pc + 1]
                num_to_save = self.ram[self.pc + 2]
                self.reg[reg] = num_to_save
                self.pc += (command >> 6)

            # PRINT_REG
            if command == self.PRINT_REG:
                reg_index = self.ram[self.pc + 1]
                print(self.reg[reg_index])
                self.pc += (command >> 6)

            # MULT
            if command == self.MULT:
                first_reg = self.ram[self.pc + 1]
                sec_reg = self.ram[self.pc + 2]
                self.reg[first_reg] = self.reg[first_reg] * self.reg[sec_reg]
                self.pc += (command >> 6)

            # ADD
            if command == self.ADD:
                first_reg = self.ram[self.pc + 1]
                sec_reg = self.ram[self.pc + 2]
                self.reg[first_reg] = self.reg[first_reg] + self.reg[sec_reg]
                self.pc += (command >> 6)

            # PUSH
            if command == self.PUSH:
                # decrement the stack pointer
                self.reg[7] -= 1
                
                # get the register number
                reg = self.ram[self.pc + 1]
                
                # get a value from the given register
                value = self.reg[reg]
                
                # put the value at the stack pointer address
                sp = self.reg[7]
                self.ram[sp] = value
                
                # Increment PC
                self.pc += (command >> 6)

            if command == self.POP:
                # get the stack pointer (where do we look?)
                sp = self.reg[7]

                # get register number to put value in
                reg = self.ram[self.pc + 1]

                # use stack pointer to get the value
                value = self.ram[sp]
                
                # put the value into the given register
                self.reg[reg] = value
                
                # increment our stack pointer
                self.reg[7] += 1

                # increment our program counter
                self.pc += (command >> 6)

            if command == self.CALL:
            #### Get register number
                reg = self.ram[self.pc + 1]

            ### get the address to jump to, from the register
                address = self.reg[reg]

            ### push command after CALL onto the stack
                return_address = self.pc + 2

                ### decrement stack pointer
                self.reg[7] -= 1
                sp = self.reg[7]
                ### put return address on the stack
                self.ram[sp] = return_address

            ### then look at register, jump to that address
                self.pc = address
                continue


            if command == self.RET:
                # pop the return address off the stack
                sp = self.reg[7]
                return_address = self.ram[sp]
                self.reg[7] += 1

                # go to return address: set the pc to return address
                self.pc = return_address
                continue

            # CMP
            if command == self.CMP:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu('CMP', reg_a, reg_b)
                self.pc += (command >> 6)

            # JMP
            if command == self.JMP:
                reg = self.ram[self.pc + 1]
                jump_to_address =  self.reg[reg]
                self.pc = jump_to_address
                continue

            # JEQ
            if command == self.JEQ:
                reg = self.ram[self.pc + 1]
                jump_to_address =  self.reg[reg]
                if self.FL == 0b00000001:
                    self.pc = jump_to_address
                    continue

            # JNE
            if command == self.JNE:
                reg = self.ram[self.pc + 1]
                jump_to_address =  self.reg[reg]
                if self.FL == 0b00000000:
                    self.pc = jump_to_address
                    continue


            # HALT
            if command == self.HALT:
                running = False

            self.pc += 1

        

if __name__ == "__main__":
    cpu = CPU()
    cpu.load_from_file()
    cpu.run()