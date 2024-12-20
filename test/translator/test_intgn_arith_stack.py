import os
import unittest
from tempfile import NamedTemporaryFile
import re
# import filecmp
import translator.VMTranslator as vmt

class TestIntegrationArithStack(unittest.TestCase):
    """Runs the translator on a VM file and compares.

    Tests arithmetic, logical, and stack manipulation.

    Creates 2 files:
        output_file: file containing the output ASM code
    """

    def getOutputFile(self) -> None:
        self.output_file = NamedTemporaryFile(
            delete=False,
            mode="w",
            newline="",
            suffix=".asm",
        )
        self.output_file_name = self.output_file.name
        self.output_file.close()

    def tearDown(self) -> None:
        os.remove(self.output_file_name)

    def test_integration(self) -> None:
        files_to_test = [('./07/BasicTest/BasicTest.vm', './07/BasicTest/BasicTestAns.asm')]
        for src_path, ans_path in files_to_test:
            self.getOutputFile()
            vmt.main(src_path, self.output_file_name)
            with open(self.output_file_name, "r") as output_file, open(ans_path, "r") as ans_file:
                contents = output_file.read()
                cleaned_output = re.sub(r"\s+", "", contents)
                contents = ans_file.read()
                cleaned_ans = re.sub(r"\s+", "", contents)
                self.assertEqual(cleaned_output, cleaned_ans)

