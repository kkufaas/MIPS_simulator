'''
Code written for inf-2200, University of Tromso
'''

import unittest
from cpuElement import CPUElement
import common
from testElement import TestElement


class RegisterFile(CPUElement):
    def __init__(self):
        # Dictionary mapping register number to register value
        self.register = {}
        # Note that we won't actually use all the registers listed here...
        self.registerNames = ['$zero', '$at', '$v0', '$v1', '$a0', '$a1', '$a2', '$a3',
                              '$t0', '$t1', '$t2', '$t3', '$t4', '$t5', '$t6', '$t7',
                              '$s0', '$s1', '$s2', '$s3', '$s4', '$s5', '$s6', '$s7',
                              '$t8', '$t9', '$k0', '$k1', '$gp', '$sp', '$fp', '$ra']
        # All registers default to 0
        for i in range(0, 32):
            self.register[i] = 0

    def readInput(self):
        '''
        Read and set input values for this element.
        This function is called once for each simulation step.
        '''
        for i in self.inputSources:
            src, name = i
            value = src.getOutputValue(name)
            self.inputValues[name] = value
        # After reading input, decompose the instruction

    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)

        assert len(inputSources) == 4, 'RegisterFile should have four input sources'
        assert len(outputValueNames) == 2, 'RegisterFile should have two output values'
        assert len(control) == 1, 'RegisterFile should have one control input'
        assert len(outputSignalNames) == 0, 'RegisterFile should not have any control output'

        self.read_reg1 = inputSources[0][1]
        self.read_reg2 = inputSources[1][1]
        self.write_reg = inputSources[2][1]
        self.write_data = inputSources[3][1]

        self.read_data1 = outputValueNames[0]
        self.read_data2 = outputValueNames[1]

        self.control_signal = control[0][1]

    def writeOutput(self):
        read_reg1 = self.inputValues[self.read_reg1]
        read_reg2 = self.inputValues[self.read_reg2]
        write_reg = self.inputValues[self.write_reg]
        write_data = self.inputValues[self.write_data]
        reg_write = self.controlSignals[self.control_signal]

        if reg_write:
            self.register[write_reg] = write_data

        self.outputValues[self.read_data1] = self.register[read_reg1]
        self.outputValues[self.read_data2] = self.register[read_reg2]

    def printAll(self):
        '''
        Print the name and value in each register.
        '''
        print("Register file")
        print("================")
        for i in range(0, 32):
            print("%s \t=> %s (%s)" % (self.registerNames[i], common.fromUnsignedWordToSignedWord(
                self.register[i]), hex(int(self.register[i]))[:-1]))
        print("================")


class TestRegisterFile(unittest.TestCase):
    def setUp(self):
        self.rf = RegisterFile()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            ['Read register 1', 'Read register 2', 'Write register', 'Write Data'],
            [],
            ['RegWrite']
        )

        self.rf.connect(
            [(self.testInput, 'Read register 1'), (self.testInput, 'Read register 2'),
             (self.testInput, 'Write register'), (self.testInput, 'Write Data')],
            ['Read data 1', 'Read data 2'],
            [(self.testInput, 'RegWrite')],
            []
        )

        self.testOutput.connect(
            [(self.rf, 'Read data 1'), (self.rf, 'Read data 2')],
            [],
            [],
            []
        )

    def test_initial_state(self):
        for i in range(32):
            self.assertEqual(self.rf.register[i], 0)

    def test_multiple_writes(self):
        self.testInput.setOutputValue('Write register', 3)
        self.testInput.setOutputValue('Write Data', 25)
        self.testInput.setOutputControl('RegWrite', 1)

        self.rf.readInput()
        self.rf.readControlSignals()
        self.rf.writeOutput()

        self.assertEqual(self.rf.register[3], 25)
        self.rf.printAll()

        self.testInput.setOutputValue('Write register', 3)
        self.testInput.setOutputValue('Write Data', 30)

        self.rf.readInput()
        self.rf.readControlSignals()
        self.rf.writeOutput()

        self.assertEqual(self.rf.register[3], 30)
        self.rf.printAll()

    def test_correct_behavior(self):
        self.testInput.setOutputValue('Read register 1', 1)
        self.testInput.setOutputValue('Read register 2', 2)

        self.testInput.setOutputValue('Write register', 1)
        self.testInput.setOutputValue('Write Data', 10)

        self.testInput.setOutputControl('RegWrite', 1)

        self.rf.readInput()
        self.rf.readControlSignals()
        self.rf.writeOutput()
        self.testOutput.readInput()

        self.assertEqual(self.rf.register[1], 10)

        output1 = self.testOutput.inputValues['Read data 1']
        output2 = self.testOutput.inputValues['Read data 2']

        self.assertEqual(output1, 10)
        self.assertEqual(output2, 0)
        self.rf.printAll()

    def test_read_after_write(self):
        self.testInput.setOutputValue('Write register', 4)
        self.testInput.setOutputValue('Write Data', 45)
        self.testInput.setOutputControl('RegWrite', 1)

        self.rf.readInput()
        self.rf.readControlSignals()
        self.rf.writeOutput()

        self.testInput.setOutputValue('Read register 1', 4)
        self.rf.readInput()
        self.rf.readControlSignals()
        self.rf.writeOutput()
        self.testOutput.readInput()

        output = self.testOutput.inputValues['Read data 1']
        self.assertEqual(output, 45)


if __name__ == '__main__':
    unittest.main()
