'''
Implements CPU element for Instruction Memory in MEM stage.

Code written for inf-2200, University of Tromso
'''

from cpuElement import CPUElement
from memory import Memory
from testElement import TestElement
import unittest
from common import Break


class InstructionMemory(Memory):
    BREAK = False

    def __init__(self, filename):
        Memory.__init__(self, filename)


    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)
        rsv = len(outputValueNames)

        ''' Remove this and replace with your implementation!
        # raise AssertionError("connect not implemented in class InstructionMemory!")'''
        assert (len(inputSources) == 1), 'InstructionMemory should have one input (PC)'
        assert (len(outputValueNames) == 8), 'InstructionMemory should have eight outputs'
        assert (len(control) == 0), 'InstructionMemory does not have control signal input'
        assert (len(outputSignalNames) == 0), 'InstructionMemory does not have any control output'

        self.pcInputName = inputSources[0][1] 
        self.instruction_instruction = outputValueNames[0]
        self.instruction_jump = outputValueNames[1]
        self.instruction_opcode = outputValueNames[2]
        self.instruction_rs = outputValueNames[3]
        self.instruction_rt = outputValueNames[4]
        self.instruction_rd = outputValueNames[5]
        self.instruction_imm = outputValueNames[6]
        self.instruction_func = outputValueNames[7]

    def slice_instruction(self, instruction):
        instruction_bin = format(instruction, '032b')

        slices = {
            self.instruction_jump: instruction_bin[6:],  # Bits 25 to 0
            self.instruction_opcode: instruction_bin[:6],
            # Bits 31 to 26. Determines the type of instruction (R-type, I-type, J-type, etc.).
            self.instruction_rs: instruction_bin[6:11],  # Bits 25 to 21
            self.instruction_rt: instruction_bin[11:16],  # Bits 20 to 16
            self.instruction_rd: instruction_bin[16:21],  # Bits 15 to 11
            self.instruction_imm: instruction_bin[16:],  # Bits 15 to 0
            self.instruction_func: instruction_bin[26:],  # Bits 5 to 0
        }
        return slices

    def getInstruction(self, address):
        """Retrieve instruction at the given address"""
        instruction = self.memory.get(address, None)
        if instruction is None:
            instruction = 0
        return instruction

    def writeOutput(self):
        """Remove this and replace with your implementation!
        # raise AssertionError("writeOutput not implemented in class InstructionMemory!")"""
        pcValue = self.inputValues[self.pcInputName]
        self.instruction = self.getInstruction(pcValue)

        if self.instruction == 0xD:
            self.BREAK = True
        
        self.instruction_slices = self.slice_instruction(self.instruction)
        self.outputValues[self.instruction_instruction] = self.instruction

        for key, value in self.instruction_slices.items():
            self.outputValues[key] = int(value, 2)
        ov = len(self.outputValues)
        print(f"IM: outputvalues are: {self.outputValues}")


class TestInstructionMemory(unittest.TestCase):
    def setUp(self):
        self.instructionMemory = InstructionMemory("add2.mem")
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            ['PC'],
            [],
            [])

        self.instructionMemory.connect(
            [(self.testInput, 'PC')],
            ['instructionOut', 'jump', 'opcode', 'rs', 'rt', 'rd', 'imm', 'func'],
            [],
            []
        )

        self.testOutput.connect(
            [(self.instructionMemory, 'instructionOut'), (self.instructionMemory, 'jump'), (self.instructionMemory, 'opcode'),
             (self.instructionMemory, 'rs'), (self.instructionMemory, 'rt'), (self.instructionMemory, 'rd'),
             (self.instructionMemory, 'imm'), (self.instructionMemory, 'func')],
            [],
            [],
            []
        )

    def test_correct_behavior(self):
        # PC value, first line in file, address 0xbfc00000
        self.testInput.setOutputValue('PC', 0xbfc00000)

        # Read the input, fetch the instruction and send the output
        self.instructionMemory.readInput()
        self.instructionMemory.writeOutput()
        self.testOutput.readInput()

        # Assuming at address 0xbfc00000 we have an instruction value of 0x0bf00080 in the memory file
        self.assertEqual(self.testOutput.inputValues['instructionOut'], 0x0bf00080)
        non_specified_address_value = self.instructionMemory.memory.get(0xbfc0000C, 0)
        self.assertEqual(non_specified_address_value, 0)

    def test_slice_instruction(self):
        # Set a known PC value where an instruction is located
        self.testInput.setOutputValue('PC', 0xbfc00000)

        # Read the input, fetch the instruction, and send the output
        self.instructionMemory.readInput()
        self.instructionMemory.writeOutput()

        # Slice the instruction
        instruction_slices = self.instructionMemory.slice_instruction(self.instructionMemory.instruction)

        expected_slices = {
            'jump': '11111100000000000010000000',
            'opcode': '000010',
            'rs': '11111',
            'rt': '10000',
            'rd': '00000',
            'imm': '0000000010000000',
            'func': '000000',
        }

        # Validate each sliced section
        for slice_range, expected_binary in expected_slices.items():
            with self.subTest(slice_range=slice_range):
                print(f"Actual {slice_range}: ", instruction_slices[slice_range])
                print(f"Expected {slice_range}: ", expected_binary)  # print the expected binary here
                self.assertEqual(instruction_slices[slice_range], expected_binary,
                                 f"Slice {slice_range} should be {expected_binary}")


if __name__ == '__main__':
    unittest.main()
