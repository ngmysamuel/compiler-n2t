import unittest
from unittest.mock import patch

from assembler import code


class TestCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.testCodeClass = code.Code()

    @patch("assembler.parser")
    def test_c_instr(self, mock_parser) -> None:
        para_ls = [
            ("C", "D", "A", "", "1110110000010000"),
            ("C", "M", "D", "", "1110001100001000"),
            ("C", "", "0", "JMP", "1110101010000111"),
            ("C", "AM", "M-1", "", "1111110010101000"),
        ]
        for para in para_ls:
            with self.subTest(para=para):
                mock_parser.instr_type = para[0]
                mock_parser.dest = para[1]
                mock_parser.comp = para[2]
                mock_parser.jmp = para[3]
                self.assertEqual(self.testCodeClass.map(mock_parser), para[4])

    @patch("assembler.parser")
    def test_a_instr(self, mock_parser) -> None:
        para_ls = [("A", "256", "0000000100000000"), ("A", "15", "0000000000001111")]
        for para in para_ls:
            with self.subTest(para=para):
                mock_parser.instr_type = para[0]
                mock_parser.sym = para[1]
                self.assertEqual(self.testCodeClass.map(mock_parser), para[2])


if __name__ == "__main__":
    unittest.main()
