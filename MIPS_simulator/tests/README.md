# MIPS TESTS
The mips tests are conducted as short specific sets of instructions, pin pointing as narrow as possible test cases.

DO NOT MODIFY ANYTHING IN THE TESTFOLDER YOURSELF, REPORT PROBLEMS TO TAs AND WAIT FOR FIX IF YOU FIND A BUG

## Pitfalls💢
These tests are not unit tests, since we do not know the layout of your implementation. Instead, they are conducted as integration tests. The tests will send instructions through your mips simulation and verify against expected results. Note that a single bug can threfore cause all tests to fail. 

Most of the tests requires **stalling** and **forwarding** mechanisms to be properly implemented.

## Test layout💡
Tests are based on .memfiles containing mips32 instructions, with corresponsing assembly instructions as comments.
Each memfile is testing one part of the instruction set, and contains subtests, testing different cases.
In order to populate the registers, IMMEDIATE instructions are used, and this should be a good starting point while implementing
your mips simulation.

Each subtest is marked with a header, recognized by the sign '>'
The header is structured like:

**> 'TestName' 'Destination' 'Expected Value' 'trap or no trap expected'**

## Single cycle vs Pipeline
The tests expect pipelined implementations and will fail if a single cycle implementation is identified.

## Score
Maximum score is 35 points.

# Test dependencies📑
python >=3.9.5\
pytest >=6.2.4
requests >= 2.26.0

# Running tests
The tests are setup so that you should be able to run 
- *pytest [-flags]* 
    - ex: pytest -rPf

anywhere within repository root directory to run the tests. Pytest parses recursivly from cwd into subfolders, looking for tests. If you try to run pytest in f.ex. the src folder, this will not work.
You can also use the shellscript, found in the test folder, this does require current working directory to be .../tests/

## Single test🩺
As with the other memfiles, you will have to parse out the memfiles found in the *../tests/memfiles* folder if you wish to run one and one test by yourself on your simulator. Alternatively you can create your own file and copy just the code from a test into the file, and give that as argument to your simulator.

## Github pipeline  🔩 ⚙️
In the .github/workflows/ folder you can find the github actions script. The pipeline is run only on push or pull-requests to your main branch.

You can add branches to the list of guarded branches, but the main branch **must** remain guarded.

This will run the tests and upload logs and result as artifacts on your github repository. It will not produce much before you have implemented quite a bit in your simulator.

On a failed test, you will by default recieve an email notifying of the failed test. You can turn off this feature under \
*../settings/notifications*
