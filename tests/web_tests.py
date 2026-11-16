import io
import json
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server


BACKEND = server.find_backend(sys.argv[1] if len(sys.argv) > 1 else None)


def request(action="structure", **parameters):
    return server.handle_request(BACKEND, dict(action=action, **parameters))


def structure(kind="array", value_type="int", **parameters):
    return request(structure=kind, valueType=value_type, **parameters)["lab"]


class MemoryConnection:
    def __init__(self, data):
        self.input = io.BytesIO(data)
        self.output = bytearray()

    def makefile(self, *args):
        return self.input

    def sendall(self, data):
        self.output.extend(data)


def http_request(method, path, body=b""):
    message = f"{method} {path} HTTP/1.0\r\nHost: 127.0.0.1\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body
    connection = MemoryConnection(message)
    server.WebsiteHandler(connection, ("127.0.0.1", 12345), None, backend=BACKEND)
    headers, content = bytes(connection.output).split(b"\r\n\r\n", 1)
    return int(headers.split()[1]), content


class WebTests(unittest.TestCase):
    def test_all_ready_checks_and_replay(self):
        total = 0
        for kind in ("array", "tree", "hash", "queue", "minheap", "maxheap"):
            types = ("double",) if kind.endswith("heap") else ("int", "double", "string")
            for value_type in types:
                with self.subTest(structure=kind, value_type=value_type):
                    result = structure(kind, value_type, mode="tests")
                    self.assertEqual(result["failed"], 0)
                    self.assertEqual(result["passed"], result["total"])
                    total += result["total"]
                    for count in (0, 1, result["total"] // 2, result["total"]):
                        prefix = structure(kind, value_type, mode="tests", count=count)
                        self.assertEqual(prefix["steps"], result["steps"][:count])
        self.assertEqual(total, 244)


    def test_strings_and_error_recovery(self):
        value = 'Привет <html> "\\\n\r\t\x00🙂'
        result = structure(value_type="string", mode="manual", operations=[
            dict(op="resize", size="2"), dict(op="set", index="0", value=value),
            dict(op="copy", value="copy"), dict(op="get", index="-1"), dict(op="get", index="0")])
        self.assertEqual(result["snapshot"]["values"], [value, ""])
        self.assertEqual(result["steps"][2]["actual"], value)
        self.assertTrue(result["steps"][3]["error"])
        self.assertEqual(result["steps"][-1]["actual"], value)


    def test_tree_traversal_and_error_recovery(self):
        commands = [dict(op="insert", value=str(n)) for n in (4,2,6,1,3,5,7)]
        result = structure("tree", operations=commands + [dict(op="threads"), dict(op="reverse"),
            dict(op="remove",value="4"),dict(op="contains",value="4"),dict(op="inorder")])
        actual = [step["actual"] for step in result["steps"][-5:]]
        self.assertEqual(actual,["1 2 3 4 5 6 7","7 6 5 4 3 2 1","true","false","1 2 3 5 6 7"])
        self.assertEqual(result["snapshot"]["values"],["1","2","3","5","6","7"])

    def test_fractional_heap_and_invalid_input(self):
        for kind in ("minheap","maxheap"):
            result = structure(kind,"double",operations=[dict(op="push",value="1.25"),
                dict(op="push",value="-3.75"),dict(op="pop"),dict(op="top")])
            self.assertEqual(result["steps"][-2]["actual"],"-3.75" if kind=="minheap" else "1.25")
        for value in ("NaN","inf","1e999","2.5bad"):
            result=structure("minheap","double",operations=[dict(op="push",value=value)])
            self.assertTrue(result["steps"][0]["error"])
        with self.assertRaises(ValueError): structure("minheap","int",mode="tests")
        with self.assertRaises(ValueError): structure(operations=[dict(op="get")]*101)
        with self.assertRaises(ValueError): request("solve")

    def test_http_and_assets(self):
        for path in ("/","/app.js","/style.css","/structures.js"):
            status,body=http_request("GET",path)
            self.assertEqual(status,200)
            self.assertTrue(body)
        payload=dict(action="structure",structure="tree",valueType="int",mode="tests")
        status,body=http_request("POST","/api",json.dumps(payload).encode())
        self.assertEqual(status,200)
        self.assertEqual(json.loads(body)["lab"]["failed"],0)
        self.assertEqual(http_request("POST","/api",b"not json")[0],400)
        self.assertEqual(http_request("POST","/unknown",b"{}")[0],404)
        self.assertEqual(http_request("GET","/../BinarySearchTree.h")[0],404)


if __name__=="__main__":
    unittest.main(argv=[sys.argv[0]],verbosity=2)
