'''
Code written for inf-2200, University of Tromso
'''

import sys
from mipsSimulator import MIPSSimulator
from common import Break

def runSimulatorIF(sim):
    while (1):
        sim.tick()
        sim.registerFile.printAll()
        sim.dataMemory.printAll()
        if sim.instructionMemory.BREAK == True:
            sim.registerFile.printAll()
            sim.dataMemory.printAll()
            raise Break("bye bitces")


if __name__ == '__main__':
    assert (len(sys.argv) == 2), 'Usage: python %s memoryFile' % (sys.argv[0],)
    memoryFile = sys.argv[1]
    simulator = MIPSSimulator(memoryFile)
    runSimulatorIF(simulator)
    print()

