from cpuElement import CPUElement
from testElement import TestElement
import unittest


class JumpMerge(CPUElement):
    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)
        assert len(inputSources) == 2, 'Jump merge should have 2 inputs'
        assert len(outputValueNames) == 1, 'Jump merge should have 1 output'
        assert len(control) == 0, 'Jump merge should not have any control signal inputs'
        assert len(outputSignalNames) == 0, 'Jump merge should have not output control signal'

        self.address = inputSources[0][1]
        self.pc4 = inputSources[1][1]

        self.jumpAddress = outputValueNames[0]

    def writeOutput(self):
        # To merge the shifted 28 bits and the 4 bit address from PC
        # to get the 32 bit j-type address [31-0]
        input1 = self.inputValues[self.address]
        input2 = self.inputValues[self.pc4]

        self.outputValues[self.jumpAddress] = (input2 & 0xf0000000) + (input1)

class TestJumpMerge(unittest.TestCase):
    def setUp(self):
        self.jmerge = JumpMerge()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            ['address', 'pc4'],
            [],
            []
        )

        self.jmerge.connect(
            [(self.testInput, 'address'), (self.testInput, 'pc4')],
            ['jumpaddress'],
            [],
            []
        )

        self.testOutput.connect(
            [(self.jmerge, 'jumpaddress')],
            [],
            [],
            []
        )
    def test_dummy(self):
        self.assertTrue(True, "Dummy test to run setUp")

    def testCorrectBehavior(self):
        self.testInput.setOutputValue('address', 0xFC00200)
        self.testInput.setOutputValue('pc4', 0xbfc00004)
        expectedValue = 0xbfc00200

        self.jmerge.readInput()
        self.jmerge.writeOutput()

        self.testOutput.readInput()

        output = self.testOutput.inputValues['jumpaddress']
        self.assertEqual(output, expectedValue)

                            
if __name__ == "__main__":
    unittest.main()        