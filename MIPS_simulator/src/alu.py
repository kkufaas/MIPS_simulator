import unittest
from cpuElement import CPUElement
from testElement import TestElement
import common
from common import Overflow

class ALU(CPUElement):
    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        '''
        Connect ALU to input sources and controller
        
        Note that the first inputSource is input zero, and the second is input 1
        '''
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)
        
        assert(len(inputSources) == 2), 'ALU should have two inputs'
        assert(len(outputValueNames) == 1), 'ALU has only one output'
        assert(len(control) == 1), 'ALU has one control signal'
        assert(len(outputSignalNames) == 1), 'ALU has one control output'
        
        self.inputReg = inputSources[0][1]
        self.inputMux = inputSources[1][1]
        self.outputName = outputValueNames[0]
        self.controlName = control[0][1]
        self.outputZero = outputSignalNames[0]

    def writeOutput(self):
        inputA = self.inputValues[self.inputReg]
        inputB = self.inputValues[self.inputMux]
        controlSignal = self.controlSignals[self.controlName]
        #print(f"\nalu: inputa value: {hex(inputA)}, inputb value: {hex(inputB)}, controlsignal from alu control: {bin(controlSignal), controlSignal}")

        signedA = common.fromUnsignedWordToSignedWord(inputA)
        signedB = common.fromUnsignedWordToSignedWord(inputB)

        result = 0

        # Performs the ALU operations based on the given control signal
        if controlSignal == 0b0111:        # set on less than
            # If inputA is less than inputB, then the result is set to be 1
            if signedA < signedB:
                result = 1
            else:       # If not the result is set to be zero
                result = 0
        elif controlSignal == 0b0010:        # add
            # Adding inputA and inputB together
            result = (inputA + inputB) & 0xFFFFFFFF  
            if (result > 0xFFFFFFFF) | (result < -0x80000000):
                raise common.Overflow("Overflow detected: add")
        elif controlSignal == 0b0110:        # subtract
            # Calcualting the subraction of inputB from inputA
            result = inputA - inputB & 0xFFFFFFF
            if (result < -0x80000000):
                raise common.Overflow("Overflow detected: sub")
        elif controlSignal == 0b0000:        # the logical AND operator
            # Calculating inputA AND inputB, using the built in & for AND operations
            result = inputA & inputB
        elif controlSignal == 0b0001:         # the logical OR operator
            # Calculating inputA OR inputB, using the built in | for OR operations
            result = inputA | inputB
        elif controlSignal == 0b1100:        # the logical NOR operator
            # According to the NOR truth table, when both are 0, the result should be 1
            if inputA == 0 and inputB == 0:
                result = 1
            else:   # All the other should result in 0, according to the truth table
                result = 0
            
        else:       # if a controlsignal is given, but it is not any of the above, a valueError is raised
            raise ValueError(f"The given control signal is not recognized: {controlSignal}")
        
        print(f"alu: resultatet er: {hex(result)}")   # Debug print to check the calculated result
        self.outputValues[self.outputName] = result     # Updating the output value to be the result
       
    def setControlSignals(self):
        super().setControlSignals()

        if self.outputValues[self.outputName] == 0:
            self.outputControlSignals[self.outputZero] = 1
        else:
            self.outputControlSignals[self.outputZero] = 0

class TestALU(unittest.TestCase):
    def setUp(self):
        self.ALU = ALU()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            ['inputReg', 'inputMux'],
            [],
            ['ALUControl']
        )

        self.ALU.connect(
            [(self.testInput, 'inputReg'), (self.testInput, 'inputMux')],
            ['ALUresult'],
            [(self.testInput, 'ALUControl')],
            ['outputZero']
        )

        self.testOutput.connect(
            [(self.ALU, 'ALUresult')],
            [],
            [(self.ALU, 'outputZero')],
            []
        )

    def run_test_ALU(self, inputA, inputB, cont_input, expectedValue, expectedSignal):
        self.testInput.setOutputValue('inputReg', inputA)
        self.testInput.setOutputValue('inputMux', inputB)
        self.testInput.setOutputControl('ALUControl', cont_input)
        
        self.testInput.writeOutput()
        self.testInput.setControlSignals()

        self.ALU.readControlSignals()
        self.ALU.readInput()
        self.ALU.writeOutput()
        self.ALU.setControlSignals()

        self.testOutput.readInput()
        self.testOutput.readControlSignals()

        self.assertEqual(self.testOutput.inputValues['ALUresult'], expectedValue)
        if expectedSignal:
            self.assertEqual(self.testOutput.controlSignals, expectedSignal)

    def testADD(self):
        self.run_test_ALU(0b0001, 0b0001, 0b0010, 0b0010, None)

    def testSUB(self):
        self.run_test_ALU(0b0110, 0b0001, 0b0110, 0b0101, None)

    def testSUB_zero(self):
        self.run_test_ALU(0b0001, 0b0001, 0b0110, 0b0000, {'outputZero': 1})

        self.run_test_ALU(0b0110, 0b0001, 0b0110, 0b0101, {'outputZero': 0})
    
    def testAND(self):
        self.run_test_ALU(0b00001111, 0b00111100, 0b0000, 0b00001100, None)
    
    def testOR(self):
        self.run_test_ALU(0b00001111, 0b00111100, 0b0001, 0b00111111, None)
        self.run_test_ALU(0b10101010, 0b11110000, 0b0001, 0b11111010, None)


if __name__ == "__main__":
    unittest.main()
