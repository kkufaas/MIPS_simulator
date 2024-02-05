from cpuElement import CPUElement
from testElement import TestElement
import unittest

class ANDgate(CPUElement):
    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)

        assert(len(inputSources) == 0), 'The AND-gate should not have any inputs'
        assert(len(outputValueNames) == 0), 'The AND-gate should not have any outputs'
        assert(len(control) == 2), 'The AND-gate should have two control signals'
        assert(len(outputSignalNames) == 1), 'The AND-gate should have one control output'

        # Assigning the input signals
        self.controlName_Branch = control[0][1]
        self.Alu_zero = control[1][1]

        # Assigning the output signal
        self.controlOutput = outputSignalNames[0]

    def writeOutput(self):
        pass

    def setControlSignals(self):
        super().setControlSignals()

        # Setting the inputsignals
        input1 = self.controlSignals[self.controlName_Branch]
        input2 = self.controlSignals[self.Alu_zero]

        # Perform an AND operation as the AND gate does
        output = input1 & input2

        # Updating the value in the map with output control signals
        self.outputControlSignals[self.controlOutput] = output

class TestANDgate(unittest.TestCase):
    def setUp(self):
        self.ANDgate = ANDgate()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            [],
            [],
            ['cont_Branch', 'Alu_zero']
        )

        self.ANDgate.connect(
            [],
            [],
            [(self.testInput, 'cont_Branch'), (self.testInput, 'Alu_zero')],
            ['Outputsignal']
        )

        self.testOutput.connect(
            [],
            [],
            [(self.ANDgate, 'Outputsignal')],
            []
        )

    def test_dummy(self):
        self.assertTrue(True, "Dummy test to run setUp")

    def test_correct_behavior(self):
        # Check when the input signals are both 1 
        self.testInput.setOutputControl('cont_Branch', 1)
        self.testInput.setOutputControl('Alu_zero', 1)
        expectedvalue = 1

        self.ANDgate.readControlSignals()
        self.ANDgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)

        # Check when input1 is 1 and input2 is 0
        self.testInput.setOutputControl('cont_Branch', 1)
        self.testInput.setOutputControl('Alu_zero', 0)
        expectedvalue = 0

        self.ANDgate.readControlSignals()
        self.ANDgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)

        # Check when input1 is 0 and input2 is 1
        self.testInput.setOutputControl('cont_Branch', 0)
        self.testInput.setOutputControl('Alu_zero', 1)
        expectedvalue = 0

        self.ANDgate.readControlSignals()
        self.ANDgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)

        # Check when both inputs are 0
        self.testInput.setOutputControl('cont_Branch', 0)
        self.testInput.setOutputControl('Alu_zero', 0)
        expectedvalue = 0

        self.ANDgate.readControlSignals()
        self.ANDgate.setControlSignals()
        self.testOutput.readControlSignals()

        output = self.testOutput.controlSignals['Outputsignal']
        self.assertEqual(output, expectedvalue)

if __name__ == "__main__":
    unittest.main()