from cpuElement import CPUElement
from testElement import TestElement
import unittest

class BufferGate(CPUElement):
    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)

        assert(len(inputSources) == 0), 'The Buffer-gate should not have any inputs'
        assert(len(outputValueNames) == 0), 'The Buffer-gate should not have any outputs'
        assert(len(control) == 1), 'The Buffer-gate should have two control signals'
        assert(len(outputSignalNames) == 1), 'The Buffer-gate should have one control output'

        # Assigning the input signals
        self.regWriteIn = control[0][1]

        # Assigning the output signal
        self.regWriteOut = outputSignalNames[0]

    def writeOutput(self):
        pass

    def setControlSignals(self):
        super().setControlSignals()
        if (self.controlSignals[self.regWriteIn] == 1):
            self.outputControlSignals[self.regWriteOut] = 1
        elif (self.controlSignals[self.regWriteIn] == 0):
            self.outputControlSignals[self.regWriteOut] = 0
        else:
            raise ValueError(f"The given control signal is not recognized: {self.controlSignal[self.regWriteOut]}")            

class TestBuffer(unittest.TestCase):
    def setUp(self):
        self.bufferGate = BufferGate()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            [],
            [],
            ['regWriteIn']
        )

        self.bufferGate.connect(
            [],
            [],
            [(self.testInput, 'regWriteIn')],
            ['Outputsignal']
        )

        self.testOutput.connect(
            [],
            [],
            [(self.bufferGate, 'Outputsignal')],
            []
        )

    def test_dummy(self):
        self.assertTrue(True, "Dummy test to run setUp")

    def test_correct_behavior(self):
        # Check when the input signal is 1
        self.testInput.setOutputControl('regWriteIn', 1)
        expectedvalue = 1

        self.bufferGate.readControlSignals()
        self.bufferGate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)

        # Check when the input signal is 0
        self.testInput.setOutputControl('regWriteIn', 0)
        expectedvalue = 0

        self.bufferGate.readControlSignals()
        self.bufferGate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)
        
if __name__ == "__main__":
    unittest.main()
                                                      