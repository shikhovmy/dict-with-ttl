import unittest
from time import sleep
from storage import Storage


class MyTestCase(unittest.TestCase):
    def test_dict_functions(self):
        s = Storage()
        s[1] = 2
        self.assertIn(1, s)
        self.assertEqual(2, s[1])
        self.assertEqual(1, len(s))
        self.assertIn(2, [v for _, v in s])
        del s[1]
        self.assertNotIn(1, s)

    def test_callback(self):
        called = {"deleted": None}
        s = Storage(ttl=1, cleanup_interval=1, purge_callback=lambda deleted: called.__setitem__("deleted", deleted))
        s[1] = 2
        sleep(2)
        self.assertIsNone(s[1])
        self.assertIn(1, called["deleted"])

    def test_callback_not_called_if_empty(self):
        called = {"deleted": False}
        s = Storage(ttl=10, cleanup_interval=1, purge_callback=lambda deleted: called.__setitem__("deleted", True))
        s[1] = 2
        sleep(2)
        self.assertFalse(called["deleted"])


    def test_no_expired(self):
        s = Storage(ttl=1, cleanup_interval=60)
        s[1] = 2
        sleep(2)
        self.assertNotIn(1, s)
        self.assertEqual(0, len([v for v in s]))


if __name__ == '__main__':
    unittest.main()
