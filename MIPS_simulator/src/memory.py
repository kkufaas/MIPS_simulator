'''
Implements base class for memory elements.

Note that since both DataMemory and InstructionMemory are subclasses of the Memory
class, they will read the same memory file containing both instructions and data
memory initially, but the two memory elements are treated separately, each with its
own, isolated copy of the data from the memory file.

Code written for inf-2200, University of Tromso
'''

from cpuElement import CPUElement
import common


class Memory(CPUElement):
    def __init__(self, filename):
        if not isinstance(filename, str):
            raise TypeError("Filename must be a string")
        '''Dictionary mapping memory addresses to data
        # Both key and value must be of type 'long'''
        self.memory = {}
        self.initializeMemory(filename)

    def initializeMemory(self, filename):
        '''
        Helper function that reads initializes the data memory by reading input
        data from a file.
        '''
        '''Implementation MUST populate the dictionary in self.memory!
        # The memory (data and instruction memory) needs to be initialized with some values (instructions and data)
        # from a file before the simulation starts. This dictionary serves as the primary data structure
        # to hold the memory contents of the simulated CPU during execution.'''
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                # Skip comment lines
                if line.startswith("0x"):
                    
                # Splitting the line by tab to separate address, content and comments
                # print(repr(line))
                    parts = line.split('\t')
                    if len(parts) < 2:
                        print(f"Error in line: {line.strip()}")
                        raise ValueError("Each line in the memory file must contain at least an address and a "
                                        "content value separated by a tab")

                    # Extracting address and content, converting them from hex to int
                    address = int(parts[0], 16)
                    content = int(parts[1], 16)

                    # Adding the address and content to the memory dictionary
                    self.memory[address] = content

        '''raise AssertionError("initializeMemory not implemented in class Memory!")'''

    def printAll(self):
        if not self.memory:
            print("Warning: Memory is empty.")
            return

        for key in sorted(self.memory.keys()):
            print("%s\t=> %s\t(%s)" % (
                hex(int(key)), common.fromUnsignedWordToSignedWord(self.memory[key]), hex(int(self.memory[key]))))



