{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

   :members:
   :show-inheritance:
   :special-memberinherited-members:

   {% block methods %}
   {% if methods %}

   .. rubric:: Methods

   .. autosummary::
      :nosignatures:

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

Indices and Tables








\* :doc:`/modindex`*
