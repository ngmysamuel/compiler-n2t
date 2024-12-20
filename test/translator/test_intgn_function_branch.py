import os
import unittest
from tempfile import NamedTemporaryFile
import re
import translator.VMTranslator as vmt


class TestIntegrationFunctionAndBranching(unittest.TestCase):
    """Runs the translator on a VM file and compares.

    Tests Function Calling, Branching, and Directory translation.

    Creates 2 files:
        output: file containing the output ASM code
    """

    def getOutputFile(self) -> None:
        self.output = NamedTemporaryFile(
            delete=False,
            mode="w",
            newline="",
            prefix="output_",
            suffix=".asm",
        )
        self.output_name = self.output.name
        self.output.close()

    def tearDown(self) -> None:
        os.remove(self.output_name)

    def test_integration(self) -> None:
        files_to_test = [('./08/FibonacciElement', './08/FibonacciElement/FibonacciElementAns.asm')]
        for src_path, ans_path in files_to_test:
            self.getOutputFile()
            vmt.main(src_path, self.output_name)
            with open(self.output_name, "r") as output_file, open(ans_path, "r") as ans_file:
                contents = output_file.read()
                cleaned_output = re.sub(r"\s+", "", contents)
                contents = ans_file.read()
                cleaned_ans = re.sub(r"\s+", "", contents)
                self.assertEqual(cleaned_output, cleaned_ans)
