Experiment Overview
*******************
``Experiment`` is the central class of the Sacred framework. This section
should give you an overview on how to use it and all of its main mechanisms.

Create an Experiment
====================
To create an ``Experiment`` you need a name and a main method:

.. code-block:: python

    from sacred import Experiment
    ex = Experiment('my_experiment')

    @ex.main
    def my_main():
        pass

The function decorated with ``@ex.main`` is the main function of the experiment.
It is executed if you run the experiment and it is also used to determine
the source-file of the experiment.

Instead of ``@ex.main`` you can use ``@ex.automain``. This will
automatically run the experiment if you execute the file. It is equivalent to
the following.

.. code-block:: python

    from sacred import Experiment
    ex = Experiment('my_experiment')

    @ex.main
    def my_main():
        pass

    if __name__ == '__main__':
        ex.run_commandline()

.. note::
    For this to work the ``automain`` function needs to be at the end of the
    file. Otherwise everything below it is not defined yet when the
    experiment is run.


Run the Experiment
==================
The easiest way to run your experiment is to just use the command-line. This
requires that you used ``automain`` (or an equivalent). You can then just
execute the experiments python file and use the powerful :doc:`commandline`.

You can also run your experiment directly from python. This is especially useful
if you want to run it multiple times with different configurations. So lets say
your experiment is in a file called ``my_experiment.py``. Then you can import
it from there an run it like this:

.. code-block:: python

    from my_experiment import ex

    ex.run()

The ``run`` function accepts ``config_updates`` to specify how the configuration
should be changed for this run. It should be (possibly nested) dictionary
containing all the values that you wish to update. For more information see
:doc:`configuration`:

.. code-block:: python

    from my_experiment import ex

    ex.run(config_updates={'foo': 23})

You can also specify the log-level while calling ``run`` like so. See
:doc:`logging` for more information:

.. code-block:: python

    from my_experiment import ex

    ex.run(loglevel='DEBUG')


.. note::

    Under the hood a ``Run`` object is created every time you run an
    ``Experiment``. This object holds some information about that run (e.g. the
    final configuration) and is responsible for emitting all the events for the
    :doc:`observers`. You can access it by accepting the special `_run` argument
    in any of your :ref:`captured_functions`. It is also used for
    :ref:`custom_info`.


Configuration
=============
The easiest way to add configuration to an experiment is through a
:doc:`configuration`:

.. code-block:: python

    from sacred import Experiment
    ex = Experiment('my_experiment')

    @ex.config
    def my_config():
        foo = 42
        bar = 'baz'

The local variables from that function are collected and form the configuration
of your experiment. You have full access to the power of python when defining
the configuration that way. The parameters can even depend on each other.

.. note::
    Only variables that are JSON serializable (i.e. a numbers, strings,
    lists, tuples, dictionaries) become part of the configuration. Other
    variables are ignored.

    Also all variables starting with an underscore will be ignored.


Capture Functions
=================
To use a configuration value all you have to do is *capture* a function and
accept it as a parameter. Whenever you now call that function Sacred will
try to fill in missing parameters from the configuration.
To see how that works we need to *capture* some function:

.. code-block:: python

    from sacred import Experiment
    ex = Experiment('my_experiment')

    @ex.config
    def my_config():
        foo = 42
        bar = 'baz'

    @ex.capture
    def some_function(a, foo, bar=10)
        print(a, foo, bar)

    @ex.main
    def my_main()
        some_function(1, 2, 3)     #  1  2   3
        some_function(1)           #  1  42  'baz'
        some_function(1, bar=12)   #  1  42  12
        some_function()            #  TypeError: missing value for 'a'

.. note::
    Configuration values are preferred over default values. So in the example
    above, ``bar=10`` is never used because there is a value of ``bar = 'baz'``
    in the configuration.


Observe an Experiment
=====================
Experiments in Sacred collect lots of information about their runs like:

  - time it was started and time it stopped
  - the used configuration
  - the result or any errors that occurred
  - basic information about the machine it runs on
  - packages the experiment depends on and their versions
  - the source code of the experiment

To access these informations you can use the observer interface. First you need to
add an observer like this:

.. code-block:: python

    from sacred.observers import MongoObserver

    ex.observers.append(MongoObserver())

At the moment ``MongoObserver`` is the only observer that is shipped with
Sacred. It connects to a MongoDB and puts all these information into a document in a
collection called ``experiments``. You can also add this observer from the
:doc:`commandline` like this::

    >> python my_experiment.py -m my_database

For more information see :doc:`observers`

