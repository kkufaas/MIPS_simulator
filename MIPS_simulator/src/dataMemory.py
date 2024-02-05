'''
Implements CPU element for Data Memory in MEM stage.

Code written for inf-2200, University of Tromso
'''

from cpuElement import CPUElement
from memory import Memory
import unittest
from testElement import TestElement


class DataMemory(Memory):
    def __init__(self, filename):
        Memory.__init__(self, filename)

    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)

        '''Remove this and replace with your implementation!
        raise AssertionError("connect not implemented in class DataMemory!")'''

        # Ensure the correct number of input and output connections
        assert len(inputSources) == 2, 'DataMemory should have two inputs: Address and Write Data.'
        assert len(outputValueNames) == 1, 'DataMemory should have one output: Read Data.'
        assert (len(control) == 2), 'DataMemory has two control signals'
        assert (len(outputSignalNames) == 0), 'Data memory should not have any control output'

        self.inputField_address = inputSources[0][1]  # Input #1, Address, could be connected to an output of the ALU
        self.inputField_writeData = inputSources[1][1]  # Input #2, Data input for write operations
        self.outputField_readData = outputValueNames[0]  # Output for read operations
        self.control_readEnable = control[0][1]  # Control signal for read operations
        self.control_writeEnable = control[1][1]  # Control signal for write operations

    def writeOutput(self):
        address = self.inputValues[self.inputField_address]
        write_data = self.inputValues[self.inputField_writeData]
        
        dataMemoryControlRead = self.controlSignals[self.control_readEnable]
        dataMemoryControlWrite = self.controlSignals[self.control_writeEnable]

        if not isinstance(dataMemoryControlRead, int) or dataMemoryControlRead not in (0, 1):
            raise AssertionError(
                f"Invalid dataMemoryControlRead control signal value: {dataMemoryControlRead}. It should be either 0 or 1.")

        if not isinstance(dataMemoryControlWrite, int) or dataMemoryControlWrite not in (0, 1):
            raise AssertionError(
                f"Invalid dataMemoryControlWrite control signal value: {dataMemoryControlWrite}. It should be either 0 or 1.")

        # Reading from Memory
        if dataMemoryControlRead == 1:
            print(f"DM: read {hex(address)}")
            self.outputValues[self.outputField_readData] = self.memory.get(address, 0)
            
        # Writing to Memory
        elif dataMemoryControlWrite == 1:
            # Write the given data to the memory at the given address
            self.memory[address] = write_data
            self.outputValues[self.outputField_readData] = 1
        # ''' raise AssertionError("writeOutput not implemented in class DataMemory!")'''
        else:
            self.outputValues[self.outputField_readData] = 0




class TestDataMemory(unittest.TestCase):
    def setUp(self):
        # Create an instance of DataMemory with a sample memory file
        self.dataMemory = DataMemory("src/add.mem")

        # Create test elements to simulate inputs and outputs
        self.testInput = TestElement()
        self.testOutput = TestElement()

        self.testInput.connect(
            [],
            ['address', 'writeData'],  # corrected input field names
            [],
            ['dataMemoryControlRead', 'dataMemoryControlWrite']  # corrected control signal names
        )

        self.dataMemory.connect(
            [(self.testInput, 'address'), (self.testInput, 'writeData')],  # corrected input field names
            ['readData'],  # corrected output field name
            [(self.testInput, 'dataMemoryControlRead'), (self.testInput, 'dataMemoryControlWrite')],  # corrected control signal names
            []
        )

        self.testOutput.connect(
            [(self.dataMemory, 'readData')],  # corrected output field name
            [],
            [],
            []
        )

    def test_dummy(self):
        self.assertTrue(True, "Dummy test to run setUp")

    def test_correct_behavior_reading_then_writing(self):
        test_address = 0xbfc00000  # Use the address from your add.mem file
        self.testInput.setOutputValue('address', test_address)
        self.testInput.setOutputValue('writeData', 20)

        # Both reading and writing are enable
        self.testInput.setOutputControl('dataMemoryControlRead', 0)
        self.testInput.setOutputControl('dataMemoryControlWrite', 1)

        self.dataMemory.readInput()
        self.dataMemory.readControlSignals()
        self.dataMemory.writeOutput()

        # Both reading and writing are enable
        self.testInput.setOutputControl('dataMemoryControlRead', 1)
        self.testInput.setOutputControl('dataMemoryControlWrite', 0)

        self.dataMemory.readInput()
        self.dataMemory.readControlSignals()
        self.dataMemory.writeOutput()

        self.testOutput.readInput()
        self.dataMemory.readControlSignals()
        self.dataMemory.writeOutput()  # This should read 20 from address 0xbfc00000
        self.testOutput.readInput()

        print(self.dataMemory.memory.get(test_address,
                                         "Still not in memory"))  # Check if 20 is written to address 0xbfc00000
        # print(self.testOutput.inputValues)  # Print the contents of inputValues

        output = self.testOutput.inputValues['readData']
        self.assertEqual(output, 20)

    def test_correct_behavior_only_read_enabled(self):
        test_address = 0xbfc00000  # Using the address from your add.mem file
        self.testInput.setOutputValue('address', test_address)

        # Enable only reading
        self.testInput.setOutputControl('dataMemoryControlRead', 1)
        self.testInput.setOutputControl('dataMemoryControlWrite', 0)

        self.dataMemory.readInput()
        self.dataMemory.readControlSignals()
        self.dataMemory.writeOutput()
        self.testOutput.readInput()

        output = self.testOutput.inputValues['readData']
        expected_value = self.dataMemory.memory.get(test_address, 0)  # Replace 0 with the default read value.
        self.assertEqual(output, expected_value)

    def test_correct_behavior_only_write_enabled(self):
        test_address = 0xbfc00000  # Using the address from your add.mem file
        self.testInput.setOutputValue('address', test_address)
        self.testInput.setOutputValue('writeData', 30)  # Arbitrary value to write

        # Enable only writing
        self.testInput.setOutputControl('dataMemoryControlRead', 0)
        self.testInput.setOutputControl('dataMemoryControlWrite', 1)

        self.dataMemory.readInput()
        self.dataMemory.readControlSignals()
        self.dataMemory.writeOutput()

        # Now read directly from the memory to confirm the write
        output = self.dataMemory.memory.get(test_address, 0)  # Replace 0 with the default read value.
        self.assertEqual(output, 30)

    def test_correct_behavior_neither_read_nor_write_enabled(self):
        test_address = 0xbfc00000  # Using the address from your add.mem file
        self.testInput.setOutputValue('address', test_address)
        self.testInput.setOutputValue('writeData', 40)  # Arbitrary value

        # Disable both reading and writing
        self.testInput.setOutputControl('dataMemoryControlRead', 0)
        self.testInput.setOutputControl('dataMemoryControlWrite', 0)

        initial_state = dict(self.dataMemory.memory)  # Store the initial state of the memory

        self.dataMemory.readInput()
        self.dataMemory.readControlSignals()
        self.dataMemory.writeOutput()
        self.testOutput.readInput()

        # Check if the memory state has changed
        self.assertDictEqual(self.dataMemory.memory, initial_state)

        # Check if the output is default read value (e.g. 0)
        output = self.testOutput.inputValues['readData']
        self.assertEqual(output, 0)  # Replace with the default read value.

    def assert_callback(self, control_signal_read, control_signal_write):
        # print("Setting Control Signals: ", control_signal_read, control_signal_write)  # Debug print
        self.testInput.setOutputControl('dataMemoryControlRead', control_signal_read)
        self.testInput.setOutputControl('dataMemoryControlWrite', control_signal_write)
        self.dataMemory.readControlSignals()
        # print("Control Signals after readControlSignals: ", self.dataMemory.controlSignals)  # Debug print
        self.dataMemory.writeOutput()


if __name__ == '__main__':
    unittest.main()
