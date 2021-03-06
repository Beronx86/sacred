Command-Line Interface
**********************

Sacred provides a powerful command line interface for every experiment out of
box. All you have to do to use it is to either have a method decorated with
``@ex.automain`` or to put this block at the end of your file:

.. code-block:: python

    if __name__ == '__main__':
        ex.run_commandline()


Configuration Updates
=====================
You can easily change any configuration entry using the powerful
``with`` command on the commandline. Just put ``with config=update`` after your
experiment call like this::

    >>> ./example.py with 'a=10'

Or even multiple values just separated by a space::

    >>> ./example.py with 'a=2.3' 'b="FooBar"' 'c=True'


.. note::
    The single quotes (``'``) around each statement are to make sure the bash
    does not interfere. In simple cases you can omit them::

       >>> ./example.py with a=-1 b=2.0 c=True

    But be careful especially with strings, because the outermost quotes get
    removed by bash.
    So for example all of the following values will be ``int``::

       >>> ./example.py with a=1 b="2" c='3'


You can use the standard python literal syntax to set numbers, bools, lists,
dicts, strings and combinations thereof::

    >>> ./example.py with 'my_list=[1, 2, 3]'
    >>> ./example.py with 'nested_list=[["a", "b"], [2, 3], False]'
    >>> ./example.py with 'my_dict={"a":1, "b":[-.2, "two"]}'
    >>> ./example.py with 'alpha=-.3e-7'
    >>> ./example.py with 'mask=0b111000'
    >>> ./example.py with 'message="Hello Bob!"'

**Dotted Notation**

If you want to set individual entries of a dictionary you can use the dotted
notation to do so. So if this is the ConfigScope of our experiment:

.. code-block:: python

    @ex.config
    def cfg():
        d = {
            "foo": 1,
            "bar": 2,
        }

Then we could just change the ``"foo"`` entry of our dictionary to ``100`` like
this::

    >>> ./example.py with 'd.foo=100'

.. warning::
    This assumes that all the keys in the dict are strings and do not contain
    any dots. It is strongly recommended to only use *valid python identifiers*
    as keys. Other choices might cause errors!

Print Config
============

To inspect the configuration of your experiment and see how changes from the
command-line affect it you can use the ``print_config`` command. The full
configuration of the experiment and all nested dictionaries will be printed with
indentation. So lets say we added the dictionary from above to the
``hello_config.py`` example::

    >>> ./hello_config print_config
    INFO - hello_config - Running command 'print_config'
    INFO - hello_config - Started
    Configuration (modified, added, typechanged):
      message = 'Hello world!'
      recipient = 'world'
      seed = 946502320
      d:
        bar = 2
        foo = 1
    INFO - hello_config - Completed after 0:00:00

This command is especially helpful to see how ``with config=update`` statements
affect the configuration. It will highlight modified entries in **green**, added
entries in **blue** and entries whose type has changed in **red**:

    ===========  =====
    Change       Color
    ===========  =====
    modified     blue
    added        green
    typechanged  red
    ===========  =====

But Sacred will also print warnings for all added and typechanged entries, to
help you find typos and update mistakes::

    >> ./hello_config.py print_config with 'recipient="Bob"' d.foo=True d.baz=3
    WARNING - root - Added new config entry: "d.baz"
    WARNING - root - Changed type of config entry "d.foo" from int to bool
    INFO - hello_config - Running command 'print_config'
    INFO - hello_config - Started
    Configuration (modified, added, typechanged):
      message = 'Hello Bob!'
      recipient = 'Bob'        # blue
      seed = 676870791
      d:                       # blue
        bar = 2
        baz = 3                # green
        foo = True             # red
    INFO - hello_config - Completed after 0:00:00

Custom Commands
===============
If you just run an experiment file it will execute the default command, that
is the method you decorated with ``@ex.main`` or ``@ex.automain``. But you
can also add other commands to the experiment by using ``@ex.command``:

.. code-block:: python

    from sacred import Experiment

    ex = Experiment('custom_command')

    @ex.command
    def scream():
        """
        scream, and shout, and let it all out ...
        """
        print('AAAaaaaaaaahhhhhh...')

    # ...

This command can then be run like this::

    >> ./custom_command.py scream
    INFO - custom_command - Running command 'scream'
    INFO - custom_command - Started
    AAAaaaaaaaahhhhhh...
    INFO - custom_command - Completed after 0:00:00

It will also show up in the usage message and you can get the signature and
the docstring by passing it to help::

    >> ./custom_command.py help scream

    scream()
        scream, and shout, and let it all out ...

Commands are of course also captured functions, so you can take arguments that
will get filled in from the config, and you can use ``with config=update`` to
change parameters from the commandline:

.. code-block:: python

    @ex.command
    def greet(name):
        """
        Print a simple greet message.
        """
        print('Hello %s!' % name)

And call it like this::

    >> ./custom_command.py greet with 'name="Bob"'
    INFO - custom_command - Running command 'scream'
    INFO - custom_command - Started
    Hello Bob!
    INFO - custom_command - Completed after 0:00:00

Flags
=====

**Help**

+------------+-----------------------------+
| ``-h``     |  Print Usage                |
+------------+                             |
| ``--help`` |                             |
+------------+-----------------------------+

This prints a help/usage message for your experiment.
It is equivalent to typing just ``help``.

**Logging Level**

+---------------------+-----------------------------+
| ``-l LEVEL``        |  control the logging level  |
+---------------------+                             |
| ``--logging=LEVEL`` |                             |
+---------------------+-----------------------------+

With this flag you can adjust the logging level.

+----------+---------------+
| Level    | Numeric value |
+==========+===============+
| CRITICAL | 50            |
+----------+---------------+
| ERROR    | 40            |
+----------+---------------+
| WARNING  | 30            |
+----------+---------------+
| INFO     | 20            |
+----------+---------------+
| DEBUG    | 10            |
+----------+---------------+
| NOTSET   | 0             |
+----------+---------------+

See :ref:`log_levels` for more details.

**MongoDB Observer**

+-------------------+--------------------------+
| ``-m DB``         |  add a MongoDB observer  |
+-------------------+                          |
| ``--mongo_db=DB`` |                          |
+-------------------+--------------------------+


This flag can be used to add a MongoDB observer to your experiment. ``DB`` must
be of the form ``db_name`` or ``[host:port:]db_name``.

See :ref:`mongo_observer` for more details.

**Debug Mode**

+-------------------+-------------------------------+
| ``-d``            |  don't filter the stacktrace  |
+-------------------+                               |
| ``--debug``       |                               |
+-------------------+-------------------------------+

This flag deactivates the stacktrace filtering. You should usually not need
this. It is mainly used for debugging Sacred.
