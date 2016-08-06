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
    ~{{ name }}.__iter__
    ~{{ name }}.__len__
    ~{{ name }}.__str__
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

   {% for m in methods %}
   .. automethod:: {{ m }}
   {% endfor %}
   .. automethod::  __iter__
   .. automethod::  __len__
   .. automethod::  __str__



