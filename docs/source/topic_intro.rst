Introduction into Data Management
*********************************

What is Data Management in Testing?
===================================

In automated testing, especially **data-driven testing**, you often need consistent, well-structured test data.
This data can be:

- Simple values (names, IDs, numbers)
- Complex objects (users with addresses, orders with items)
- Related data (a blog post that belongs to an author)

Managing this data manually quickly becomes error-prone. You want to:

- Define data once and reuse it across many tests
- Load realistic sample data into your test environment
- Make sure the *device under test (DUT)* sees the same data the test expects
- Support different test scenarios (full data vs. restricted views, simulated vs. real systems)

The ``balderhub-data`` package gives you a clean, reusable solution for all of this inside the
**Balder test framework**.

Why ``balderhub-data``?
=======================

``balderhub-data`` is a foundational BalderHub package that **other BalderHub packages** (for example
``balderhub-crud``) and your own tests can rely on.

It provides:

- Structured **data models** that are type-safe and support relationships
- Automatic **loading and syncing** of sample data to your DUT
- Flexible **initial-data configuration** for different test environments
- Powerful **query/filter utilities** so tests can easily find the data they need

This keeps your tests readable, maintainable, and consistent, whether you are testing against a simulator, a staging
system, or a real device.

Main Concepts
=============

Data Items
----------

The central building block is a **data item**.
You define your own Python classes that inherit from :class:`balderhub.data.lib.utils.SingleDataItem`.

These classes are built on **Pydantic**, so they are:

- Strongly typed
- Support optional fields, nested objects, and lists
- Can declare a unique identifier (``get_unique_identification()`` method)

Example (simplified):

.. code-block:: python

   from balderhub.data.lib.utils import SingleDataItem

   class Author(SingleDataItem):
       first_name: str
       last_name: str

       def get_unique_identification(self):
           return f"{self.first_name}-{self.last_name}"

Data Environment Feature
------------------------

Inside a **Scenario**/**Setup** you use the :class:`balderhub.data.lib.feature.DataEnvironmentFeature`.
It gives you two methods, that keeps the test data and the system-under-test in sync:

- ``load_data()`` - loads your sample data set
- ``sync_environment()`` - pushes the data to the device under test (DUT)


Initial Data Configuration
--------------------------

To access or manage data for a specific data item, you can use the following feature classes:

- :class:`balderhub.data.lib.scenario_features.InitialDataConfig` - full access to all data
- :class:`balderhub.data.lib.scenario_features.AccessibleInitialDataConfig` - a restricted view (e.g. only data a certain user/role can see)

This is especially useful when you just want to access the data that was available initially or is accessible by a
specific user.

Factories & Automatic Wiring
----------------------------

``balderhub-data`` automatically registers factories for every data item type you use.
This means you rarely have to write boilerplate code to connect your data models to the test environment - Balder does
most of the work for you.

Further Utilities
-----------------

The package also ships handy helper classes such as:

- :class:`balderhub.data.lib.utils.SingleDataItemCollection` - a collection that supports powerful filtering and
  lookups (e.g. ``author__last_name="Smith"``)
- :class:`balderhub.data.lib.utils.filter.Filter` - base class for defining filters on `SingleDataItemCollection`
- :class:`balderhub.data.lib.utils.LookupFieldString` - a helper object that supports lookup strings like
  ``author__last_name="Smith"``


Next Steps
==========

* :doc:`installation` - how to install the package
* :doc:`features` - detailed look at all provided Features and classes
* :doc:`scenarios` - how to use data inside Scenarios
* :doc:`examples` - concrete code examples you can copy
* :doc:`utilities` - additional helper functions and classes

This package is still under active development.
Feedback and contributions are very welcome on the `GitHub repository <https://github.com/balder-dev/balderhub-data/>`_.

Happy data-driven testing! 🚀