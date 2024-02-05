from genericpath import exists
import pytest
import logging
import os  # nopep8
import sys  # nopep8
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))  # nopep8
from common import fromUnsignedWordToSignedWord, Break, Overflow
from src.mipsSimulator import MIPSSimulator


log = logging.getLogger(__name__)


class SubTest():
    def __init__(self, name, destination, expectedValue, minCycles, maxCycles, code):
        self.name = name
        self.destination = destination
        self.expectedValue = expectedValue
        self.minCycles = minCycles
        self.maxCycles = maxCycles
        self.code = code


class MipsWrapper():
    def __init__(self, cwd, memfolder, file, trapTest):
        self.cd = cwd
        self.tmpFileFolder = os.getcwd()+'/'
        self.memfolder = memfolder
        self.filename = file
        self.trapTest = trapTest
        self.tests = {}
        self.currentTest = None
        self.simulator = None
        self.score = 0
        self.maxScore = 0
        # score rewarded for correct trap handling
        self.trapPoint = 1
        # score rewarded for correct mem/reg value
        self.valPoint = 1
        self.setupTests()

    def setupTests(self):
        log.debug(f"Wrapper setting up {self.filename}")
        with open(self.memfolder + self.filename) as memfile:
            for line in memfile:
                if line.startswith(">"):
                    test = line[:-1]  # remove newline
                    _, _, dest, expVal, trap = line.split()
                    if trap == "trap" and self.trapTest:
                        self.setupSubTest(test, dest, expVal, memfile)
                    elif not self.trapTest:
                        self.setupSubTest(test, dest, expVal, memfile)
        self.creatTmpFiles()
        # Each subtest has a max score of 2(1 for trap, 1 for val)
        if self.trapTest:
            self.maxScore = len(self.tests.keys()) * (self.trapPoint)
        else:
            self.maxScore = len(self.tests.keys()) * (self.valPoint)

    def setupSubTest(self, test, dest, expVal, memfile):
        log.debug(f"Parsing code for {test}")
        code = []
        minCycles = 0
        for line in memfile:
            if not line.startswith("0"):
                break
            # find number of lines until first break
            _, _, asm = line.split('\t')
            if not asm.startswith("break"):
                minCycles += 1
            code.append(line)
        log.debug(f"Initializing subtest for {test}")
        self.tests[test] = SubTest(
            test, dest, expVal, minCycles, len(code)*10, code)

    def creatTmpFiles(self):
        for _, subtest in self.tests.items():
            log.debug(f"Writing tmp files for {subtest.name}")
            with open(self.tmpFileFolder+subtest.name, "w") as f:
                for line in subtest.code:
                    f.writelines(line)

    def rmTmpFiles(self):
        log.debug(f"Removing all tmp files for {self.filename}")
        for tmpFile in self.tests.keys():
            try:
                os.remove(self.tmpFileFolder+tmpFile)
            except FileNotFoundError:
                log.error(f"Failed removing {tmpFile}, not found!")

    def checkSimulator(self):
        assert hasattr(self.simulator, "registerFile")
        assert hasattr(self.simulator.registerFile, "register")
        assert type(self.simulator.registerFile.register) == dict
        assert hasattr(self.simulator.registerFile, "registerNames")
        assert type(self.simulator.registerFile.registerNames) == list
        assert hasattr(self.simulator, "dataMemory")
        assert hasattr(self.simulator.dataMemory, "memory")
        assert type(self.simulator.dataMemory.memory) == dict

    def prepare(self, test):
        log.debug(f"Wrapper setting up subtest {test.name}")
        self.simulator = MIPSSimulator(test.name)
        self.CT = test
        self.checkSimulator()

    def _runSimulator(self):
        log.debug(f"Running simulator with {self.CT.name}")
        while(self.simulator.nCycles <= self.CT.maxCycles):
            self.simulator.tick()
        log.critical(
            f"Simulation of '{self.CT.name}' exit due to exceeding cycle limit: {self.CT.maxCycles}")

    def addTrapPoint(self):
        log.debug(f"Adding point for correct trap in {self.CT}")
        self.score += self.trapPoint

    def addValPoint(self):
        log.debug(f"Adding point for correct value in {self.CT}")
        self.score += self.valPoint

    def writeResults(self):
        log.info(
            f"Subtest completed with: [{self.score}] out of [{self.maxScore}] points")
        with open("result", "a+") as res:
            res.write(f"{self.score}/{self.maxScore}\n")

    def getRegisterName(self):
        return self.simulator.registerFile.registerNames[int(self.CT.destination)]

    def getRegisterVal(self):
        return fromUnsignedWordToSignedWord(
            self.simulator.registerFile.register[int(self.CT.destination)])

    def getMemVal(self, _):
        return hex(self.simulator.dataMemory.memory[int(self.CT.destination, base=16)])

    def validateRun(self):
        log.debug(f"Validating values in {self.CT.name}")
        if "Test_sw" in self.CT.name:
            try:
                self.validateMemory()
                self.addValPoint()
            except AssertionError:
                self.memErrInfo()
                raise ValueError(
                    f"Memory {self.CT.destination} value: {self.getMemVal()} expected: {self.CT.expectedValue}")
        else:
            try:
                self.validateRegister()
                self.addValPoint()
            except AssertionError:
                self.regErrInfo()
                raise ValueError(
                    f"Register {self.getRegisterName()} value: {self.getRegisterVal()} expected: {self.CT.expectedValue}")

    def memErrInfo(self):
        log.warning(
            f"Memory {self.CT.destination} value: {self.getMemVal()} expected: {self.CT.expectedValue}")

    def validateMemory(self):
        mem = self.simulator.dataMemory.memory
        sw = hex(mem[int(self.CT.destination, base=16)])
        assert sw == self.CT.expectedValue
        k = bytes.fromhex(sw[2:]).decode("ASCII")
        log.info(f"Memory value OK...{k}")

    def regErrInfo(self):
        log.warning(
            f"Register {self.getRegisterName()} value: {self.getRegisterVal()} expected: {self.CT.expectedValue}")
        self.simulator.printRegisterFile()

    def validateRegister(self):
        reg = int(self.CT.destination)
        regValue = fromUnsignedWordToSignedWord(
            self.simulator.registerFile.register[reg])
        assert regValue == int(self.CT.expectedValue)
        log.info("Register value OK...")

    def tearDown(self):
        log.debug(f"Tearing down {self} for {self.filename}")
        self.writeResults()
        self.rmTmpFiles()


class TestMips():
    cwd = os.path.dirname(os.path.abspath(__file__))
    testFolder = os.path.join(cwd, "memfiles/")
    testFiles = ["add.mem", "addu.mem", "and.mem", "beq.mem", "bne.mem", "break.mem",
                 "jump.mem", "lui.mem", "lw.mem", "nop.mem", "nor.mem", "or.mem",
                 "slt.mem", "sub.mem", "subu.mem", "sw.mem"]
    mipsWrapper = None
    currentSubTest = None
    trap = True
    exception = None
    testName = None

    def _setupTest(self, test, trap):
        log.debug(f"Setting up test: {test}")
        self.mipsWrapper = MipsWrapper(
            self.cwd, self.testFolder, test, trap)
        if trap:
            self.exception = Overflow
        else:
            self.exception = Break

    def _prepareSubTest(self, subtest):
        log.debug(f"Preparing {subtest.name}")
        self.currentSubTest = subtest
        self.mipsWrapper.prepare(subtest)

    def _runTrapTest(self):
        log.debug(f"Running: {self.currentSubTest.name} ")
        with pytest.raises(self.exception):
            self.mipsWrapper._runSimulator()
        log.info("Trapps OK...")
        self.mipsWrapper.addTrapPoint()

    def _runValTest(self):
        log.debug(f"Running: {self.currentSubTest.name} ")
        with pytest.raises(Exception):
            self.mipsWrapper._runSimulator()
        log.debug(f"Simulator ticks: {self.mipsWrapper.simulator.nCycles}")
        if self.mipsWrapper.simulator.nCycles <= self.currentSubTest.minCycles:
            pytest.fail(f"{self.currentSubTest.name} ran as singleCycle?")
        self._validateResult()

    def _validateResult(self):
        log.debug(f"Validating {self.currentSubTest.name} ")
        self.mipsWrapper.validateRun()

    @pytest.fixture()
    def _finish(self):
        yield
        self.mipsWrapper.tearDown()
        log.info(f"Finished test")

    @ pytest.mark.parametrize('test', testFiles)
    def test_trap(self, test, _finish):
        self._setupTest(test, self.trap)
        for _, subtest in self.mipsWrapper.tests.items():
            log.debug(f"Starting test: {subtest.name}")
            try:
                self._prepareSubTest(subtest)
                self._runTrapTest()
            except AssertionError as ae:
                log.critical(
                    f"Assertion error while running test: {test} {ae}")
                pytest.exit(ae)
            except Break as b:
                pytest.fail(f"Excepted {self.exception} caught {b}")
            except Overflow as ovf:
                pytest.fail(f"Excepted {self.exception} caught {ovf}")
            except Exception as e:
                log.warning(f"Unexpected exception: {e}")

    @ pytest.mark.parametrize('test', testFiles)
    def test_val(self, test, _finish):
        self._setupTest(test, not self.trap)
        for _, subtest in self.mipsWrapper.tests.items():
            log.debug(f"Starting test: {subtest.name}")
            try:
                self._prepareSubTest(subtest)
                self._runValTest()
            except AssertionError as ae:
                log.critical(
                    f"Assertion error while running test: {test} {ae}")
                pytest.exit(ae)
            except ValueError as ve:
                pytest.fail(f"{ve}")
            except Exception as e:
                log.warning(f"Unexpected exception: {e}")


if __name__ == "__main__":
    print("Run: pytest [-flags].. Ex: pytest -rPf")
