import os
import random
import re

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .words import FREQUENT_WORDS


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def get_good_words():
    with open(os.path.join(__location__, 'new_words.txt'), 'r') as r:
        words = [w.strip() for w in r.readlines()]
    return words


def get_bad_words():
    with open(os.path.join(__location__, 'no_words.txt'), 'r') as r:
        words = [w.strip() for w in r.readlines()]
    return words


class MemaheretWOTHView(View):
    def get(self, request):
        word = random.choice(get_good_words())
        return HttpResponse(f'const word_of_the_day = "{word}";', content_type="application/x-javascript; charset=utf-8")


def _has_diff_letters(word: str) -> bool:
    fixed_word = word
    fixed_word = fixed_word.replace('ך', 'כ')
    fixed_word = fixed_word.replace('ם', 'מ')
    fixed_word = fixed_word.replace('ן', 'נ')
    fixed_word = fixed_word.replace('ף', 'פ')
    fixed_word = fixed_word.replace('ץ', 'צ')
    return len(set(fixed_word)) == 5


class AddWordsView(View):
    def get(self, request):
        while True:
            word = random.choice(FREQUENT_WORDS)
            if word in get_good_words() or word in get_bad_words():
                continue
            if not _has_diff_letters(word):
                with open(os.path.join(__location__, 'no_words.txt'), 'a') as w:
                    w.write(word + '\n')
            else:
                break

        context = {
            'word': word
        }
        return render(request, 'add_words.html', context=context)

    def post(self, request):
        word = request.POST['word']
        good = request.POST.get('good', False)

        if good:
            filename = 'new_words.txt'
        else:
            filename = 'no_words.txt'

        with open(os.path.join(__location__, filename), 'a') as writer:
            writer.write(word + '\n')

        words = request.POST['words']
        words = words.split('\n')
        good_words = []
        already = get_good_words()
        for w in words:
            w = w.strip()
            if re.search(r'^[אבגדהוזחטיכלמנסעפצקרשתךםןףץ]{5}$', w) and _has_diff_letters(w) and w not in already:
                good_words.append(w)
        if good_words:
            with open(os.path.join(__location__, 'new_words.txt'), 'a') as writer:
                for w in good_words:
                    writer.write(w + '\n')

        return HttpResponseRedirect('/add_word/')
