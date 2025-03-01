{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}

      :members:
      :undoc-members:
      :show-inheritance:
      :special-member

      {% block modules %}
      {% if modules %}
      Submodules

      .. autosummary::
         :toctree:
         :recursive:

      {% for item in modules %}
         {{ item }}
      {%- endfor %}
      {% endif %}
      {% endblock %}

      {% block attributes %}
      {% if attributes %}
      Module Attributes

      .. autosummary::
         :toctree:

      {% for item in attributes %}
         {{ item }}
      {%- endfor %}
      {% endif %}
      {% endblock %}

      {% block functions %}
      {% if functions %}
      Functions

      .. autosummary::
         :toctree:

      {% for item in functions %}
         {{ item }}
      {%- endfor %}
      {% endif %}
      {% endblock %}

      {% block classes %}
      {% if classes %}
      Classes

      .. autosummary::
         :toctree:
         :template: class.rst

      {% for item in classes %}
         {{ item }}
      {%- endfor %}
      {% endif %}
      {% endblock %}

      {% block exceptions %}
      {% if exceptions %}
      Exceptions

      .. autosummary::
         :toctree:

      {% for item in exceptions %}
         {{ item }}
      {%- endfor %}
      {% endif %}
      {% endblock %}

Indices and Tables








\* :doc:`/modindex`*
