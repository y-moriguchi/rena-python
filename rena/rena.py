#
# rena-python
#
# Copyright (c) 2019 Yuichiro MORIGUCHI
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
#
import re;

class Rena:
    def __init__(self, option={}):
        self._ignoreExp = None
        if "ignore" in option:
            rbase = Rena()
            self._ignoreExp = rbase.wrap(option["ignore"])
        self._trie = None
        if "keys" in option:
            self._trie = {}
            for key in option["keys"]:
                trie = self._trie
                for ch in key:
                    if not ch in trie:
                        trie[ch] = {}
                    trie = trie[ch]

    def _ignore(self, match, lastIndex):
        if self._ignoreExp is None:
            return lastIndex
        else:
            matched, indexNew, attrNew = self._ignoreExp(match, lastIndex, 0)
            if matched is None:
                return lastIndex
            else:
                return indexNew

    def _findKey(self, match, lastIndex):
        if self._trie is None:
            return ""
        trie = self._trie
        i = lastIndex
        while i < len(match):
            ch = match[i]
            if ch in trie:
                trie = trie[ch]
                i += 1
            else:
                break
        return match[lastIndex:i]

    def wrap(self, obj):
        if type(obj) is str:
            def process(match, lastIndex, attr):
                if match.startswith(obj, lastIndex):
                    return (obj, lastIndex + len(obj), attr)
                else:
                    return (None, None, None)
            return process
        else:
            return obj

    def re(self, pattern):
        compiledRe = re.compile(pattern)
        def process(match, lastIndex, attr):
            result = compiledRe.match(match, lastIndex)
            if result:
                return (result.group(0), lastIndex + len(result.group(0)), attr)
            else:
                return (None, None, None)
        return process

    def then(self, *exps):
        def process(match, lastIndex, attr):
            matched = ""
            indexNew = lastIndex
            attrNew = attr
            for exp in exps:
                wrapped = self.wrap(exp)
                matched, indexNew, attrNew = wrapped(match, indexNew, attrNew)
                if matched is None:
                    return (None, None, None)
                else:
                    indexNew = self._ignore(match, indexNew)
            return (match[lastIndex:indexNew], indexNew, attrNew)
        return process

    def choice(self, *exps):
        def process(match, lastIndex, attr):
            for exp in exps:
                wrapped = self.wrap(exp)
                matched, indexNew, attrNew = wrapped(match, lastIndex, attr)
                if matched is not None:
                    return (matched, indexNew, attrNew)
            return (None, None, None)
        return process

    def times(self, mincount, maxcount, exp, action=lambda match, syn, inh: syn):
        wrapped = self.wrap(exp)
        def process(match, lastIndex, attr):
            matched = ""
            indexNew = lastIndex
            attrNew = attr
            count = 0
            matchedLoop, indexLoop, attrLoop = "", lastIndex, attr
            while maxcount is None or count < maxcount:
                matchedLoop, indexLoop, attrLoop = wrapped(match, indexNew, attrNew)
                if matchedLoop is None:
                    if count < mincount:
                        return (None, None, None)
                    else:
                        return (match[lastIndex:indexNew], indexNew, attrNew)
                else:
                    indexNew = self._ignore(match, indexLoop)
                    attrNew = action(matchedLoop, attrLoop, attrNew)
            return (match[lastIndex:indexNew], indexNew, attrNew)
        return process

    def atLeast(self, mincount, exp, action=lambda match, syn, inh: syn):
        return self.times(mincount, None, exp, action)

    def atMost(self, maxcount, exp, action=lambda match, syn, inh: syn):
        return self.times(0, maxcount, exp, action)

    def oneOrMore(self, exp, action=lambda match, syn, inh: syn):
        return self.times(1, None, exp, action)

    def zeroOrMore(self, exp, action=lambda match, syn, inh: syn):
        return self.times(0, None, exp, action)

    def maybe(self, exp):
        return self.times(0, 1, exp)

    def delimit(self, exp, delimiter, action=lambda match, syn, inh: syn):
        wrapped = self.wrap(exp)
        wrappedDelimiter = self.wrap(delimiter)
        def process(match, lastIndex, attr):
            matched = ""
            indexNew = lastIndex
            attrNew = attr
            matchedLoop, indexLoop, attrLoop = "", lastIndex, attr
            already = False
            while True:
                matchedLoop, indexLoop, attrLoop = wrapped(match, indexLoop, attrLoop)
                if matchedLoop is None:
                    if already:
                        return (match[lastIndex:indexNew], indexNew, attrNew)
                    else:
                        return (None, None, None)
                else:
                    already = True
                    matched, indexNew, attrNew = matchedLoop, indexLoop, attrLoop
                    indexLoop = self._ignore(match, indexLoop)
                    matchedLoop, indexLoop, attrLoop = wrappedDelimiter(match, indexLoop, attrLoop)
                    if matchedLoop is None:
                        return (match[lastIndex:indexNew], indexNew, attrNew)
                    indexLoop = self._ignore(match, indexLoop)
        return process

    def lookahead(self, exp, signum=True):
        wrapped = self.wrap(exp)
        def process(match, lastIndex, attr):
            matched, indexNew, attrNew = wrapped(match, lastIndex, attr)
            if (signum and matched is not None) or (not signum and matched is None):
                return ("", lastIndex, attr)
            else:
                return (None, None, None)
        return process

    def lookaheadNot(self, exp):
        return self.lookahead(exp, False)

    def attr(self, attr):
        return lambda match, lastIndex, attrOld: (match, lastIndex, attr)

    def cond(self, predicate):
        def process(match, lastIndex, attr):
            if predicate(attr):
                return ("", lastIndex, attr)
            else:
                return (None, None, None)
        return process

    def action(self, exp, action):
        wrapped = self.wrap(exp)
        def process(match, lastIndex, attr):
            matched, indexNew, attrNew = wrapped(match, lastIndex, attr)
            if matched is None:
                return (None, None, None)
            else:
                return (matched, indexNew, action(matched, attrNew, attr))
        return process

    def key(self, key):
        def process(match, lastIndex, attr):
            matchedKey = self._findKey(match, lastIndex)
            if matchedKey == key:
                return (key, lastIndex + len(key), attr)
            else:
                return (None, None, None)
        return process

    def notKey(self):
        def process(match, lastIndex, attr):
            matchedKey = self._findKey(match, lastIndex)
            if matchedKey == "":
                return ("", lastIndex, attr)
            else:
                return (None, None, None)
        return process

    def equalsId(self, keyword):
        wrapped = self.wrap(keyword)
        def process(match, lastIndex, attr):
            matched, indexNew, attrNew = wrapped(match, lastIndex, attr)
            if matched is None:
                return (None, None, None)
            elif indexNew == len(match):
                return (matched, indexNew, attrNew)
            elif self._ignoreExp is None and self._trie is None:
                return (matched, indexNew, attrNew)
            elif self._ignoreExp is not None and self._ignore(match, indexNew) != indexNew:
                return (matched, self._ignore(match, indexNew), attrNew)
            elif self._trie is not None and self._findKey(match, indexNew) != "":
                return (matched, indexNew, attrNew)
            else:
                return (None, None, None)
        return process

    def real(self):
        realPattern = re.compile(r'[\+\-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][\+\-]?[0-9]+)?')
        def process(match, lastIndex, attr):
            matched = realPattern.match(match, lastIndex)
            if matched:
                return (matched.group(0), lastIndex + len(matched.group(0)), float(matched.group(0)))
            else:
                return (None, None, None)
        return process

    def br(self):
        return self.re(r'\r\n|\r|\n')

    def end(self):
        def process(match, lastIndex, attr):
            if lastIndex == len(match):
                return ("", lastIndex, attr)
            else:
                return (None, None, None)
        return process

    def letrec(self, *args):
        funcg = lambda g: g(g)
        def funcp(p):
            res = []
            for arg in args:
                def inner(match, lastIndex, attr):
                    return (self.wrap(arg(*p(p))))(match, lastIndex, attr)
                res.append(inner)
            return res
        res = funcg(funcp)
        return res[0]

