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
        self._ignoreExp = None;
        if "ignore" in option:
            rbase = Rena()
            self._ignoreExp = rbase.wrap(option["ignore"]);

    def _ignore(self, match, lastIndex):
        if self._ignoreExp is None:
            return lastIndex
        else:
            matched, indexNew, attrNew = self._ignoreExp(match, lastIndex, 0)
            if matched is None:
                return lastIndex
            else:
                return indexNew

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

    def action(self, exp, action):
        wrapped = self.wrap(exp)
        def process(match, lastIndex, attr):
            matched, indexNew, attrNew = wrapped(match, lastIndex, attr)
            if matched is None:
                return (None, None, None)
            else:
                return (matched, indexNew, action(matched, attrNew, attr))
        return process

