'''
Code written for inf-2200, University of Tromso
'''

from add import Add
from constant import Constant
from instructionMemory import InstructionMemory
from pc import PC

from sign_extend import Sign_Extend
from shiftLeft16 import ShiftLeft16
from registerFile import RegisterFile
from control import Control
from bufferGate import BufferGate

from shiftLeft2 import ShiftLeft2
from jumpmerge import JumpMerge
from notgate import Not
from ANDgate import ANDgate
from orgate import ORgate
from mux import Mux
from aluControl import ALUControl
from alu import ALU

from dataMemory import DataMemory

from common import Break


class MIPSSimulator():
    '''Main class for MIPS pipeline simulator.

    Provides the main method tick(), which runs pipeline
    for one clock cycle.

    '''

    def __init__(self, memoryFile):
        self.nCycles = 0  # Used to hold number of clock cycles spent executing instructions
        #IF stage
        
        self.constant4 = Constant(4)
        self.adder = Add()
        self.instructionMemory = InstructionMemory(memoryFile)
        self.pc = PC(self.startAddress())
        
        #ID stage
        self.shifter1 = ShiftLeft2()
        self.jumpmerge = JumpMerge()
        self.control = Control()
        self.bufferGate = BufferGate()
        self.mux1 = Mux()
        self.registerFile = RegisterFile()
        self.signExtender = Sign_Extend()
        self.shifter16 = ShiftLeft16()
        self.mux3 = Mux()

        #EX stage
        self.mux2 = Mux()
        self.adderAlu = Add()
        self.shifter2 = ShiftLeft2()
        self.notgate = Not()
        self.andequal = ANDgate()
        self.andnotequal = ANDgate()
        self.orgate = ORgate()
        
        self.alucontrol = ALUControl()
        self.alu = ALU()

        #MEM stage
        self.mux4 = Mux()
        self.mux5 = Mux()
        self.dataMemory = DataMemory(memoryFile)


        #WriteBack stage
        self.mux6 = Mux()
        # legge til registerFila en gan til i writeback stage
        self.elements = [self.pc, self.instructionMemory, self.constant4, self.adder, self.control,
                         self.registerFile, self.signExtender, self.shifter1, self.jumpmerge,
                         self.shifter16, self.alucontrol, self.mux3, self.shifter2, self.adderAlu,
                         self.mux2, self.alu,  
                         self.notgate, self.andequal, self.andnotequal, self.orgate, self.mux4,
                         self.mux5, self.dataMemory, self.mux6, self.bufferGate, self.mux1, self.registerFile
                        ]
                        
        self.connectCPUElements()

    def connectCPUElements(self):
        #IF stage
        self.pc.connect(
            [(self.mux5, 'mux5Out')],
            ['currentAddress'],
            [],
            []
        )

        self.constant4.connect(
            [],
            ['constant'],
            [],
            []
        )

        self.adder.connect(
            [(self.pc, 'currentAddress'), (self.constant4, 'constant')],
            ['nextAddress'],
            [],
            []
        )

        self.instructionMemory.connect(
            [(self.pc, 'currentAddress')],
            ['instruction', 'jump_target', 'opcode', 'rs', 'rt', 'rd', 'imm', 'func'],
            [],
            []
        )

        
        # ID stage
        self.control.connect(
            [(self.instructionMemory, 'opcode')],
            [],
            [],
            Control.outputSignalNames
        )

    
        self.mux1.connect(
            [(self.instructionMemory, 'rt'), (self.instructionMemory, 'rd') ],
            ['mux1Out'],
            [(self.control, 'outputField_RegDst')],
            []
        )

        self.shifter1.connect(
            [(self.instructionMemory, 'jump_target')],
            ['shifted1'],
            [],
            []
        )

        self.jumpmerge.connect(
            [(self.shifter1, 'shifted1'), (self.adder, 'nextAddress')],
            ['jumpAddress'],
            [],
            []
        )

        self.registerFile.connect(
            [(self.instructionMemory, 'rs'), (self.instructionMemory, 'rt'), (self.mux1, 'mux1Out'), (self.mux6, 'mux6Out')],
            ['ReadData1', 'ReadData2'],
            [(self.bufferGate, 'regWriteActual')],
            []
        )

        self.signExtender.connect(
            [(self.instructionMemory, 'imm')],
            ['immediate'],
            [],
            []
        )

        # legg til shift left 16 og en mux til her
        self.shifter16.connect(
            [(self.signExtender, 'immediate')],
            ['shift16out'],
            [],
            []
        )

        self.mux3.connect(
            [(self.signExtender, 'immediate'), (self.shifter16, 'shift16out')],
            ['mux3Out'],
            [(self.control, 'outputField_Immediate')],
            []
        )

        # EX stage
        self.mux2.connect(
            [(self.registerFile, 'ReadData2'), (self.mux3, 'mux3Out')],
            ['mux2Out'],
            [(self.control, 'outputField_ALUSrc')],
            []
        )

        self.shifter2.connect(
            [(self.mux3, 'mux3Out')],
            ['shifted2'],
            [],
            []
        )

        self.adderAlu.connect(
            [(self.adder, 'nextAddress'), (self.shifter2, 'shifted2')],
            ['addResult'],
            [],
            []
        )

        self.alucontrol.connect(
            [(self.instructionMemory, 'func')],
            [],
            [(self.control, 'outputField_ALUOp')],
            ['aluControl']
        )

        self.alu.connect(
            [(self.registerFile, 'ReadData1'), (self.mux2, 'mux2Out')],
            ['aluResult'],
            [(self.alucontrol,'aluControl')],
            ['zero']
        )

        self.andequal.connect(
            [],
            [],
            [(self.control, 'outputField_BEQ'), (self.alu, 'zero')],
            ['BEQ']
        )

        self.notgate.connect(
            [],
            [],
            [(self.alu, 'zero')],
            ['notout']
        )

        self.andnotequal.connect(
            [],
            [],
            [(self.control, 'outputField_BNE'),(self.notgate, 'notout')],
            ['BNE']
        )

        self.orgate.connect(
            [],
            [],
            [(self.andequal, 'BEQ'), (self.andnotequal, 'BNE')],
            ['branch']
        )

        #MEM stage
        self.mux4.connect(
            [(self.adder, 'nextAddress'), (self.adderAlu, 'addResult')],
            ['mux4Out'],
            [(self.orgate, 'branch')],
            []
        )

        self.mux5.connect(
            [(self.mux4, 'mux4Out'), (self.jumpmerge, 'jumpAddress')],
            ['mux5Out'],
            [(self.control, 'outputField_Jump')],
            []
        )

        self.dataMemory.connect(
            [(self.alu, 'aluResult'), (self.registerFile, 'ReadData2')],
            ['readDataMem'],
            [(self.control, 'outputField_MemRead'), (self.control, 'outputField_MemWrite')],
            []
        )

        #WriteBack stage
        self.bufferGate.connect(
            [],
            [],
            [(self.control, 'outputField_RegWrite')],
            ['regWriteActual']
        )

        self.mux6.connect(
            [(self.alu, 'aluResult'), (self.dataMemory, 'readDataMem')],
            ['mux6Out'],
            [(self.control, 'outputField_MemtoReg')],
            []
        )

    def startAddress(self):
        '''
        Returns first instruction from instruction memory
        '''
        first_instruction = next(iter(sorted(self.instructionMemory.memory.keys())))
        return first_instruction

    def clockCycles(self):
        '''Returns the number of clock cycles spent executing instructions.'''
        return self.nCycles

    def dataMemory(self):
        '''Returns dictionary, mapping memory addresses to data, holding
        data memory after instructions have finished executing.'''
        return self.dataMemory.memory

    def registerFile(self):
        '''Returns dictionary, mapping register numbers to data, holding
        register file after instructions have finished executing.'''
        return self.registerFile.register

    def printDataMemory(self):
        self.dataMemory.printAll()

    def printRegisterFile(self):
        self.registerFile.printAll()

    def tick(self):
        '''Execute one clock cycle of pipeline.'''

        self.nCycles += 1
        self.pc.writeOutput()

        if self.instructionMemory.BREAK == True:
            raise Break("bye bitces")


        for elem in self.elements:
            if elem == self.pc and self.nCycles == 1:
                pass
            else:
                elem.readControlSignals()
                elem.readInput()
                elem.writeOutput()
                elem.setControlSignals()
        print(f"MipsSimulator: cycle number: {self.nCycles}")

