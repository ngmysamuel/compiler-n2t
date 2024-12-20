import os
import unittest
from tempfile import NamedTemporaryFile
import re
from assembler import driver


class TestIntegrationBasic(unittest.TestCase):

    file_list = []

    def getOutputFile(self) -> str:
        output_file = NamedTemporaryFile(
            delete=False,
            mode="w",
            newline="",
            suffix=".asm",
        )
        output_file_name = output_file.name
        output_file.close()

        self.file_list.append(output_file_name)
        return output_file_name

    @classmethod
    def tearDownClass(cls) -> None:
        for i in cls.file_list:
            os.remove(i)

    def test_integration(self) -> None:
        files_to_test = [
            ('./06/Rect.asm', './06/Rect.hack'),
            ('./06/Add.asm', './06/Add.hack'),
            ('./06/Max.asm', './06/Max.hack'),
            ('./06/Pong.asm', './06/Pong.hack'),
        ]
        for src_path, ans_path in files_to_test:
            with self.subTest(src_path=src_path, ans_path=ans_path):
                output_path = self.getOutputFile()
                driver.main(src_path, output_path)
                with open(output_path) as output_file, open(ans_path) as ans_file:
                    contents = output_file.read()
                    cleaned_output = re.sub(r"\s+", "", contents)
                    contents = ans_file.read()
                    cleaned_ans = re.sub(r"\s+", "", contents)
                    self.assertEqual(cleaned_output, cleaned_ans)