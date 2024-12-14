import unittest
from tempfile import NamedTemporaryFile
import os
from compiler import JackAnalyzer
import filecmp
import re

class TestIntegration(unittest.TestCase):

  file_list = []

  def setup(self):
    output_file = NamedTemporaryFile(
      delete = False,
      mode="w",
      newline="",
      suffix=".vm",
    )
    output_file_name = output_file.name
    temp_ans_file = NamedTemporaryFile(
      delete = False,
      mode="w",
      newline="",
      suffix=".vm",
    )
    temp_ans_file_name = temp_ans_file.name
    self.file_list.append((output_file_name, temp_ans_file_name))
    return output_file_name, temp_ans_file_name
  
  @classmethod
  def tear_down_class(cls):
    for i, j in cls.file_list:
      os.remove(i)
      os.remove(j)

  def test_integration(self):
    files_to_test = [
      ("./11/Seven/Main.jack", "d", "./11/Seven/Main.vm"),
      ("./11/ConvertToBin/Main.jack", "d", "./11/ConvertToBin/Main.vm"),
      ("./11/Square/Main.jack", "d", "./11/Square/Main.vm"),
      ("./11/Square/SquareGame.jack", "d", "./11/Square/SquareGame.vm"),
      ("./11/Square/Square.jack", "d", "./11/Square/Square.vm"),
      ("./11/Average/Main.jack", "d", "./11/Average/Main.vm"),
      ("./11/Pong/Main.jack", "d", "./11/Pong/Main.vm"),
      ("./11/Pong/PongGame.jack", "d", "./11/Pong/PongGame.vm"),
      ("./11/Pong/Bat.jack", "d", "./11/Pong/Bat.vm"),
      ("./11/Pong/Ball.jack", "d", "./11/Pong/Ball.vm"),
      ("./11/ComplexArrays/Main.jack", "d", "./11/ComplexArrays/Main.vm"),
    ]
    for input_path, log_level, ans_path in files_to_test:
      with self.subTest(input_path=input_path, log_level=log_level, ans_path=ans_path):
        output, temp_ans = self.setup()
        JackAnalyzer.main(input_path, log_level, output)
        with open(output, "r") as output_file, open(ans_path, "r") as ans_file:
          contents = output_file.read()
          cleaned_output = re.sub(r"\s+", "", contents)
          contents = ans_file.read()
          cleaned_ans = re.sub(r"\s+", "", contents)
        with open(output, "w") as output_file, open(temp_ans, "w") as temp_ans_file:
          output_file.write(cleaned_output)
          temp_ans_file.write(cleaned_ans)
        self.assertTrue(filecmp.cmp(output, temp_ans), "The files are not the same")
