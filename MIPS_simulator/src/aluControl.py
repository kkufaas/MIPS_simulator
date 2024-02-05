import unittest
from cpuElement import CPUElement
from testElement import TestElement

class ALUControl(CPUElement):
    def connect(self, inputSources, outputValueNames, control, outputSignalName):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalName)

        assert len(inputSources) == 1, 'ALUControl should have one input source'
        assert len(outputValueNames) == 0, 'ALUControl should not have output values'
        assert len(control) == 1, 'ALUControl should have one control input signal'
        assert len(outputSignalName) == 1, 'ALUControl should have one control output'

        # Assigning the input data
        self.funct = inputSources[0][1]

        # Assigning the input signal
        self.ALUOp = control[0][1]

        # Assigning the output signal field
        self.alucontrol = outputSignalName[0]

    def writeOutput(self):
        aluop = self.controlSignals[self.ALUOp]
        funct = self.inputValues[self.funct]
        alucontrol = 0b0000
        if aluop == 0b10:               # For R-type instructions
            if funct == 0b100000:       # For add operations
                alucontrol = 0b0010 # 2
            elif funct == 0b100010:     # For subtract operations
                alucontrol = 0b0110 # 6
            elif funct == 0b100100:     # For logical AND operations
                alucontrol = 0b0000 # 0
            elif funct == 0b100101:     # For logical OR operations
                alucontrol = 0b0001 # 1
            elif funct == 0b101010:     # For set on less than operations
                alucontrol = 0b0111 # 7
            elif funct == 0b100111:       # For logical NOR operations
                alucontrol = 0b1100 # 12
            elif funct == 0b0:          # For the NOP (no operation)
                alucontrol = 0b0010
            elif funct == 0xd:          # For the BREAK (no operation)
                alucontrol = 0b0010
            else:
                raise ValueError(f"The given funct field value is not recognized: {funct}")
        elif aluop == 0b01:             # For branch operations
            alucontrol = 0b0110 # 6
        elif aluop == 0b00:             # For I-type instructions
            alucontrol = 0b0010 # 2
        else:
            raise ValueError(f"The given AluOp value is not recognized: {aluop}")

        self.outputControlSignals[self.alucontrol] = alucontrol
        print(f"AC: the signal sent to alu: {self.outputControlSignals}")

class TestALU(unittest.TestCase):
    def setUp(self):
        self.ALUControl = ALUControl()
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            ['funct'],
            [],
            ['ALUOp']
        )

        self.ALUControl.connect(
            [(self.testInput, 'funct')],
            [],
            [(self.testInput, 'ALUOp')],
            ['ALUControl']
        )

        self.testOutput.connect(
            [],
            [],
            [(self.ALUControl, 'ALUControl')],
            []
        )

    def run_test_ALUControl(self, funct, aluop, expectedSignal):
        self.testInput.setOutputValue('funct', funct)
        self.testInput.setOutputControl('ALUOp', aluop)
        
        self.testInput.writeOutput()
        self.testInput.setControlSignals()

        self.ALUControl.readControlSignals()
        self.ALUControl.readInput()
        self.ALUControl.writeOutput()
        self.ALUControl.setControlSignals()

        self.testOutput.readInput()
        self.testOutput.readControlSignals()

        self.assertEqual(self.testOutput.controlSignals['ALUControl'], expectedSignal)

    def testADD(self):
        self.run_test_ALUControl(0b100000, 0b10, 0b0010)

    def testSUB(self):
        self.run_test_ALUControl(0b100010, 0b10, 0b0110)
    
    def testAND(self):
        self.run_test_ALUControl(0b100100, 0b10, 0b0000)
    
    def testOR(self):
        self.run_test_ALUControl(0b100101, 0b10, 0b0001)

    def testSLT(self):
        self.run_test_ALUControl(0b101010, 0b10, 0b0111)

    def testNOR(self):
        self.run_test_ALUControl(0b100111, 0b10, 0b1100)

    def testBranches(self):
        self.run_test_ALUControl(0b0, 0b01, 0b0110)
    
    def testNOP(self):
        self.run_test_ALUControl(0b0, 0b10, 0b0010)
    
    def testBreak(self):
        self.run_test_ALUControl(0xd, 0b10, 0b0010)
    
    def testItype(self):
        self.run_test_ALUControl(0b0, 0b00, 0b0010)

if __name__ == "__main__":
    unittest.main()



            
                


