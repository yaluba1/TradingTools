# Configuration file for the Sphinx documentation builder.
import os
import sys
sys.path.insert(0, os.path.abspath('../../tools'))

project = 'IBKR Trading Tools'
copyright = '2026, Yaluba'
author = 'Juan Noguera'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_default_options = {
    'exclude-members': '__pydantic_extra__, __pydantic_fields__, __pydantic_computed_fields__, __pydantic_private__, __pydantic_core_schema__, __pydantic_custom_init__, __pydantic_decorators__, __pydantic_parent_namespace__, __pydantic_post_init__, __pydantic_serializer__, __pydantic_validator__',
}

autodoc_use_legacy_class_based = True
