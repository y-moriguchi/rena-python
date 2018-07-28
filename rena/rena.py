#
# rena-python
#
# Copyright (c) 2018 Yuichiro MORIGUCHI
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
#
import re

def Rena(ignore = None):
	return _RenaFactory(ignore)

class _RenaFactory:
	def __init__(self, ignore):
		self._ignore = ignore

	def find(self, pattern):
		return _RenaInstance(self).find(pattern)

	def alt(self, *alternation):
		return _RenaInstance(self).alt(*alternation)

	def times(self, countmin, countmax, pattern, action = None, init = None):
		return _RenaInstance(self).findTimes(countmin, countmax, pattern, action, init)

	def atLeast(self, count, pattern, action = None, init = None):
		return _RenaInstance(self).findAtLeast(count, pattern, action, init)

	def atMost(self, count, pattern, action = None, init = None):
		return _RenaInstance(self).findAtMost(count, pattern, action, init)

	def maybe(self, pattern, action = None, init = None):
		return _RenaInstance(self).findMaybe(pattern, action, init)

	def zeroOrMore(self, pattern, action = None, init = None):
		return _RenaInstance(self).findZeroOrMore(pattern, action, init)

	def oneOrMore(self, pattern, action = None, init = None):
		return _RenaInstance(self).findOneOrMore(pattern, action, init)

	def delimit(self, pattern, delimiter, action, init):
		return _RenaInstance(self).findDelimit(pattern, delimiter, action, init)

class _RenaInstance:
	def __init__(self, factory):
		self._factory = factory
		self._patterns = []

	def find(self, pattern, action = None):
		def aMethod(str, index, attribute):
			result = self._wrap(pattern)(str, index, attribute)
			if result is None:
				return result
			else:
				strnew, indexnew, attributenew = result
				return (strnew, indexnew, self._wrapAction(action)(strnew, attributenew, attribute))
		self._patterns.append(aMethod)
		return self

	def __add__(self, pattern):
		return self._factory.find(self, pattern)

	def alt(self, *alternation):
		def aMethod(str, index, attribute):
			for pattern in alternation:
				result = self._wrap(pattern)(str, index, attribute)
				if not(result is None):
					return result
			return None
		self._patterns.append(aMethod)
		return self

	def __or__(self, pattern):
		return self._factory.alt(self, pattern)

	def times(self, countmin, countmax, action = None, init = None):
		return self._factory.times(countmin, countmax, self, action, init)

	def atLeast(self, count, action = None, init = None):
		return self._factory.atLeast(count, self, action, init)

	def atMost(self, count, action = None, init = None):
		return self._factory.atMost(count, self, action, init)

	def maybe(self, action = None, init = None):
		return self._factory.maybe(self, action, init)

	def zeroOrMore(self, action = None, init = None):
		return self._factory.zeroOrMore(self, action, init)

	def oneOrMore(self, action = None, init = None):
		return self._factory.oneOrMore(self, action, init)

	def delimit(self, delimiter, action = None, init = None):
		return self._factory.delimit(self, delimiter, action, init)

	def findTimes(self, countmin, countmax, pattern, action = None, init = None):
		def aMethod(str, index, attribute):
			wrappedPtn = self._wrap(pattern)
			wrappedAction = self._wrapAction(action)
			count = 0
			indexnew = index
			inherited = init is None if attribute else init
			while countmax < 0 or count < countmax:
				result = wrappedPtn(str, indexnew, inherited)
				if result is None:
					break
				strnew, indexnew, attributenew = result
				inherited = wrappedAction(strnew, attributenew, inherited)
				indexnew = self._skipSpace(str, indexnew)
				count += 1
			return None if count < countmin else (str, indexnew, inherited)
		self._patterns.append(aMethod)
		return self

	def findAtLeast(self, count, pattern, action = None, init = None):
		return self.findTimes(count, -1, pattern, action, init)

	def findAtMost(self, count, pattern, action = None, init = None):
		return self.findTimes(0, count, pattern, action, init)

	def findMaybe(self, pattern, action = None):
		return self.findTimes(0, 1, pattern, action, None)

	def findZeroOrMore(self, pattern, action = None, init = None):
		return self.findTimes(0, -1, pattern, action, init)

	def findOneOrMore(self, pattern, action = None, init = None):
		return self.findTimes(1, -1, pattern, action, init)

	def findDelimit(self, pattern, delimiter, action = None, init = None):
		def aMethod(str, index, attribute):
			wrappedPtn = self._wrap(pattern)
			wrappedDelimit = self._wrap(delimiter)
			wrappedAction = self._wrapAction(action)
			inherited = attribute if init is None else init

			result = wrappedPtn(str, index, inherited)
			if result is None:
				return nil
			strnew, indexnew, attributenew = result
			inherited = wrappedAction(strnew, attributenew, inherited)
			indexnew = self._skipSpace(str, indexnew)
			while True:
				resultDelimit = wrappedDelimit(str, indexnew, inherited)
				if resultDelimit is None:
					return (str, indexnew, inherited)
				strnew, indexnew, attributenew = resultDelimit
				indexnew = self._skipSpace(str, indexnew)
				result = wrappedPtn(str, indexnew, inherited)
				if result is None:
					return nil
				strnew, indexnew, attributenew = result
				inherited = wrappedAction(strnew, attributenew, inherited)
				indexnew = self._skipSpace(str, indexnew)
		self._patterns.append(aMethod)
		return self

	def match(self, str, index = 0, attribute = None):
		strres, indexnew, attributenew = "", index, attribute
		for pattern in self._patterns:
			result = pattern(str, indexnew, attributenew)
			if result is None:
				return None
			strnew, indexnew, attributenew = result
			strres += strnew
		return (strres, indexnew, attributenew)

	def lookahead(self, pattern, positive = True):
		def aMethod(str, index, attribute):
			strnew, indexnew, attributenew = wrap(pattern)(str, index, attribute)
			return strnew is None != ("", index, attribute) if positive else None
		self._patterns.append(aMethod)
		return self

	def lookaheadNot(self, pattern, positive):
		return lookahead(pattern, False)

	def cond(self, condition):
		self._patterns.append(lambda str, index, attribute: ("", index, attribute) if condition(attribute) else None)
		return self

	def attribute(self, attribute):
		self._patterns.append(lambda str, index, ignored: ("", index, attribute))
		return self

	def action(self, action):
		self._patterns.append(lambda str, index, ignored: ("", index, action.call(attribute)))
		return self

	def _wrap(self, pattern):
		if type(pattern) is str:
			return lambda str, index, attribute: (pattern, index + len(pattern), None) if str.startswith(pattern, index) else None
		elif type(pattern) is re:
			def aMethod(str, index, attribute):
				result = pattern.match(str, index)
				return result and (result.group(0), index + len(result.group(0)), None)
			return aMethod
		elif isinstance(pattern, _RenaInstance):
			return lambda str, index, attribute: pattern.match(str, index, attribute)
		else:
			return pattern

	def _wrapAction(self, action):
		if action is None:
			return lambda match, attribute, inherited: attribute
		else:
			return action

	def _skipSpace(self, str, index):
		if not(self._factory._ignore is None):
			ignore1, indexnew, ignore3 = self._factory._ignore(str, index, nil)
			return indexnew
		else:
			return index
