import json
import os
import random
import re

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .words import FREQUENT_WORDS


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

_WORD = re.compile(r'[אבגדהוזחטיכלמנסעפצקרשתךםןףץ]{5}')


def is_valid_word(word: str) -> bool:
    """Five Hebrew letters, all different (final forms count as their letter)."""
    return bool(_WORD.fullmatch(word)) and _has_diff_letters(word)


def _read_words(filename: str):
    with open(os.path.join(__location__, filename), 'r') as r:
        return [w.strip() for w in r.readlines()]


def get_good_words():
    # Only real words: they are served to the game's pages (woth.js).
    return [w for w in _read_words('new_words.txt') if is_valid_word(w)]


def get_bad_words():
    return _read_words('no_words.txt')


class MemaheretWOTHView(View):
    def get(self, request):
        word = random.choice(get_good_words())
        # A JavaScript string literal, whatever the word is.
        return HttpResponse(f'const word_of_the_day = {json.dumps(word)};',
                            content_type="application/x-javascript; charset=utf-8")


def _has_diff_letters(word: str) -> bool:
    fixed_word = word
    fixed_word = fixed_word.replace('ך', 'כ')
    fixed_word = fixed_word.replace('ם', 'מ')
    fixed_word = fixed_word.replace('ן', 'נ')
    fixed_word = fixed_word.replace('ף', 'פ')
    fixed_word = fixed_word.replace('ץ', 'צ')
    return len(set(fixed_word)) == 5


class AddWordsView(LoginRequiredMixin, UserPassesTestMixin, View):
    """For superusers only: what they add is served to the game's pages."""

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        known = set(get_good_words()) | set(get_bad_words())
        while True:
            word = random.choice(FREQUENT_WORDS)
            if word in known:
                continue
            if not _has_diff_letters(word):
                with open(os.path.join(__location__, 'no_words.txt'), 'a') as w:
                    w.write(word + '\n')
                known.add(word)
            else:
                break

        context = {
            'word': word
        }
        return render(request, 'add_words.html', context=context)

    def post(self, request):
        word = request.POST.get('word', '').strip()
        good = request.POST.get('good', False)

        if good:
            filename = 'new_words.txt'
        else:
            filename = 'no_words.txt'

        if is_valid_word(word):
            with open(os.path.join(__location__, filename), 'a') as writer:
                writer.write(word + '\n')

        words = request.POST.get('words', '')
        words = words.split('\n')
        good_words = []
        already = get_good_words()
        for w in words:
            w = w.strip()
            if is_valid_word(w) and w not in already:
                good_words.append(w)
        if good_words:
            with open(os.path.join(__location__, 'new_words.txt'), 'a') as writer:
                for w in good_words:
                    writer.write(w + '\n')

        return HttpResponseRedirect('/add_word/')
