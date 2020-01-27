from codacy_pylint import *
import unittest
import tempfile

def withConfigAndSources(config, sources):
    with tempfile.TemporaryDirectory() as directory:
        codacyrcPath = directory + "/.codacyrc"
        with open(codacyrcPath, "w") as codacyrc:
            print(config, file=codacyrc)
        for (name, source) in sources:
            with open(directory + '/' + name, 'w') as f:
                print(source, file=f)
        return runTool(codacyrcPath, directory)

def python3_file():
    source ='''
##Patterns: E0102

class Test():
    def dup(self):
        return 1

    ##Err: E0102
    def dup(self):
        return 2

##Err: E0102
class Test():
    def __init__(self):
        return

def dup_function():
    return 1

##Err: E0102
def dup_function():
    return 2
'''
    sources = [('E0102.py', source)]
    config = '{"tools":[{"name":"PyLint (Python 3)","patterns":[{"patternId":"E0102"}]}],"files":["E0102.py"]}'
    return config, sources

class ResultTest(unittest.TestCase):
    def test_toJson(self):
        result = Result("file.py", "message", "id", 80)
        res = toJson(result)
        expected = '{"filename": "file.py", "line": 80, "message": "message", "patternId": "id"}'
        self.assertEqual(res, expected)

class PyLintTest(unittest.TestCase):
    maxDiff = None
    def test_chunks(self):
        l = ["file1", "file2"]
        expected = [["file1", "file2"]]
        out = chunks(l, 10)
        self.assertEqual(out, expected)

        expected2 = [["file1"], ["file2"]]
        out2 = chunks(l, 1)
        self.assertEqual(expected2, out2)

    def test_readConfiguration(self):
        with tempfile.TemporaryDirectory() as directory:
            codacyrcPath = os.path.join(directory, ".codacyrc")
            with open(codacyrcPath, "w") as codacyrc:
                print('{"tools":[{"name":"PyLint (Python 3)","patterns":[{"patternId":"C0111"}]}],"files":["C0111.py"]}', file=codacyrc)
            
            expectedConfiguration = Configuration(['--disable=all', '--enable=C0111'],['C0111.py'], None)
            
            configuration = readConfiguration(codacyrcPath, "docs/test")
            self.assertEqual(expectedConfiguration, configuration)

    def test_parse_message(self):
        message_input = '''[C0103(invalid-name), ] Module name "W0124" doesn't conform to snake_case naming style'''
        (rule, message) = parseMessage(message_input)
        self.assertEqual(rule, 'C0103')
        self.assertEqual(message, '''Module name "W0124" doesn't conform to snake_case naming style''')

    def test_E0711(self):
        config = '{"tools":[{"name":"PyLint (Python 3)","patterns":[{"patternId":"E0711"}]}],"files":["E0711.py"]}'
        sources = [('E0711.py',
'''##Patterns: E0711
##Err: E0711
raise NotImplemented
raise NotImplementedError''')]
        expected_result = [
            Result(
                'E0711.py',
                'NotImplemented raised - should raise NotImplementedError',
                'E0711',
                3)]
        self.assertEqual(withConfigAndSources(config, sources), expected_result)

    def test_E1125(self):
        config = '{"tools":[{"name":"PyLint (Python 3)","patterns":[{"patternId":"E1125"}]}],"files":["E1125.py"]}'
        sources = [('E1125.py',
'''##Patterns: E1125

def function(*, foo):
    print(foo)

function(foo=1)

foo = 1
##Err: E1125
function(foo)
##Err: E1125
function(1)
''')]
        expected_result = [
            Result(
                'E1125.py',
                "Missing mandatory keyword argument 'foo' in function call",
                'E1125',
                10),
            Result(
                'E1125.py',
                "Missing mandatory keyword argument 'foo' in function call",
                'E1125',
                12)
            ]
        self.assertEqual(withConfigAndSources(config, sources), expected_result)

    def test_python3_file(self):
        (config, sources) = python3_file()
        expected_result = [Result('E0102.py','method already defined line 5','E0102',9),
                          Result('E0102.py','class already defined line 4','E0102',13),
                          Result('E0102.py','function already defined line 17','E0102',21)]
        self.assertEqual(withConfigAndSources(config, sources), expected_result)

    def test_no_conf(self):
        (_, sources) = python3_file()
        result = withConfigAndSources(None, sources)
        self.assertEqual(len(result), 16)

    def test_timeout(self):
        self.assertEqual(getTimeout("60"), 60)
        self.assertEqual(getTimeout("blabla"), DEFAULT_TIMEOUT)

if __name__ == '__main__':
    unittest.main()
