#
# rena-python
#
# Copyright (c) 2019 Yuichiro MORIGUCHI
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
#
import unittest
from rena import *

class TestRena(unittest.TestCase):
    def match(self, ptn, string, index):
        self.assertEqual(index, ptn(string, 0, 0)[1])

    def matchInitAttr(self, ptn, string, init, index):
        self.assertEqual(index, ptn(string, 0, init)[1])

    def nomatch(self, ptn, string):
        self.assertIsNone(ptn(string, 0, 0)[1])

    def nomatchInitAttr(self, ptn, string, init):
        self.assertIsNone(ptn(string, 0, init)[1])

    def matchAttr(self, ptn, string, index, attr):
        self.assertEqual(index, ptn(string, 0, 0)[1])
        self.assertEqual(attr, ptn(string, 0, 0)[2])

    def matchAttrInitAttr(self, ptn, string, init, index, attr):
        self.assertEqual(index, ptn(string, 0, init)[1])
        self.assertEqual(attr, ptn(string, 0, init)[2])

    def test_simple(self):
        r = rena.Rena()
        self.match(r.then("765"), "765", 3)
        self.nomatch(r.then("765"), "961")
        self.nomatch(r.then("765"), "")

    def test_regex(self):
        r = rena.Rena()
        self.match(r.re("ab+"), "abbbbb", 6)
        self.match(r.re("ab+"), "ab", 2)
        self.nomatch(r.re("ab+"), "a")

    def test_then(self):
        r = rena.Rena()
        self.match(r.then("765", "pro"), "765pro", 6)
        self.nomatch(r.then("765", "pro"), "961pro")
        self.nomatch(r.then("765", "pro"), "765ab")
        self.nomatch(r.then("765", "pro"), "")

    def test_then_ignore(self):
        r = rena.Rena({ "ignore": " " })
        self.match(r.then("765", "pro"), "765pro", 6)
        self.match(r.then("765", "pro"), "765 pro", 7)
        self.match(r.then("765", "pro"), "765 pro ", 8)

    def test_choice(self):
        r = rena.Rena()
        self.match(r.choice("765", "346"), "765", 3)
        self.match(r.choice("765", "346"), "346", 3)
        self.nomatch(r.choice("765", "346"), "961")

    def test_times(self):
        r = rena.Rena()
        self.match(r.times(2, 4, "a"), "aaa", 3)
        self.match(r.times(2, 4, "a"), "aa", 2)
        self.match(r.times(2, 4, "a"), "aaaa", 4)
        self.match(r.times(2, 4, "a"), "aaaaa", 4)
        self.nomatch(r.times(2, 4, "a"), "a")
        self.match(r.times(2, None, "a"), "aa", 2)
        self.match(r.times(2, None, "a"), "aaaaa", 5)
        self.nomatch(r.times(2, None, "a"), "a")

    def test_times_ignore(self):
        r = rena.Rena({ "ignore": " " })
        self.match(r.times(2, 4, "a"), "aaa", 3)
        self.match(r.times(2, 4, "a"), "a aa", 4)
        self.match(r.times(2, 4, "a"), "aa a", 4)
        self.match(r.times(2, 4, "a"), "a a a ", 6)

    def test_times_attr(self):
        r = rena.Rena()
        self.matchAttrInitAttr(r.times(2, 4, r.re("[a-z]"), lambda m, s, i: m + i), "abc", "", 3, "cba")
        self.matchAttrInitAttr(
                r.times(2, 4, r.action(r.re("[1-9]"), lambda m, s, i: int(m)),
                    lambda m, s, i: i + s), "123", 0, 3, 6)

    def test_atLeast(self):
        r = rena.Rena()
        self.match(r.atLeast(2, "a"), "aa", 2)
        self.match(r.atLeast(2, "a"), "aaaaa", 5)
        self.nomatch(r.atLeast(2, "a"), "a")

    def test_atMost(self):
        r = rena.Rena()
        self.match(r.atMost(4, "a"), "aaa", 3)
        self.match(r.atMost(4, "a"), "aaaa", 4)
        self.match(r.atMost(4, "a"), "aaaaa", 4)
        self.match(r.atMost(4, "a"), "", 0)

    def test_oneOrMore(self):
        r = rena.Rena()
        self.match(r.oneOrMore("a"), "aaa", 3)
        self.match(r.oneOrMore("a"), "a", 1)
        self.nomatch(r.oneOrMore("a"), "")

    def test_zeroOrMore(self):
        r = rena.Rena()
        self.match(r.zeroOrMore("a"), "aaa", 3)
        self.match(r.zeroOrMore("a"), "a", 1)
        self.match(r.zeroOrMore("a"), "", 0)

    def test_maybe(self):
        r = rena.Rena()
        self.match(r.maybe("a"), "a", 1)
        self.match(r.maybe("a"), "aa", 1)
        self.match(r.maybe("a"), "", 0)

    def test_delimit(self):
        r = rena.Rena()
        self.match(r.delimit(r.re("[a-z]"), ","), "a", 1)
        self.match(r.delimit(r.re("[a-z]"), ","), "a,b,c", 5)
        self.match(r.delimit(r.re("[a-z]"), ","), "a,b,", 3)
        self.nomatch(r.delimit(r.re("[a-z]"), ","), "")
        self.nomatch(r.delimit(r.re("[a-z]"), ","), ",")

    def test_delimit_ignore(self):
        r = rena.Rena({ "ignore": " " })
        self.match(r.delimit(r.re("[a-z]"), ","), "a,a", 3)
        self.match(r.delimit(r.re("[a-z]"), ","), "a ,a", 4)
        self.match(r.delimit(r.re("[a-z]"), ","), "a, a", 4)
        self.match(r.delimit(r.re("[a-z]"), ","), "a,a ", 4)
        self.match(r.delimit(r.re("[a-z]"), ","), "a,a ,", 4)
        self.match(r.delimit(r.re("[a-z]"), ","), "a , a ,", 6)

    def test_delimit_attr(self):
        r = rena.Rena()
        self.matchAttrInitAttr(r.delimit(r.real(), "+", lambda m, s, i: i + s), "765", 0, 3, 765)
        self.matchAttrInitAttr(r.delimit(r.real(), "+", lambda m, s, i: i + s), "765+346", 0, 7, 1111)
        self.matchAttrInitAttr(r.delimit(r.real(), "+", lambda m, s, i: i + s), "765+1+2", 0, 7, 768)
        self.matchAttrInitAttr(r.delimit(r.real(), "+", lambda m, s, i: i + m), "765", "", 3, "765")
        self.matchAttrInitAttr(r.delimit(r.real(), "+", lambda m, s, i: i + m), "765+346", "", 7, "765346")
        self.matchAttrInitAttr(r.delimit(r.real(), "+", lambda m, s, i: i + m), "765+1+2", "", 7, "76512")

    def test_lookahead(self):
        r = rena.Rena()
        self.match(r.then("765", r.lookahead("pro")), "765pro", 3)
        self.nomatch(r.then("765", r.lookahead("pro")), "765pr")
        self.nomatch(r.then("765", r.lookahead("pro")), "961pro")

    def test_lookaheadNot(self):
        r = rena.Rena()
        self.match(r.then("765", r.lookaheadNot("aaa")), "765pro", 3)
        self.nomatch(r.then("765", r.lookaheadNot("aaa")), "765aaa")
        self.nomatch(r.then("765", r.lookaheadNot("aaa")), "961pro")

    def test_attr(self):
        r = rena.Rena()
        self.matchAttr(r.attr(27), "", 0, 27)

    def test_cond(self):
        r = rena.Rena()
        self.matchInitAttr(r.cond(lambda a: a == 27), "", 27, 0)
        self.nomatchInitAttr(r.cond(lambda a: a == 27), "", 29)

    def test_action(self):
        r = rena.Rena()
        self.matchAttrInitAttr(r.action("765", lambda m, s, a: m), "765", 29, 3, "765")
        self.matchAttrInitAttr(r.action("765", lambda m, s, a: a * a), "765", 29, 3, 841)
        self.nomatchInitAttr(r.action("765", lambda m, s, a: a * a), "961", 29)

    def test_key(self):
        r = rena.Rena({ "keys": [ "++", "+++", "-" ] })
        self.match(r.key("++"), "++", 2)
        self.match(r.key("-"), "-", 1)
        self.nomatch(r.key("++"), "+++")
        self.nomatch(r.key("++"), "+")

    def test_notKey(self):
        r = rena.Rena({ "keys": [ "++", "+++", "-" ] })
        self.match(r.notKey(), "+", 0)
        self.match(r.notKey(), "a", 0)
        self.nomatch(r.notKey(), "++")
        self.nomatch(r.notKey(), "-")
        self.nomatch(r.notKey(), "+++")

    def test_equalsId1(self):
        r = rena.Rena()
        self.match(r.equalsId("key"), "key", 3)
        self.match(r.equalsId("key"), "key ", 3)
        self.match(r.equalsId("key"), "keys", 3)
        self.match(r.equalsId("key"), "key++", 3)
        self.match(r.equalsId("key"), "key+", 3)

    def test_equalsId2(self):
        r = rena.Rena({ "ignore": " " })
        self.match(r.equalsId("key"), "key", 3)
        self.match(r.equalsId("key"), "key ", 4)
        self.nomatch(r.equalsId("key"), "keys")
        self.nomatch(r.equalsId("key"), "key++")
        self.nomatch(r.equalsId("key"), "key+")

    def test_equalsId3(self):
        r = rena.Rena({ "ignore": " ", "keys": [ "++" ] })
        self.match(r.equalsId("key"), "key", 3)
        self.match(r.equalsId("key"), "key ", 4)
        self.nomatch(r.equalsId("key"), "keys")
        self.match(r.equalsId("key"), "key++", 3)
        self.nomatch(r.equalsId("key"), "key+")

    def test_real(self):
        r = rena.Rena()
        self.matchAttr(r.real(), "0", 1, 0)
        self.matchAttr(r.real(), "765", 3, 765)
        self.matchAttr(r.real(), "76.5", 4, 76.5)
        self.matchAttr(r.real(), "0.765", 5, 0.765)
        self.matchAttr(r.real(), ".765", 4, 0.765)
        self.matchAttr(r.real(), "765e2", 5, 765e2)
        self.matchAttr(r.real(), "765E2", 5, 765E2)
        self.matchAttr(r.real(), "765e+2", 6, 765e+2)
        self.matchAttr(r.real(), "765e-2", 6, 765e-2)
        self.matchAttr(r.real(), "+765", 4, 765)
        self.matchAttr(r.real(), "+76.5", 5, 76.5)
        self.matchAttr(r.real(), "+0.765", 6, 0.765)
        self.matchAttr(r.real(), "+.765", 5, 0.765)
        self.matchAttr(r.real(), "+765e2", 6, 765e2)
        self.matchAttr(r.real(), "+765E2", 6, 765E2)
        self.matchAttr(r.real(), "+765e+2", 7, 765e+2)
        self.matchAttr(r.real(), "+765e-2", 7, 765e-2)
        self.matchAttr(r.real(), "-765", 4, -765)
        self.matchAttr(r.real(), "-76.5", 5, -76.5)
        self.matchAttr(r.real(), "-0.765", 6, -0.765)
        self.matchAttr(r.real(), "-.765", 5, -0.765)
        self.matchAttr(r.real(), "-765e2", 6, -765e2)
        self.matchAttr(r.real(), "-765E2", 6, -765E2)
        self.matchAttr(r.real(), "-765e+2", 7, -765e+2)
        self.matchAttr(r.real(), "-765e-2", 7, -765e-2)

    def test_br(self):
        r = rena.Rena()
        self.match(r.br(), "\r\n", 2)
        self.match(r.br(), "\r", 1)
        self.match(r.br(), "\n", 1)
        self.nomatch(r.br(), "a\r\n")

    def test_end(self):
        r = rena.Rena()
        self.match(r.then("765", r.end()), "765", 3)
        self.nomatch(r.then("765", r.end()), "765aaa")

    def test_letrec(self):
        r = rena.Rena()
        a = r.letrec(lambda x: r.then("(", r.maybe(x), ")"))
        self.match(a, "((()))", 6)
        self.match(a, "(()))", 4)
        self.nomatch(a, "((())")

if __name__ == "__main__":
    unittest.main()

