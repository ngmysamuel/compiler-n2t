import unittest
from tempfile import NamedTemporaryFile
import re
import os
import filecmp
import compiler.JackAnalyzer as ja

class TestIntgration(unittest.TestCase):

  file_list = []

  def setUpFiles(self, src_file_path, dest_file_ans_path):
    src_file = NamedTemporaryFile(
      delete=False,
      mode="w",
      newline="",
      suffix=".xml",
    )
    src_file_name = src_file.name
    with open(src_file_path, "r") as f:
      src_file.write(f.read())
    src_file.close()

    dest_file_ans = NamedTemporaryFile(
      delete=False,
      mode="w",
      newline="",
      suffix=".xml",
    )
    dest_file_ans_name = dest_file_ans.name
    with open(dest_file_ans_path, "r") as f:
      contents = f.read()
      no_white_space = re.sub(r"\s+", "", contents)
      dest_file_ans.write(no_white_space)
    dest_file_ans.close()

    dest_file_name = dest_file_ans_name.replace(".xml", "2.xml")

    files = (src_file_name, dest_file_ans_name, dest_file_name)
    self.file_list.append(files)
    return files

  @classmethod
  def tearDownClass(cls):
      for i, j, k in cls.file_list:
        os.remove(i)
        os.remove(j)
        os.remove(k)

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
    for src_file_path, dest_file_ans_path in files_to_test:
      with self.subTest(src_file_path=src_file_path, dest_file_ans_path=dest_file_ans_path):
        src_file_name, dest_file_ans_name, dest_file_name = self.setUpFiles(src_file_path, dest_file_ans_path)
        ja.main(src_file_name, "d", dest_file_name)
        with open(dest_file_name, "w+") as dest_file, open(dest_file_ans_name, "w+") as dest_file_ans:
          contents = dest_file.read()
          no_white_space = re.sub(r"\s+", "", contents)
          dest_file.write(no_white_space)
          contents = dest_file_ans.read()
          no_white_space = re.sub(r"\s+", "", contents)
          dest_file_ans.write(no_white_space)
        self.assertTrue(filecmp.cmp(dest_file_name, dest_file_ans_name), "The files are not the same")


