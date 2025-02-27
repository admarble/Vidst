{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}

   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:
   :no-index:

   {% block attributes %}
   {% if attributes %}

   .. rubric:: Module Attributes

   .. autosummary::

   {% for item in attributes %}

      {{ item }}

   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block functions %}
   {% if functions %}

   .. rubric:: Functions

   .. autosummary::

   {% for item in functions %}

      {{ item }}

   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}

   .. rubric:: Classes

   .. autosummary::

   {% for item in classes %}

      {{ item }}

   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if exceptions %}

   .. rubric:: Exceptions

   .. autosummary::

   {% for item in exceptions %}

      {{ item }}

   {%- endfor %}
   {% endif %}
   {% endblock %}
