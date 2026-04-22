Examples
********

The BalderHub data package provides various types of objects for defining data class models. These are particularly
helpful for data-related tests, such as those in `balderhub-crud <https://hub.balder.dev/projects/crud>`_ or
`balderhub-auth <https://hub.balder.dev/projects/auth>`_.


Defining Your Own Data Model Structure
======================================

This package allows you to define your own data model structure by using the
:class:`balderhub.data.lib.utils.SingleDataItem` as the base class:

.. code-block:: python

    from typing import Optional
    from balderhub.data.lib.utils import SingleDataItem


    class AuthorDataItem(SingleDataItem):
        id: int
        first_name: str
        last_name: str

        def get_unique_identification(self):
            return self.id

    class BookCategoryDataItem(SingleDataItem):
        id: int
        name: str

        def get_unique_identification(self):
            return self.id


    class BookDataItem(SingleDataItem):
        id: int
        title: str
        author: AuthorDataItem
        category: Optional[BookCategoryDataItem] = None

        def get_unique_identification(self):
            return self.id

You can use the following types within :class:`balderhub.data.lib.utils.SingleDataItem`:

* base types like `str`, `int`, `bool`, `float`, etc.
* declare a type as optional with `typing.Optional[int]` or `typing.Union[int, None]` (both are equal and accepted)
* nested data items (referred data item needs to be another :class:`balderhub.data.lib.utils.SingleDataItem`)

What is not allowed:

* multiple possible types defined by `typing.Union[int, float, ..]` (except the Optional like definition:
  `typing.Union[int, None]`)
* list types other than `list[MyDataItem]` (where `MyDataItem` is a `SingleDataItem` subclass)
* dictionary types: use nested data items for that

Interacting with `SingleDataItem` Objects
=========================================

The package provides various ways to interact with data items.

For more details, see the API documentation for :class:`balderhub.data.lib.utils.SingleDataItem` and
:class:`balderhub.data.lib.utils.SingleDataItemCollection`.

For referencing fields, especially nested fields, use :class:`balderhub.data.lib.utils.LookupFieldString`.

For example, to access the author's last name from a `BookDataItem` instance, use ``author__last_name``. The
project will automatically convert strings like that to `LookupFieldString` objects.

Using the Data Environment Feature
==================================

Most features use the :class:`balderhub.data.lib.scenario_features.DataEnvironmentFeature`, which
allows you to define your own data samples.

.. code-block:: python

    from balderhub.data.lib.scenario_features.data_environment_feature import DataEnvironmentFeature
    from tests.lib.utils import data_items
    from tests.lib.setup_features.dut_simulator_feature import DutSimulatorFeature
    from tests.lib.utils.dut_simulator import DutSimulator


    class TestDataEnvironment(DataEnvironmentFeature):

        sim = DutSimulatorFeature()

        def load_data(self):

            self._add_data(data_items.AuthorDataItem(id=1, first_name='J.K.', last_name='Rowling'))
            self._add_data(data_items.AuthorDataItem(id=2, first_name='J.R.R.', last_name='Tolkien'))
            self._add_data(data_items.AuthorDataItem(id=3, first_name='A.B.C.', last_name='Alphabet'))

            self._add_data(data_items.BookCategoryDataItem(id=1, name='Fantasy'))
            self._add_data(data_items.BookCategoryDataItem(id=2, name='Science Fiction'))
            self._add_data(data_items.BookCategoryDataItem(id=3, name='Action'))

            self._add_data(data_items.BookDataItem(
                id=1, title='Harry Potter and the Sorcerer’s Stone',
                author=self.get(data_items.AuthorDataItem, 1),
                category=self.get(data_items.BookCategoryDataItem, 1))
            )

            self._add_data(data_items.BookDataItem(
                id=2, title='Harry Potter and the Order of the Phoenix',
                author=self.get(data_items.AuthorDataItem, 1),
                category=self.get(data_items.BookCategoryDataItem, 1))
            )

            self._add_data(data_items.BookDataItem(
                id=3, title='The Hobbit',
                author=self.get(data_items.AuthorDataItem, 2),
                category=self.get(data_items.BookCategoryDataItem, 1))
            )

        def sync_environment(self):
            """Triggers data synchronization when the remote data needs to be synced"""
            self.sim.dut_simulator.remove_all()

            for cur_author in self.get_all_for(data_items.AuthorDataItem):
                self.sim.dut_simulator._all_authors[cur_author.id] = DutSimulator.Author(
                    id=cur_author.id, first_name=cur_author.first_name, last_name=cur_author.last_name
                )

            for cur_category in self.get_all_for(data_items.BookCategoryDataItem):
                self.sim.dut_simulator._all_categories[cur_category.id] = DutSimulator.Category(
                    id=cur_category.id, name=cur_category.name
                )

            for cur_book in self.get_all_for(data_items.BookDataItem):
                self.sim.dut_simulator._all_books[cur_book.id] = DutSimulator.Book(
                    id=cur_book.id, title=cur_book.title, author__id=cur_book.author.id, category__id=cur_book.category.id
                )

You need to define two methods, the method :meth:`balderhub.data.lib.scenario_features.DataEnvironmentFeature.load_data`
which describes the full data sample and the method
:meth:`balderhub.data.lib.scenario_features.DataEnvironmentFeature.sync_environment`, that will be executed when the data
samples need to be synced. This will be done by most projects automatically. You only need to make sure that you
have an implementation of this method.

If you would like to run tests under different data samples, you can
define multiple versions of your `DataEnvironmentFeature` with different data sets and assign them to different setups:

.. code-block:: python

    class SetupBase(balder.Setup):

        class DUT(balder.Device):
            data = FictitiousDataEnvironmentFeature()
            ...

        ...

    class SetupWithLiveData(balder.Setup):
        class DUT(balder.Device):
            data = LiveDataEnvironmentFeature()
            ...

        ...

Initial Data Config Features
============================

This project provides two main features used in other BalderHub projects, like
`balderhub-crud <https://hub.balder.dev/projects/crud>`_ or
`balderhub-auth <https://hub.balder.dev/projects/auth>`_.

These features are the :class:`balderhub.data.lib.scenario_features.InitialDataConfig` and the
:class:`balderhub.data.lib.scenario_features.AccessibleInitialDataConfig`.

The `InitialDataConfig` will be assigned to the same device, that has the `DataEnvironmentFeature` and describes all
initial loaded data for a specific data item. On the other side, the `AccessibleInitialDataConfig` is a feature, that
is assigned to the remote device that is used to access the data from the DUT. It can return the same data as the
remote `InitialDataConfig` feature or return a subset of it. This is mainly used for data, that has special object
permission and can only be accessed by a specific user group.

When using the :class:`balderhub.data.lib.scenario_features.DataEnvironmentFeature`, you will not need to provide an
implementation for both of them, just use the setup factories:

.. code-block:: python

    class SetupBase(balder.Setup):

        class DUT(balder.Device):
            data = FictitiousDataEnvironmentFeature()
            initial_data = balderhub.data.lib.setup_features.factories.AutoInitialDataConfigFactory.get_for(AuthorDataItem)()
            ...

        @balder.connect(DUT, over_connection=balder.Connection)
        class User(balder.Device):
            accessible_data = balderhub.data.lib.setup_features.factories.AutoAccessibleInitialDataConfigFactory.get_for(AuthorDataItem)(Master='DUT')


`AbstractDataItemRelatedFeature` and the `@balderhub.data.register_for_data_item()` Decorator
=============================================================================================

This BalderHub project provides a base feature class
:class:`balderhub.data.lib.scenario_features.AbstractDataItemRelatedFeature`, that is used for a wide set of features
within this package but also within other depending BalderHub packages like
`balderhub-crud <https://hub.balder.dev/projects/crud>`_ or
`balderhub-auth <https://hub.balder.dev/projects/auth>`_.

By using this `AbstractDataItemRelatedFeature` as base class, the BalderHub package expects that further subclasses
(mostly defined as setup features by the end user) use the `@balderhub.data.register_for_data_item()` decorator to
specify the affiliation of the specific feature:

.. code-block:: python

    from typing import List, Dict, Union, Any

    import balder
    import balderhub.data

    from balderhub.data.lib.scenario_features import InitialDataConfig, AccessibleInitialDataConfig


    @balderhub.data.register_for_data_item(BookDataItem)
    class AccessibleBookInitialDataConfig(AccessibleInitialDataConfig):

        class Master(balder.VDevice):
            """inner virtual device referencing the master device that provides the full initial data config"""
            full_initial_config = InitialDataConfig.get_specific_feature_for(BookDataItem)

        @property
        def data_list(self) -> SingleDataItemCollection:
            return self.Master.full_initial_config.data_list.filter(MyBookFilter())


You can assign such a feature to your setup like any other feature or by using the method
:meth:`balderhub.data.lib.scenario_features.AbstractDataItemRelatedFeature.get_specific_feature_for`:


.. code-block:: python

    import balder
    import balderhub.data

    from balderhub.data.lib.scenario_features import InitialDataConfig, AccessibleInitialDataConfig

    class SetupBase(balder.Setup):

        class DUT(balder.Device):
            data = FictitiousDataEnvironmentFeature()
            initial_data = InitialDataConfig.get_for(BookDataItem)
            ...

        @balder.connect(DUT, over_connection=balder.Connection)
        class User(balder.Device):
            accessible_data = AccessibleInitialDataConfig.get_for(BookDataItem, Master="DUT")




.. _single_data_item_collection:

Working with `SingleDataItemCollection`
=======================================

`SingleDataItemCollection` is a collection of `SingleDataItem` instances with additional utility methods like
filtering, getting by attributes, sorting, and comparison.

Example:

.. code-block:: python

    from balderhub.data.lib.utils import SingleDataItemCollection

    # Assuming AuthorDataItem defined earlier

    authors = SingleDataItemCollection([
        AuthorDataItem(id=1, first_name='J.K.', last_name='Rowling'),
        AuthorDataItem(id=2, first_name='J.R.R.', last_name='Tolkien'),
    ])

    # Get by identifier
    rowling = authors.get_by(id=1)

    # Filter (requires a Filter subclass, see below)
    fantasy_authors = authors.filter(FantasyAuthorFilter())

    # Compare collections
    expected = SingleDataItemCollection([rowling])
    if expected.compare(fantasy_authors):
        print(\"Collections match\")

.. _filters:

Using Filters
=============

Define custom filters for `SingleDataItemCollection.filter()`:

.. code-block:: python

    from balderhub.data.lib.utils import Filter

    class FantasyAuthorFilter(Filter):
        def apply(self, item: AuthorDataItem) -> bool:
            return item.last_name == 'Rowling'  # example logic

    filtered = authors.filter(FantasyAuthorFilter())
