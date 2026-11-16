import subprocess
import sys
import unittest

BINARY=sys.argv[1]

def run(commands):
    result=subprocess.run([BINARY],input=commands,text=True,capture_output=True,timeout=15)
    if result.returncode: raise AssertionError(result.stderr)
    return result.stdout

class ConsoleTests(unittest.TestCase):
    def test_tree_operations(self):
        out=run('tree int\ninsert 4\ninsert 2\ninsert 6\nthreads\nreverse\nremove 4\ncontains 4\nshow\nclear\npop\nquit\n')
        for value in ('2 4 6','6 4 2','false','2 6','Ошибка:'): self.assertIn(value,out)

    def test_heap_doubles_and_switching(self):
        out=run('minheap double\npush 1.25\npush -2.5\npop\ntop\npop\npop\nback\ntree string\ninsert строка с пробелами\nshow\nquit\n')
        for value in ('-2.5','1.25','Ошибка:','строка с пробелами'): self.assertIn(value,out)

    def test_priority_and_duplicates(self):
        out=run('queue string\npush 1 apple\npush 3 pear\npush 3 plum\npop\npop\npop\nquit\n')
        lines=out.splitlines()
        self.assertLess(lines.index('> plum'),lines.index('> pear'))
        self.assertLess(lines.index('> pear'),lines.index('> apple'))

    def test_reproducible_generation(self):
        script='tree int\nrandom 20 2026\nshow\nquit\n'
        self.assertEqual(run(script),run(script))

if __name__=='__main__': unittest.main(argv=[sys.argv[0]],verbosity=2)
