from cpuElement import CPUElement
from testElement import TestElement
import unittest

class ORgate(CPUElement):
    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)

        assert(len(inputSources) == 0), 'The Not-gate should not have any inputs'
        assert(len(outputValueNames) == 0), 'The Not-gate should not have any outputs'
        assert(len(control) == 2), 'The Not-gate should have two control signals'
        assert(len(outputSignalNames) == 1), 'The Not-gate should have one control output'

        # Assigning the input signals
        self.BEQ = control[0][1]
        self.BNE = control[1][1]

        # Assigning the output signal
        self.controlOutput = outputSignalNames[0]

    def writeOutput(self):
        pass

    def setControlSignals(self):
        super().setControlSignals()

        # Setting the inputsignals
        input1 = self.controlSignals[self.BEQ]
        input2 = self.controlSignals[self.BNE]

        # Perform an AND operation as the AND gate does
        output = input1 | input2

        # Updating the value in the map with output control signals
        self.outputControlSignals[self.controlOutput] = output
            

class TestOR(unittest.TestCase):
    def setUp(self):
        self.ORgate = ORgate()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            [],
            [],
            ['BEQ', 'BNE']
        )

        self.ORgate.connect(
            [],
            [],
            [(self.testInput, 'BEQ'), (self.testInput, 'BNE')],
            ['Outputsignal']
        )

        self.testOutput.connect(
            [],
            [],
            [(self.ORgate, 'Outputsignal')],
            []
        )

    def test_dummy(self):
        self.assertTrue(True, "Dummy test to run setUp")

    def test_correct_behavior(self):
        # Check when the input signals are both 1 
        self.testInput.setOutputControl('BEQ', 1)
        self.testInput.setOutputControl('BNE', 1)
        expectedvalue = 1

        self.ORgate.readControlSignals()
        self.ORgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)

        # Check when input1 is 1 and input2 is 0
        self.testInput.setOutputControl('BEQ', 1)
        self.testInput.setOutputControl('BNE', 0)
        expectedvalue = 1

        self.ORgate.readControlSignals()
        self.ORgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)

        # Check when input1 is 0 and input2 is 1
        self.testInput.setOutputControl('BEQ', 0)
        self.testInput.setOutputControl('BNE', 1)
        expectedvalue = 1

        self.ORgate.readControlSignals()
        self.ORgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)

        # Check when both inputs are 0
        self.testInput.setOutputControl('BEQ', 0)
        self.testInput.setOutputControl('BNE', 0)
        expectedvalue = 0

        self.ORgate.readControlSignals()
        self.ORgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)
        
if __name__ == "__main__":
    unittest.main()
        