import unittest
from tempfile import NamedTemporaryFile
import re
import os
import filecmp
import compiler_xml.JackAnalyzer as ja

class TestIntgration(unittest.TestCase):

  file_list = []

  def setUpFiles(self, answer_path):
    answer_file = NamedTemporaryFile(
      delete=False,
      mode="w",
      newline="",
      suffix=".xml",
    )
    answer_file_name = answer_file.name
    with open(answer_path, "r") as f:
      contents = f.read()
      no_white_space = re.sub(r"\s+", "", contents)
      answer_file.write(no_white_space)
    answer_file.close()

    output_name = answer_file_name.replace(".xml", "2.xml")

    files = (answer_file_name, output_name)
    self.file_list.append(files)
    return files

  @classmethod
  def tearDownClass(cls):
      for i, j in cls.file_list:
        os.remove(i)
        os.remove(j)

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
        output_path, answer_path = self.setUpFiles(answer_path)
        ja.main(src_path, "d", answer_path)
        with open(answer_path, "r") as answer, open(output_path, "r") as output:
          contents = answer.read()
          cleaned_ans = re.sub(r"\s+", "", contents)
          contents = output.read()
          cleaned_output = re.sub(r"\s+", "", contents)
        with open(answer_path, "w") as answer, open(output_path, "w") as output:
          answer.write(cleaned_ans)
          output.write(cleaned_output)
        self.assertTrue(filecmp.cmp(answer_path, output_path), "The files are not the same")
