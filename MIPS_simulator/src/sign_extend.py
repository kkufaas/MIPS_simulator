import unittest
from cpuElement import CPUElement
from testElement import TestElement


class Sign_Extend(CPUElement):
    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        # Print the input arguments to see their values
        print(f"inputSources: {inputSources}")
        print(f"outputValueNames: {outputValueNames}")
        print(f"control: {control}")
        print(f"outputSignalNames: {outputSignalNames}")
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)

        assert (len(inputSources) == 1), 'sign_extend should have one inputs'
        assert (len(outputValueNames) == 1), 'sign_extend has only one output'
        assert (len(control) == 0), 'sign_extend does not have any control signal'
        assert (len(outputSignalNames) == 0), 'sign_extend does not have any control output'

        self.inputZero = inputSources[0][1]
        self.outputName = outputValueNames[0]

    def writeOutput(self):
        sign_value = self.inputValues[self.inputZero]  # 16-bit input
        # checks if the sign bit is set
        if sign_value & 0x8000:
            # if the sign bit is set, extend with 1s (sign bit extension)
            extended_value = sign_value | 0xFFFF0000
        else:
            # if the sign bit is not set, extend with 0s
            extended_value = sign_value
        self.outputValues[self.outputName] = extended_value


class TestSign_Extend(unittest.TestCase):
    def setUp(self):
        self.siex = Sign_Extend()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            ['dataA'],
            [],
            []
        )

        self.siex.connect(
            [(self.testInput, 'dataA')],
            ['siexData'],
            [],
            []
        )

        self.testOutput.connect(
            [(self.siex, 'siexData')],
            [],
            [],
            [],
        )

    def test_correct_behavior(self):
        ' Testvalues when positive '
        testValue1 = 0b0000000000000010
        correctValue1 = 0b00000000000000000000000000000010
        ' Testvalues when negative'
        testValue2 = 0b1111111111111110
        correctValue2 = 0b11111111111111111111111111111110

        ' Test 1 with positive values '
        # Set dataA to testValue1
        self.testInput.setOutputValue('dataA', testValue1)

        self.siex.readInput()  # Reads the input form testInput
        self.siex.writeOutput()  # Performs the operation set in the function
        self.testOutput.readInput()  # Reads the output from siex
        output = self.testOutput.inputValues['siexData']  # Gets the result

        # Checks if the output matches the expected sign-extended value
        self.assertEqual(output, correctValue1)

        ' Test 2 with negative values '
        # Set dataA to testValue2
        self.testInput.setOutputValue('dataA', testValue2)

        self.siex.readInput()  # Reads the input form testInput
        self.siex.writeOutput()  # Performs the operation set in the function
        self.testOutput.readInput()  # Reads the output from siex
        output = self.testOutput.inputValues['siexData']  # Gets the result

        # Checks if the output matches the expected sign-extended value
        self.assertEqual(output, correctValue2)


if __name__ == "__main__":
    unittest.main()
