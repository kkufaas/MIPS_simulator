import unittest
from cpuElement import CPUElement
from testElement import TestElement


class IF_ID_Register(CPUElement):
    def __init__(self):
        self.slice_names = ['jump_target', 'opcode', 'rs', 'rt', 'rd', 'imm', 'func']

    def connect(self, inputSources, outputValueNames, control, outputSignalNames):
        CPUElement.connect(self, inputSources, outputValueNames, control, outputSignalNames)

        assert len(inputSources) == 8, 'IFID should have 2 input sources, add address and sliced instruction fromIM'
        assert len(outputValueNames) == 8, 'IFID should have 2 output values, add address and sliced instruction from IM '
        #assert len(control) == 2, 'DataMemory has two control signals (inputs)'
        assert len(outputSignalNames) == 0, 'No control output'

        self.add_address_input = inputSources[0][1]
        self.sliced_instruction_inputs = {name: inputSources[i + 1][1] for i, name in enumerate(self.slice_names)}

        self.add_address_output = outputValueNames[0]
        self.sliced_instruction_outputs = {name: outputValueNames[i + 1] for i, name in enumerate(self.slice_names)}

        #self.control_hazardDetectionUnit = control[0][1]  # Input control signal from Hazard Detection Unit
        #self.control_ifFlush = control[1][1]  # Input control signal from Control, IF.Flush

    def writeOutput(self):

        #ifFlushControl = self.controlSignals[self.control_ifFlush]
        #hazardDetection = self.controlSignals[self.control_hazardDetectionUnit]
        self.outputValues[self.add_address_output] = self.inputValues[self.add_address_input]

        # if not isinstance(ifFlushControl, int) or ifFlushControl not in (0, 1):
        #     raise AssertionError(
        #         f"Invalid ifFlushControl control signal value: {ifFlushControl}. It should be either 0 or 1.")
        #
        # if not isinstance(hazardDetection, int) or hazardDetection not in (0, 1):
        #     raise AssertionError(
        #         f"Invalid hazardDetection control signal value: {hazardDetection}. It should be either 0 or 1.")
        #
        # if ifFlushControl == 0 and hazardDetection == 0:
        #     # Set the output_address value using the value of add_address input
        for name in self.slice_names:
            self.outputValues[self.sliced_instruction_outputs[name]] = self.inputValues[
                self.sliced_instruction_inputs[name]]

        # Clear the instruction values to zero
        # elif hazardDetection == 0 and ifFlushControl == 1:
        #     self.outputValues[self.add_address_output] = self.inputValues[self.add_address_input]
        #     for name in self.slice_names:
        #         self.outputValues[self.sliced_instruction_outputs[name]] = self.inputValues[
        #             self.sliced_instruction_inputs[name]]
        #
        # # Do nothing, just keep the current values
        # elif hazardDetection == 1 and ifFlushControl == 0:
        #     for name in self.slice_names:
        #         self.outputValues[self.sliced_instruction_outputs[name]] = '0b' + '0' * len(
        #             self.inputValues[self.sliced_instruction_inputs[name]])
        #
        # elif hazardDetection == 1 and ifFlushControl == 1:
        #     for name in self.slice_names:
        #         self.outputValues[self.sliced_instruction_outputs[name]] = self.inputValues[
        #             self.sliced_instruction_inputs[name]]

            # Update the instruction part of IF/ID with NOP (all zeroes).
        print(f"IF_ID Output Values after write: {self.outputValues}")


    def printConnectionInfo(self, element, name):
        print(f"---- {name} ----")
        print("Input Sources:")
        for src, name in element.inputSources:
            print(f"{src} - {name}")

        print("Output Values:")
        for name, value in element.outputValues.items():
            print(f"{name} - {value}")

    def readInput(self):
        for src, name in self.inputSources:
            value = src.getOutputValue(name)
            self.inputValues[name] = value
            if name == self.add_address_input:
                self.add_address_value = value
            elif name == self.sliced_instruction_inputs:
                self.add_instruction_value = value
        print(f"IF_ID Input Values after read: {self.inputValues}")


class TestIFID(unittest.TestCase):
    def setUp(self):
        self.ifid = IF_ID_Register()

        self.testInput = TestElement()
        self.testOutput = TestElement()

        # Connect testInput
        self.testInput.connect(
            [],
            self.ifid.slice_names + ['add_address'],
            [],
            #['ifFlushControl', 'hazardDetection']
            []
        )

        # Connect ifid
        inputs_for_ifid = [(self.testInput, 'add_address')] + [(self.testInput, key) for key in self.ifid.slice_names]
        outputs_for_ifid = ['output_address'] + self.ifid.slice_names

        self.ifid.connect(
            inputs_for_ifid,
            outputs_for_ifid,
            #[(self.testInput, 'ifFlushControl'), (self.testInput, 'hazardDetection')],
            [],
            []
        )

        # Connect testOutput
        self.testOutput.connect(
            [(self.ifid, 'output_address')] + [(self.ifid, key) for key in self.ifid.slice_names],
            [],
            [],
            []
        )

    def printConnectionInfo(self, label):
        print(f"---- {label} ----")
        self.ifid.printConnectionInfo(self.testInput, "testInput")
        self.ifid.printConnectionInfo(self.ifid, "ifid")
        self.ifid.printConnectionInfo(self.testOutput, "testOutput")
        print(f"{'-' * (len(label) + 8)}")

    def test_correct_behaviour(self):  # both control signals = 0, enabled
        # Address example
        example_address = '0b11011100110000001111111100000000'  # example 32b address
        self.testInput.setOutputValue('add_address', example_address)
        # Sliced instruction example
        for key in self.ifid.slice_names:
            self.testInput.setOutputValue(key,
                                          '0b' + '1' * len(key))  # assuming the name of the slice represents its length
        # Both reading and writing are enable
        # self.testInput.setOutputControl('ifFlushControl', 0)
        # self.testInput.setOutputControl('hazardDetection', 0)
        # Call methods to propagate values
        self.ifid.readInput()
        #self.ifid.readControlSignals()
        self.ifid.writeOutput()
        self.testOutput.readInput()
        self.ifid.readControlSignals()
        # Check values received by ifid from testInput
        for key in self.ifid.slice_names:
            self.assertEqual(self.ifid.inputValues[key], '0b' + '1' * len(key))
        self.assertEqual(self.ifid.inputValues['add_address'], example_address)
        # Check values sent to testOutput by ifid
        for key in self.ifid.slice_names:
            self.assertEqual(self.testOutput.inputValues[key], '0b' + '1' * len(key))
        self.assertEqual(self.testOutput.inputValues['output_address'], example_address)

    # def test_flush(self):
    #     # Clear the instruction values to zero
    #     example_address = '0b11011100110000001111111100000000'  # example 32b address
    #     self.testInput.setOutputValue('add_address', example_address)
    #
    #     instruction_slices = {
    #         'jump_target': '0b11111100000000000010000000',
    #         'opcode': '0b000010',
    #         'rs': '0b11111',
    #         'rt': '0b10000',
    #         'rd': '0b00000',
    #         'imm': '0b0000000010000000',
    #         'func': '0b000000',
    #     }
    #
    #     # Set the instruction_slices into the testInput
    #     for key, value in instruction_slices.items():
    #         self.testInput.setOutputValue(key, value)
    #
    #     # # Both reading and writing are enabled
    #     # self.testInput.setOutputControl('ifFlushControl', 1)
    #     # self.testInput.setOutputControl('hazardDetection', 0)
    #
    #     # Call methods to propagate values
    #     self.ifid.readInput()
    #     #self.ifid.readControlSignals()
    #     self.ifid.writeOutput()
    #     self.testOutput.readInput()
    #
    #     for key, value in instruction_slices.items():
    #         self.assertEqual(self.ifid.inputValues[key], value)
    #     self.assertEqual(self.ifid.inputValues['add_address'], example_address)
    #
    #     # Check values sent to testOutput by ifid
    #     for key in self.ifid.slice_names:
    #         expected_zeros = '0b' + '0' * (len(instruction_slices[key]))
    #         self.assertEqual(self.testOutput.inputValues[key], expected_zeros)
    #     self.assertEqual(self.testOutput.inputValues['output_address'], example_address)

    # def test_hazardDetection(self):
    #     # Address example
    #     example_address = '0b11011100110000001111111100000000'  # example 32b address
    #     self.testInput.setOutputValue('add_address', example_address)
    #
    #     instruction_slices = {
    #         'jump_target': '0b11111100000000000010000000',
    #         'opcode': '0b000010',
    #         'rs': '0b11111',
    #         'rt': '0b10000',
    #         'rd': '0b00000',
    #         'imm': '0b0000000010000000',
    #         'func': '0b000000',
    #     }
    #
    #     # Set the instruction_slices into the testInput
    #     for key, value in instruction_slices.items():
    #         self.testInput.setOutputValue(key, value)
    #
    #     # Both reading and writing are enabled
    #     self.testInput.setOutputControl('ifFlushControl', 0)
    #     self.testInput.setOutputControl('hazardDetection', 1)
    #
    #     # Call methods to propagate values
    #     self.ifid.readInput()
    #     self.ifid.readControlSignals()
    #     self.ifid.writeOutput()
    #     self.testOutput.readInput()
    #
    #
    #     # Check values received by ifid from testInput
    #     for key, value in instruction_slices.items():
    #         self.assertEqual(self.ifid.inputValues[key], value)
    #     self.assertEqual(self.ifid.inputValues['add_address'], example_address)
    #
    #     # Check values sent to testOutput by ifid
    #     for key, value in instruction_slices.items():
    #         self.assertEqual(self.testOutput.inputValues[key], value)
    #     self.assertEqual(self.testOutput.inputValues['output_address'], example_address)

    # def test_hazard_and_flush(self):
    #     # Address example
    #     example_address = '0b11011100110000001111111100000000'  # example 32b address
    #     self.testInput.setOutputValue('add_address', example_address)
    #
    #     instruction_slices = {
    #         'jump_target': '0b11111100000000000010000000',
    #         'opcode': '0b000010',
    #         'rs': '0b11111',
    #         'rt': '0b10000',
    #         'rd': '0b00000',
    #         'imm': '0b0000000010000000',
    #         'func': '0b000000',
    #     }
    #
    #     # Set the instruction_slices into the testInput
    #     for key, value in instruction_slices.items():
    #         self.testInput.setOutputValue(key, value)
    #
    #     # Both reading and writing are enabled
    #     self.testInput.setOutputControl('ifFlushControl', 1)
    #     self.testInput.setOutputControl('hazardDetection', 1)
    #
    #     # Call methods to propagate values
    #     self.ifid.readInput()
    #     self.ifid.readControlSignals()
    #     self.ifid.writeOutput()
    #     self.testOutput.readInput()
    #
    #     # Check values received by ifid from testInput
    #     for key, value in instruction_slices.items():
    #         self.assertEqual(self.ifid.inputValues[key], value)
    #     self.assertEqual(self.ifid.inputValues['add_address'], example_address)
    #
    #     # Check values sent to testOutput by ifid
    #     for key, value in instruction_slices.items():
    #         self.assertEqual(self.testOutput.inputValues[key], value)
    #     self.assertEqual(self.testOutput.inputValues['output_address'], example_address)


if __name__ == '__main__':
    unittest.main()
