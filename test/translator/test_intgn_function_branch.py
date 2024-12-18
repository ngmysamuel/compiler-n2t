import os
import unittest
from tempfile import NamedTemporaryFile
import re
import filecmp
import translator.VMTranslator as vmt


class TestIntegrationFunctionAndBranching(unittest.TestCase):
    """Runs the translator on a VM file and compares.

    Tests Function Calling, Branching, and Directory translation.

    Creates 2 files:
        output: output ASM code
        temp_ans_file: contains the correct assembly code previously tested on the CPU
        emulator on Nand2Tetris site. Temp because I remove all white space from the
        file and I do not wish to have that happen to the actual file.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.output = NamedTemporaryFile(
            delete=False,
            mode="w",
            newline="",
            prefix="output_",
            suffix=".asm",
        )
        cls.output_name = cls.output.name
        cls.output.close()

        cls.temp_ans_file = NamedTemporaryFile(
            delete=False,
            mode="w",
            newline="",
            prefix="answer_",
            suffix=".asm",
        )
        cls.temp_ans_file_name = cls.temp_ans_file.name
        cls.temp_ans_file.close()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.output_name)
        os.remove(cls.temp_ans_file_name)

    def test_integration(self) -> None:
        files_to_test = [('./08/FibonacciElement', './08/FibonacciElement/FibonacciElementAns.asm')]
        for src_path, ans_path in files_to_test:
            vmt.main(src_path, self.output_name)
            with open(self.output_name, "r") as output_file, open(ans_path, "r") as ans_file:
                contents = output_file.read()
                cleaned_output = re.sub(r"\s+", "", contents)
                contents = ans_file.read()
                cleaned_ans = re.sub(r"\s+", "", contents)
            with open(self.output_name, "w") as output_file, open(self.temp_ans_file_name, "w") as temp_ans_file:
                output_file.write(cleaned_output)
                temp_ans_file.write(cleaned_ans)
            self.assertTrue(filecmp.cmp(self.output_name, self.temp_ans_file_name), "The files are not the same")
