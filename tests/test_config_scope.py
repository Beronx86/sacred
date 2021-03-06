#!/usr/bin/env python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
import pytest
from sacred.custom_containers import DogmaticDict, DogmaticList
from sacred.config_scope import (ConfigScope, dedent_line, is_empty_or_comment,
                                 dedent_function_body, get_function_body)

try:
    import numpy as np
except ImportError:
    np = None


@pytest.fixture
def conf_scope():
    @ConfigScope
    def cfg():
        a = 1
        b = 2.0
        c = True
        d = 'string'
        e = [1, 2, 3]
        f = {'a': 'b', 'c': 'd'}
        composit1 = a + b
        composit2 = f['c'] + "ada"

        ignored1 = lambda: 23

        deriv = ignored1()

        def ignored2():
            pass

        ignored3 = int

        _ignored4 = 'eventhough it is a string'

    cfg()
    return cfg


def test_config_scope_is_dict(conf_scope):
    assert isinstance(conf_scope, ConfigScope)
    assert isinstance(conf_scope, dict)


def test_config_scope_contains_keys(conf_scope):
    assert set(conf_scope.keys()) == {'a', 'b', 'c', 'd', 'e', 'f',
                                      'composit1', 'composit2', 'deriv'}

    assert conf_scope['a'] == 1
    assert conf_scope['b'] == 2.0
    assert conf_scope['c']
    assert conf_scope['d'] == 'string'
    assert conf_scope['e'] == [1, 2, 3]
    assert conf_scope['f'] == {'a': 'b', 'c': 'd'}
    assert conf_scope['composit1'] == 3.0
    assert conf_scope['composit2'] == 'dada'
    assert conf_scope['deriv'] == 23


def test_fixing_values(conf_scope):
    conf_scope({'a': 100})
    assert conf_scope['a'] == 100
    assert conf_scope['composit1'] == 102.0


def test_fixing_nested_dicts(conf_scope):
    conf_scope({'f': {'c': 't'}})
    assert conf_scope['f']['a'] == 'b'
    assert conf_scope['f']['c'] == 't'
    assert conf_scope['composit2'] == 'tada'


def test_adding_values(conf_scope):
    conf_scope({'g': 23, 'h': {'i': 10}})
    assert conf_scope['g'] == 23
    assert conf_scope['h'] == {'i': 10}
    assert conf_scope.added_values == {'g', 'h', 'h.i'}


def test_typechange(conf_scope):
    conf_scope({'a': 'bar', 'b': 'foo', 'c': 1})
    assert conf_scope.typechanges == {'a': (int, type('bar')),
                                      'b': (float, type('foo')),
                                      'c': (bool, int)}


def test_nested_typechange(conf_scope):
    conf_scope({'f': {'a': 10}})
    assert conf_scope.typechanges == {'f.a': (type('a'), int)}


def is_dogmatic(a):
    if isinstance(a, (DogmaticDict, DogmaticList)):
        return True
    elif isinstance(a, dict):
        return any(is_dogmatic(v) for v in a.values())
    elif isinstance(a, (list, tuple)):
        return any(is_dogmatic(v) for v in a)


def test_conf_scope_is_not_dogmatic(conf_scope):
    conf_scope({'e': [1, 1, 1]})
    assert not is_dogmatic(conf_scope)


@pytest.mark.skipif(np is None, reason="requires numpy")
def test_conf_scope_handles_numpy_bools():
    @ConfigScope
    def cfg():
        a = np.bool_(1)

    cfg()
    assert 'a' in cfg
    assert cfg['a']


def test_conf_scope_can_access_preset():
    @ConfigScope
    def cfg(a):
        answer = 2 * a

    cfg(preset={'a': 21})
    assert cfg['answer'] == 42


def test_conf_scope_contains_presets():
    @ConfigScope
    def cfg(a):
        answer = 2 * a

    cfg(preset={'a': 21, 'unrelated': True})
    assert set(cfg.keys()) == {'a', 'answer', 'unrelated'}
    assert cfg['a'] == 21
    assert cfg['answer'] == 42
    assert cfg['unrelated'] is True


def test_conf_scope_cannot_access_undeclared_presets():
    @ConfigScope
    def cfg():
        answer = 2 * a

    with pytest.raises(NameError):
        cfg(preset={'a': 21})


def test_conf_scope_can_access_fallback():
    @ConfigScope
    def cfg(a):
        answer = 2 * a

    cfg(fallback={'a': 21})
    assert cfg['answer'] == 42


def test_conf_scope_does_not_contain_fallback():
    @ConfigScope
    def cfg(a):
        answer = 2 * a

    cfg(fallback={'a': 21, 'b': 10})

    assert set(cfg.keys()) == {'answer'}


def test_conf_scope_cannot_access_undeclared_fallback():
    @ConfigScope
    def cfg():
        answer = 2 * a

    with pytest.raises(NameError):
        cfg(fallback={'a': 21})


def test_conf_scope_can_access_fallback_and_preset():
    @ConfigScope
    def cfg(a, b):
        answer = a + b

    cfg(preset={'b': 40}, fallback={'a': 2})
    assert cfg['answer'] == 42


def test_conf_raises_for_unaccessible_arguments():
    @ConfigScope
    def cfg(a, b, c):
        answer = 42

    with pytest.raises(KeyError):
        cfg(preset={'a': 1}, fallback={'b': 2})


def test_can_access_globals_from_original_scope():
    from .enclosed_config_scope import cfg
    cfg()
    assert set(cfg.keys()) == {'answer'}
    assert cfg['answer'] == 42


SEVEN = 7


def test_cannot_access_globals_from_calling_scope():
    from .enclosed_config_scope import cfg2
    with pytest.raises(NameError):
        cfg2()  # would require SEVEN


def test_fixed_subentry_of_preset():
    @ConfigScope
    def cfg():
        pass

    cfg(preset={'d': {'a': 1, 'b': 2}}, fixed={'d': {'a': 10}})

    assert set(cfg.keys()) == {'d'}
    assert set(cfg['d'].keys()) == {'a', 'b'}
    assert cfg['d']['a'] == 10
    assert cfg['d']['b'] == 2


@pytest.mark.parametrize("line,indent,expected", [
    ('    a=5', '    ', 'a=5'),
    ('  a=5',   '    ', 'a=5'),
    ('a=5',     '    ', 'a=5'),
    ('    a=5', '  ',   '  a=5'),
    ('    a=5', '',     '    a=5'),
    ('    a=5', '\t',   '    a=5'),
    ('  a=5', '      ', 'a=5'),
    ('    a=5', '  \t', '  a=5')
])
def test_dedent_line(line, indent, expected):
    assert dedent_line(line, indent) == expected


@pytest.mark.parametrize("line,expected", [
    ('', True),
    ('  ', True),
    ('\n', True),
    ('    \n', True),
    ('  \t \n', True),
    ('#comment', True),
    ('   #comment', True),
    ('  a=5 # not comment', False),
    ('a=5', False),
    ('"""', False),
    ("'''", False)

])
def test_is_empty_or_comment(line, expected):
    assert is_empty_or_comment(line) == expected


def evil_indentation_func(a,
                                    b,
c, d):
# Lets do the most evil things with indentation
  # 1
    # 2
     # ran
        """ and also in the docstring
             atrne
    uiaeue
utdr
    """
        alpha = 0.1
        d = ('even', 'more',
    'evilness')
        wat = """ multi
    line
strings
    """
# another comment
        # this one is ok
    # madness
        foo=12

        def subfunc():
            return 23

body = '''# Lets do the most evil things with indentation
  # 1
    # 2
     # ran
        """ and also in the docstring
             atrne
    uiaeue
utdr
    """
        alpha = 0.1
        d = ('even', 'more',
    'evilness')
        wat = """ multi
    line
strings
    """
# another comment
        # this one is ok
    # madness
        foo=12

        def subfunc():
            return 23
'''

dedented_body = '''# Lets do the most evil things with indentation
# 1
# 2
# ran
""" and also in the docstring
     atrne
uiaeue
utdr
"""
alpha = 0.1
d = ('even', 'more',
'evilness')
wat = """ multi
line
strings
"""
# another comment
# this one is ok
# madness
foo=12

def subfunc():
    return 23
'''


def test_dedent_body():
    assert dedent_function_body(body) == dedented_body


def test_get_function_body():
    func_body, line_offset = get_function_body(evil_indentation_func)
    assert func_body == body


def test_config_scope_can_deal_with_indentation_madness():
    # assert_no_raise:
    ConfigScope(evil_indentation_func)


