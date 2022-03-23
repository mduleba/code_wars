from __future__ import annotations

import copy
import re
from typing import List


class NotRecognizedLetter(NotImplementedError):
    pass


class Word:
    _state = None
    text = ''

    def __init__(self, state: State, initial_text: str = None):
        self.set_state(state)
        if initial_text:
            self.text = initial_text

    @property
    def is_final(self) -> bool:
        return self._state.__class__ == A3

    def get_final_value(self, word_length: int):
        return self.text.rjust(word_length, '-')

    def get_state_value(self):
        return self._state.value

    def set_state(self, state: State):
        self.text += state.value

        self._state = state
        self._state.word = self

    def unknown_state(self):
        raise NotRecognizedLetter

    @property
    def a(self):
        a_states = {
            B: self._state.a1,
            N1: self._state.a2,
            N2: self._state.a3
        }
        return a_states.get(self._state.__class__, self.unknown_state)

    @property
    def n(self):
        n_states = {
            A1: self._state.n1,
            A2: self._state.n2
        }
        return n_states.get(self._state.__class__, self.unknown_state)

    def __call__(self, command):
        decision = {
            'a': self.a,
            'n': self.n
        }
        try:
            decision[command]()
            return True
        except (KeyError, NotRecognizedLetter):
            self.text += '-'
            return False

    def __str__(self):
        return self.text


class State:
    value: str

    @property
    def word(self) -> word:
        return self._word

    @word.setter
    def word(self, word: word):
        self._word = word

    def b(self):
        raise NotRecognizedLetter

    def a1(self):
        raise NotRecognizedLetter

    def n1(self):
        raise NotRecognizedLetter

    def a2(self):
        raise NotRecognizedLetter

    def n2(self):
        raise NotRecognizedLetter

    def a3(self):
        raise NotRecognizedLetter


class B(State):
    value = 'b'

    def a1(self):
        self.word.set_state(A1())


class A1(State):
    value = 'a'

    def n1(self):
        self.word.set_state(N1())


class N1(State):
    value = 'n'

    def a2(self):
        self.word.set_state(A2())


class A2(State):
    value = 'a'

    def n2(self):
        self.word.set_state(N2())


class N2(State):
    value = 'n'

    def a3(self):
        self.word.set_state(A3())


class A3(State):
    value = 'a'


example = 'bbananana'


class BananaFinder:

    def __init__(self):
        self.word_list: List[Word] = []

    def clean_word(self, word: str):
        return re.sub("[^ban]+", "-", word.lower())

    def get_results(self, word_length) -> List[str]:
        return [word.get_final_value(word_length) for word in self.word_list if word.is_final]

    def find_bananas(self, word):
        word = self.clean_word(word)
        word_length = len(word)

        for letter in word:
            tmp_list = []

            for word_app in self.word_list:

                old_state = word_app._state
                old_text = word_app.text
                new_letter = word_app(letter)
                if new_letter:
                    tmp_app = Word(old_state, old_text + '-')
                    tmp_list.append(tmp_app)

            if letter == 'b':
                self.word_list.append(Word(B()))

            self.word_list += tmp_list

        return self.get_results(word_length)


finder = BananaFinder()
results = finder.find_bananas(example)