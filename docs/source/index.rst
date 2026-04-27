Welcome to balderhub-data
=========================

**balderhub-data** is the official BalderHub package for **structured, reusable test data** in the
`Balder test framework <https://docs.balder.dev>`_.

It makes data-driven testing clean, type-safe, and maintainable by giving you powerful building blocks to define, load,
sync, and query test data - whether you are working with a simulator, staging environment, or real device under test.

What you will find in this package
==================================

This documentation is organised around the core pieces you will use every day:

* **Data Models**
  Define your own type-safe data items with :class:`balderhub.data.lib.utils.SingleDataItem`.
  Built on Pydantic - supports nested objects, lists, relationships, and unique identifiers.

* **Data Environment Feature**
  Use :class:`balderhub.data.lib.feature.DataEnvironmentFeature` inside Scenarios to load sample data and automatically
  keep the device under test in sync.

* **Initial Data Configuration**
  Control exactly what data your test setups can see with :class:`balderhub.data.lib.feature.InitialDataConfig` and
  :class:`balderhub.data.lib.feature.AccessibleInitialDataConfig` (perfect for permission and visibility testing).

* **Powerful Utilities**
  Collections, filters, factories, and query helpers that let you find the exact data you need with clean, readable
  syntax (e.g. ``author__last_name="Smith"``).

* **Ready-to-use Examples**
  Concrete code snippets and full scenarios that you can copy straight into your own tests.

.. toctree::
   :maxdepth: 2

   installation.rst
   topic_intro.rst
   scenarios.rst
   features.rst
   examples.rst
   utilities.rst
   contrib.rst

Quick start
-----------

.. code-block:: bash

   python -m pip install balderhub-data

Then head to the :ref:`Introduction into Data Management` to see how everything fits together - or jump straight into the :ref:`examples` if
you prefer to learn by code.

**Happy data-driven testing!** 🚀

If you have questions or ideas, feel free to open an issue or pull request on the
`GitHub repository <https://github.com/balder-dev/balderhub-data>`_.