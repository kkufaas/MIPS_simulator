import unittest
from cpuElement import CPUElement
from testElement import TestElement


class ShiftLeft2(CPUElement):
    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)
        assert len(inputSources) == 1, 'ShiftLeft2 should have only one input.'
        assert len(outputValueNames) == 1, 'ShiftLeft2 should have only one output.'
        assert len(control) == 0, 'ShiftLeft2 should have no control signal inputs.'
        assert len(outputSignalNames) == 0, 'ShiftLeft2 should have no control signal outputs.'

        self.inputField_sliceInstruction = inputSources[0][1]  # The input field for the slice of instruction
        self.outputField_shiftedInstruction = outputValueNames[0]  # The output field for the shifted instruction

    def writeOutput(self):
        slice_instruction = self.inputValues[self.inputField_sliceInstruction]  # Get the input value
        shift = 2
        shifted_instruction = (slice_instruction << shift) & 0xFFFFFFFF  # Perform a left shift by 2 on the binary value
        self.outputValues[self.outputField_shiftedInstruction] = shifted_instruction  # Set the output value


class TestShiftLeft2(unittest.TestCase):
    def setUp(self):
        self.shiftLeft2 = ShiftLeft2()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            ['inputField_sliceInstruction'],
            [],
            []
        )

        self.shiftLeft2.connect(
            [(self.testInput, 'inputField_sliceInstruction')],
            ['shifted_instruction'],
            [],
            []
        )

        self.testOutput.connect(
            [(self.shiftLeft2, 'shifted_instruction')],
            [],
            [],
            []
        )

    def test_correct_behavior(self):
        # Prepare test case
        slice_instruction = 0b0010  # Assume 2 as binary input for simplicity
        expected_output = 0b1000  # Left shifting by 2 results in 8 in binary

        # Set the input value
        self.testInput.setOutputValue('inputField_sliceInstruction', slice_instruction)

        # Execute the logic
        self.shiftLeft2.readInput()
        self.shiftLeft2.writeOutput()
        self.testOutput.readInput()

        # Get the output value
        actual_output = self.testOutput.inputValues['shifted_instruction']
        # Assert the output value is as expected
        self.assertEqual(actual_output, expected_output,
                         f"Expected output to be {expected_output} but got {actual_output}")


if __name__ == '__main__':
    unittest.main()
