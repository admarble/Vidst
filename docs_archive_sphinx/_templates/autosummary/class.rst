{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:
   :no-index:

   {% block methods %}
   {% if methods %}

   .. rubric:: Methods

   .. autosummary::

   {% for item in methods %}

      ~{{ name }}.{{ item }}

   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block attributes %}
   {% if attributes %}

   .. rubric:: Attributes

   .. autosummary::

   {% for item in attributes %}

      ~{{ name }}.{{ item }}

   {%- endfor %}
   {% endif %}
   {% endblock %}
