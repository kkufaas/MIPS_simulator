from cpuElement import CPUElement
from testElement import TestElement
import unittest

class Not(CPUElement):
    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)

        assert(len(inputSources) == 0), 'The Not-gate should not have any inputs'
        assert(len(outputValueNames) == 0), 'The Not-gate should not have any outputs'
        assert(len(control) == 1), 'The Not-gate should have two control signals'
        assert(len(outputSignalNames) == 1), 'The Not-gate should have one control output'

        # Assigning the input signals
        self.aluzero = control[0][1]

        # Assigning the output signal
        self.controlOutput = outputSignalNames[0]

    def writeOutput(self):
        pass

    def setControlSignals(self):
        super().setControlSignals()

        # The Not operation flips the input values to be the opposite value (in binary)
        if (self.controlSignals[self.aluzero] == 1):
            self.outputControlSignals[self.controlOutput] = 0
        elif (self.controlSignals[self.aluzero] == 0):
            self.outputControlSignals[self.controlOutput] = 1
        else:
            pass
        print(f"\nnot: the outputsignal is: {self.outputControlSignals}")
            

class TestNot(unittest.TestCase):
    def setUp(self):
        self.NOTgate = Not()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            [],
            [],
            ['aluzero']
        )

        self.NOTgate.connect(
            [],
            [],
            [(self.testInput, 'aluzero')],
            ['Outputsignal']
        )

        self.testOutput.connect(
            [],
            [],
            [(self.NOTgate, 'Outputsignal')],
            []
        )

    def test_dummy(self):
        self.assertTrue(True, "Dummy test to run setUp")

    def test_correct_behavior(self):
        # Check when the input signal is 1
        self.testInput.setOutputControl('aluzero', 1)
        expectedvalue = 0

        self.NOTgate.readControlSignals()
        self.NOTgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)

        # Check when the input signal is 0
        self.testInput.setOutputControl('aluzero', 0)
        expectedvalue = 1

        self.NOTgate.readControlSignals()
        self.NOTgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)
        
if __name__ == "__main__":
    unittest.main()
                                                      