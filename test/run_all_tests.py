import unittest
import xmlrunner

test_loader = unittest.TestLoader()
test_suite =unittest.TestSuite()

test_suite.addTests(test_loader.discover("./test/assembler"))
test_suite.addTests(test_loader.discover("./test/translator"))
test_suite.addTests(test_loader.discover("./test/compiler"))
# test_suite.addTests(test_loader.discover("./test/compiler_xml"))

with open('./test-results/results.xml', 'wb') as output:
    test_runner=xmlrunner.XMLTestRunner(output=output)
    test_runner.run(test_suite)