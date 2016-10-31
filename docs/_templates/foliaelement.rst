{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :show-inheritance:
   :undoc-members:
   :special-members:

   {% block methods %}

   {% if methods %}
   .. rubric:: Method Summary

   .. autosummary::
   {% for item in methods %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
    {% for private_method in ['__iter__', '__len__', '__str__'] %}
    {% if private_method in members %}
    ~{{ name }}.{{ private_method }}
    {% endif %}
    {% endfor %}
   {% endif %}
   {% endblock %}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: Class Attributes

   {% for item in attributes %}
   .. autoattribute:: {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   .. rubric:: Method Details

   .. automethod::  __init__
   {% for m in methods %}
   .. automethod:: {{ m }}
   {% endfor %}
   {% for private_method in ['__iter__', '__len__', '__str__'] %}
   {% if private_method in members %}
   .. automethod:: {{ private_method }}
   {% endif %}
   {% endfor %}
