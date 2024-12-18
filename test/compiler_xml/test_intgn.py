import unittest
from tempfile import NamedTemporaryFile
import re
import os

import compiler_xml.JackAnalyzer as ja

class TestIntgration(unittest.TestCase):

  file_list = []

  def setUp(self):
    output_file = NamedTemporaryFile(
      delete=False,
      mode="w",
      newline="",
      suffix=".xml",
    )
    output_file_name = output_file.name

    self.file_list.append(output_file_name)
    return output_file_name

  @classmethod
  def tearDownClass(cls):
      for i in cls.file_list:
        os.remove(i)

  def test_integration(self):
    files_to_test = [
      (
          "./10/ExpressionLessSquare/Main.jack",
          "./10/ExpressionLessSquare/Main.xml"
      ),
      (
        "./10/ExpressionLessSquare/Square.jack",
        "./10/ExpressionLessSquare/Square.xml"
      ),
      (
        "./10/ExpressionLessSquare/SquareGame.jack",
        "./10/ExpressionLessSquare/SquareGame.xml"
      ),
      (
        "./10/ArrayTest/Main.jack",
        "./10/ArrayTest/Main.xml"
      ),
      (
        "./10/Square/Main.jack",
        "./10/Square/Main.xml"
      ),
      (
        "./10/Square/Square.jack",
        "./10/Square/Square.xml"
      ),
      (
        "./10/Square/SquareGame.jack",
        "./10/Square/SquareGame.xml"
      )
      ]
    for src_path, answer_path in files_to_test:
      with self.subTest(src_path=src_path, answer_path=answer_path):
        output_path = self.setUp()
        ja.main(src_path, "d", output_path)
        with open(answer_path, "r") as answer, open(output_path, "r") as output:
          contents = answer.read()
          cleaned_ans = re.sub(r"\s+", "", contents)
          contents = output.read()
          cleaned_output = re.sub(r"\s+", "", contents)
          self.assertEqual(cleaned_output, cleaned_ans)

