import unittest
from cpuElement import CPUElement
from testElement import TestElement


class Control(CPUElement):
    # Setup connections for Control
    outputSignalNames = [
        'outputField_Jump', 'outputField_BEQ', 'outputField_RegDst',
        'outputField_MemRead', 'outputField_MemtoReg', 'outputField_ALUOp',
        'outputField_MemWrite', 'outputField_ALUSrc', 'outputField_RegWrite',
        'outputField_BNE', 'outputField_Immediate'
    ]
    
    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)
        # print(inputSources)
        assert len(inputSources) == 1, 'Control should have only one input.'
        assert len(outputValueNames) == 0, 'Control has no outputs.'
        assert len(control) == 0, 'Control has no signal inputs.'
        assert len(outputSignalNames) == 11, 'Control has 11 signal outputs.'

        # Assigning the input fields
        self.type_of_instruction = inputSources[0][1]

        # Assigning the output fields
        self.outputField_Jump = outputSignalNames[0]
        self.outputField_BEQ = outputSignalNames[1]
        self.outputField_RegDst = outputSignalNames[2]
        self.outputField_MemRead = outputSignalNames[3]
        self.outputField_MemtoReg = outputSignalNames[4]
        self.outputField_ALUOp = outputSignalNames[5]
        self.outputField_MemWrite = outputSignalNames[6]
        self.outputField_ALUSrc = outputSignalNames[7]
        self.outputField_RegWrite = outputSignalNames[8]
        self.outputField_BNE = outputSignalNames[9]
        self.outputField_Immediate = outputSignalNames[10]

        self.connectedElements = []


    def setControlSignals(self):
        type_of_instruction = self.inputValues.get(self.type_of_instruction, 'NOT FOUND')
        
        for signal in self.outputControlSignals:
            self.outputControlSignals[signal] = 0

        if type_of_instruction == 0x2:  # '000010' is opcode for 'j', jump
            self.outputControlSignals[self.outputField_Jump] = 1

        elif type_of_instruction == 0x4:  # '000100' is opcode for 'beq'
            self.outputControlSignals[self.outputField_BEQ] = 1
            self.outputControlSignals[self.outputField_ALUSrc] = 0
            self.outputControlSignals[self.outputField_ALUOp] = 0b01    # BEQ performs an add operation in ALU

        elif type_of_instruction == 0x5:  # The hex funct value for 'bne' is 0x5
            self.outputControlSignals[self.outputField_BNE] = 1
            self.outputControlSignals[self.outputField_ALUSrc] = 0
            self.outputControlSignals[self.outputField_ALUOp] = 0b01    # BNE performs a subtraction in ALU

        elif type_of_instruction == 0xf:  # '001111' is opcode for 'lui'
            self.outputControlSignals[self.outputField_ALUSrc] = 1
            self.outputControlSignals[self.outputField_RegWrite] = 1
            self.outputControlSignals[self.outputField_Immediate] = 1
            self.outputControlSignals[self.outputField_ALUOp] = 0b00    # LUI performs an add operation in ALU

        elif type_of_instruction == 0x0:  # For R-type instructions like -slt -add -addu
            # -sub -subu -and -or -nor (-break)
            self.outputControlSignals[self.outputField_RegDst] = 1
            self.outputControlSignals[self.outputField_RegWrite] = 1
            self.outputControlSignals[
                self.outputField_ALUOp] = 0b10  # ALU Control will use funct field to determine exact operation

        elif type_of_instruction == 0x23:  # '100011' is opcode for 'lw'
            self.outputControlSignals[self.outputField_MemRead] = 1
            self.outputControlSignals[self.outputField_MemtoReg] = 1
            self.outputControlSignals[self.outputField_ALUSrc] = 1
            self.outputControlSignals[self.outputField_RegWrite] = 1
            self.outputControlSignals[self.outputField_ALUOp] = 0b00    # LW performs an add operation in ALU

        elif type_of_instruction == 0x2b:  # '101011' is opcode for 'sw'
            self.outputControlSignals[self.outputField_MemWrite] = 1
            self.outputControlSignals[self.outputField_ALUSrc] = 1
            self.outputControlSignals[self.outputField_ALUOp] = 0b00    # SW performs an add operation in ALU

        elif type_of_instruction == 0x8:  # '001000' is opcode for 'addi'
            self.outputControlSignals[self.outputField_ALUSrc] = 1
            self.outputControlSignals[self.outputField_RegWrite] = 1
            self.outputControlSignals[
                self.outputField_ALUOp] = 0b00

        elif type_of_instruction == 0x9:  # '001001' is opcode for 'addiu'
            self.outputControlSignals[self.outputField_ALUSrc] = 1
            self.outputControlSignals[self.outputField_RegWrite] = 1
            self.outputControlSignals[
                self.outputField_ALUOp] = 0b00

        else:  
            self.outputControlSignals[self.outputField_Jump] = 0
            self.outputControlSignals[self.outputField_BEQ] = 0
            self.outputControlSignals[self.outputField_RegDst] = 0
            self.outputControlSignals[self.outputField_MemRead] = 0
            self.outputControlSignals[self.outputField_MemtoReg] = 0
            self.outputControlSignals[self.outputField_ALUOp] = 0
            self.outputControlSignals[self.outputField_MemWrite] = 0
            self.outputControlSignals[self.outputField_ALUSrc] = 0
            self.outputControlSignals[self.outputField_RegWrite] = 0
            self.outputControlSignals[self.outputField_BNE] = 0
            self.outputControlSignals[self.outputField_Immediate] = 0


    def writeOutput(self):
        for element in self.connectedElements:
            for signal, value in self.outputControlSignals.items():
                element.setOutputControl(signal, value)


class TestDataMemory(unittest.TestCase):
    def setUp(self):
        # Create an instance of Control
        self.control = Control()

        # Create a test element to simulate inputs and outputs
        self.testInput = TestElement()
        self.testOutput = TestElement()

        # Setup connections for testInput
        self.testInput.connect(
            [],
            ['type_of_instruction'], 
            [],
            []
        )

        # Setup connections for Control
        outputSignalNames = [
            'outputField_Jump', 'outputField_BEQ', 'outputField_RegDst',
            'outputField_MemRead', 'outputField_MemtoReg', 'outputField_ALUOp',
            'outputField_MemWrite', 'outputField_ALUSrc', 'outputField_RegWrite'
        ]
        self.control.connect(
            [(self.testInput, 'type_of_instruction')],
            [],
            [],
            outputSignalNames
        )

        # Setup connections for testOutput
        self.testOutput.connect(
            [],
            [],
            [
                (self.control, 'outputField_Jump'), (self.control, 'outputField_BEQ'),
                (self.control, 'outputField_RegDst'), (self.control, 'outputField_MemRead'),
                (self.control, 'outputField_MemtoReg'), (self.control, 'outputField_ALUOp'),
                (self.control, 'outputField_MemWrite'), (self.control, 'outputField_ALUSrc'),
                (self.control, 'outputField_RegWrite')
            ],
            []
        )
        self.control.connectedElements.append(self.testOutput)

    def test_jump_instruction(self):
        self.testInput.setOutputValue('type_of_instruction', '000010')
        self.control.readInput()  # Read the inputs set
        self.control.setControlSignals()  # Compute the control signals based on the input
        self.testOutput.readControlSignals()  # Read the computed control signals

        self.assertEqual(self.testOutput.controlSignals['outputField_Jump'], 1,
                         "Jump signal should be 1 for 'jump' instruction")

        for signal in ['outputField_BEQ', 'outputField_RegDst', 'outputField_MemRead', 'outputField_MemtoReg',
                       'outputField_ALUOp', 'outputField_MemWrite', 'outputField_ALUSrc', 'outputField_RegWrite']:
            self.assertEqual(self.testOutput.controlSignals[signal], 0, f"{signal} should be 0 for 'jump' instruction")

    def test_beq_instruction(self):
        # Given
        self.testInput.setOutputValue('type_of_instruction', '000100')  # '000100' is opcode for 'beq'

        # When
        self.control.readInput()
        self.control.setControlSignals()
        self.testOutput.readControlSignals()

        # Then
        expected_branch_signal = 1  # 'beq' instruction should set BEQ signal to 1
        actual_branch_signal = self.testOutput.controlSignals['outputField_BEQ']
        self.assertEqual(actual_branch_signal, expected_branch_signal)

        # Also, ensure that other control signals are as expected (probably set to 0, except BEQ)
        for signal_name, actual_value in self.testOutput.controlSignals.items():
            if signal_name != 'outputField_BEQ':
                self.assertEqual(actual_value, 0, f"{signal_name} should be 0 for 'beq' instruction")

    def test_bne_instruction(self):
        # Set the input opcode representing a 'bne' instruction
        self.testInput.setOutputValue('type_of_instruction', '000101')

        # Perform the operations in the Control unit
        self.control.readInput()
        self.control.setControlSignals()  # Assuming you are using setControlSignals method to set control signals

        # Check if only the BEQ control signal is set
        self.assertEqual(self.control.outputControlSignals[self.control.outputField_BEQ], 1)

        # Check that no other control signals are inadvertently set.
        # List all other control signals except BEQ and assert they are not set.
        for signal_name, value in self.control.outputControlSignals.items():
            if signal_name != self.control.outputField_BEQ:
                self.assertEqual(value, 0)

    def test_lui_instruction(self):
        # Set the input opcode representing a 'lui' instruction
        self.testInput.setOutputValue('type_of_instruction', '001111')

        # Perform the operations in the Control unit
        self.control.readInput()
        self.control.setControlSignals()  # Assuming you are using setControlSignals method to set control signals

        # Check if only the ALUSrc and RegWrite control signals are set
        self.assertEqual(self.control.outputControlSignals[self.control.outputField_ALUSrc], 1)
        self.assertEqual(self.control.outputControlSignals[self.control.outputField_RegWrite], 1)

        # Also, check that no other control signals are inadvertently set.
        # List all other control signals except ALUSrc and RegWrite and assert they are not set.
        for signal_name, value in self.control.outputControlSignals.items():
            if signal_name not in [self.control.outputField_ALUSrc, self.control.outputField_RegWrite]:
                self.assertEqual(value, 0)

    def test_r_type_instruction(self):
        # Set the input opcode representing an R-Type instruction
        self.testInput.setOutputValue('type_of_instruction', '000000')

        # Perform the operations in the Control unit
        self.control.readInput()
        self.control.setControlSignals()  # Assuming you are using setControlSignals method to set control signals

        # Check if the RegDst and RegWrite control signals are set and ALUOp is 'R_TYPE'
        self.assertEqual(self.control.outputControlSignals[self.control.outputField_RegDst], 1)
        self.assertEqual(self.control.outputControlSignals[self.control.outputField_RegWrite], 1)
        self.assertEqual(self.control.outputControlSignals[self.control.outputField_ALUOp], 'R_TYPE')

        # Also, check that no other control signals are inadvertently set.
        # List all other control signals except RegDst, RegWrite, and ALUOp and assert they are not set.
        for signal_name, value in self.control.outputControlSignals.items():
            if signal_name not in [self.control.outputField_RegDst, self.control.outputField_RegWrite,
                                   self.control.outputField_ALUOp]:
                self.assertEqual(value, 0)

    def test_lw_instruction(self):
        # Setup input values
        print("Initial state:", self.testOutput.outputControlSignals)  # Before any operation
        self.testInput.setOutputValue('type_of_instruction', '100011')  # 'lw' opcode
        print(self.testInput.outputValues)  # Print the output values of testInput

        # Call the setControlSignals() method explicitly, or run one cycle of the simulation.
        self.control.readInput()
        self.control.setControlSignals()
        self.control.writeOutput()
        print("After writeOutput on Control:",
              self.testOutput.outputControlSignals)  # Print after writeOutput is called on Control object

        # Assertions to check that the correct control signals are set
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemRead'), 1, "outputField_MemRead should be 1")
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemtoReg'), 1,
                         "outputField_MemtoReg should be 1")
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUSrc'), 1, "outputField_ALUSrc should be 1")
        self.assertEqual(self.testOutput.getControlSignal('outputField_RegWrite'), 1,
                         "outputField_RegWrite should be 1")

        # Assertions to check that all other control signals are unset
        self.assertEqual(self.testOutput.getControlSignal('outputField_Jump'), 0, "outputField_Jump should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_BEQ'), 0, "outputField_BEQ should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_RegDst'), 0, "outputField_RegDst should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemWrite'), 0,
                         "outputField_MemWrite should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUOp'), 0, "outputField_ALUOp should be 0")

    def test_sw_instruction(self):
        # Setup input values
        self.testInput.setOutputValue('type_of_instruction', '101011')  # 'sw' opcode

        # Call the setControlSignals() method explicitly, or run one cycle of the simulation.
        self.control.readInput()
        self.control.setControlSignals()
        self.control.writeOutput()

        # Assertions to check that the correct control signals are set
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemWrite'), 1,
                         "outputField_MemWrite should be 1")
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUSrc'), 1, "outputField_ALUSrc should be 1")

        # Assertions to check that all other control signals are unset
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemRead'), 0, "outputField_MemRead should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemtoReg'), 0,
                         "outputField_MemtoReg should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_RegWrite'), 0,
                         "outputField_RegWrite should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_Jump'), 0, "outputField_Jump should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_BEQ'), 0, "outputField_BEQ should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_RegDst'), 0, "outputField_RegDst should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUOp'), 0,
                         "outputField_ALUOp should be 'NOP'")

    def test_addi_instruction(self):
        print("Initial state:", self.testOutput.outputControlSignals)  # Before any operation

        self.testInput.setOutputValue('type_of_instruction', '001000')  # 'addi' opcode
        print(self.testInput.outputValues)  # Print the output values of testInput

        # Call the setControlSignals() method explicitly, or run one cycle of the simulation.
        self.control.readInput()
        self.control.setControlSignals()
        self.control.writeOutput()

        print("After writeOutput on Control:",
              self.testOutput.outputControlSignals)  # Print after writeOutput is called on Control object

        # Assertions to check that the correct control signals are set
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUSrc'), 1, "outputField_ALUSrc should be 1")
        self.assertEqual(self.testOutput.getControlSignal('outputField_RegWrite'), 1,
                         "outputField_RegWrite should be 1")
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUOp'), 'ADD',
                         "outputField_ALUOp should be 'ADD'")

    def test_addiu_instruction(self):
        # Setup input values
        print("Initial state:", self.testOutput.outputControlSignals)  # Before any operation
        self.testInput.setOutputValue('type_of_instruction', '001001')  # 'addiu' opcode
        print(self.testInput.outputValues)  # Print the output values of testInput

        # Call the setControlSignals() method explicitly, or run one cycle of the simulation.
        self.control.readInput()
        self.control.setControlSignals()
        self.control.writeOutput()
        print("After writeOutput on Control:",
              self.testOutput.outputControlSignals)  # Print after writeOutput is called on Control object

        # Assertions to check that the correct control signals are set
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUSrc'), 1, "outputField_ALUSrc should be 1")
        self.assertEqual(self.testOutput.getControlSignal('outputField_RegWrite'), 1,
                         "outputField_RegWrite should be 1")
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUOp'), 'ADDU',
                         "outputField_ALUOp should be 'ADDU'")

        # Assertions to check that all other control signals are unset
        self.assertEqual(self.testOutput.getControlSignal('outputField_Jump'), 0, "outputField_Jump should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_BEQ'), 0, "outputField_BEQ should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_RegDst'), 0, "outputField_RegDst should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemRead'), 0, "outputField_MemRead should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemtoReg'), 0,
                         "outputField_MemtoReg should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemWrite'), 0,
                         "outputField_MemWrite should be 0")

    def test_invalid_instruction(self):
        # Setup input values with an invalid opcode
        self.testInput.setOutputValue('type_of_instruction', '111111')  # '111111' is an invalid opcode

        # Call the setControlSignals() method explicitly, or run one cycle of the simulation.
        self.control.readInput()
        self.control.setControlSignals()
        self.control.writeOutput()

        # Assertions to check that all control signals are in their default state
        self.assertEqual(self.testOutput.getControlSignal('outputField_Jump'), 0, "outputField_Jump should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_BEQ'), 0, "outputField_BEQ should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_RegDst'), 0, "outputField_RegDst should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemRead'), 0, "outputField_MemRead should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemtoReg'), 0,
                         "outputField_MemtoReg should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUOp'), 'NOP',
                         "outputField_ALUOp should be 'NOP'")
        self.assertEqual(self.testOutput.getControlSignal('outputField_MemWrite'), 0,
                         "outputField_MemWrite should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_ALUSrc'), 0, "outputField_ALUSrc should be 0")
        self.assertEqual(self.testOutput.getControlSignal('outputField_RegWrite'), 0,
                         "outputField_RegWrite should be 0")

if __name__ == '__main__':
    unittest.main()