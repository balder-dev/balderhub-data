# BalderHub Package ``balderhub-data``

This is a BalderHub package for the [Balder](https://docs.balder.dev) test framework. If you are new to Balder check out the
[official documentation](https://docs.balder.dev) first.

**balderhub-data** is the official BalderHub package for **structured, reusable test data** in the
[Balder test framework](https://github.com/balder-dev/balder). If you are new to Balder check out the
[official documentation](https://docs.balder.dev) first.

It makes data-driven testing clean, type-safe, and maintainable by giving you powerful building blocks to define, load,
sync, and query test data - whether you are working with a simulator, staging environment, or real device under test.


## What you will find in this package

This documentation is organised around the core pieces you will use every day:

* **Data Models**
  Define your own type-safe data items with `balderhub.data.lib.utils.SingleDataItem`.
  Built on Pydantic - supports nested objects, lists, relationships, and unique identifiers.

* **Data Environment Feature**
  Use `balderhub.data.lib.feature.DataEnvironmentFeature` inside Scenarios to load sample data and automatically
  keep the device under test in sync.

* **Initial Data Configuration**
  Control exactly what data your test setups can see with `balderhub.data.lib.feature.InitialDataConfig` and
  `balderhub.data.lib.feature.AccessibleInitialDataConfig` (perfect for permission and visibility testing).

* **Powerful Utilities**
  Collections, filters, factories, and query helpers that let you find the exact data you need with clean, readable
  syntax (e.g. ``author__last_name="Smith"``).

* **Ready-to-use Examples**
  Concrete code snippets and full scenarios that you can copy straight into your own tests.

Then head to the [Topic Intro of the Documentation](https://hub.balder.dev/projects/data/en/latest/topic_intro.html), 
to see how everything fits together - or jump straight into the 
[Examples Section of the Documentation](https://hub.balder.dev/projects/data/en/latest/examples.html), if
you prefer to learn by code.

## Installation

You can install the latest release with pip:

```
python -m pip install balderhub-data
```

# Check out the documentation

If you need more information, 
[checkout the ``balderhub-data`` documentation](https://hub.balder.dev/projects/data).


# License

This BalderHub package is free and Open-Source

Copyright (c)  2025  balderhub-data

Distributed under the terms of the MIT license
