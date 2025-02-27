
Contributing Guide

==================











Overview


--------





--------





--------





--------





--------




This guide explains how to contribute to the Video Understanding AI project.

Getting Started


---------------





---------------





---------------





---------------





---------------




1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Development Setup


-----------------





-----------------





-----------------





-----------------





-----------------




1. Clone your fork:

.. code-block:: bash

      git clone https://github.com/your-username/video-understanding-poc
      cd video-understanding-poc

2. Create virtual environment:

.. code-block:: bash

      python -m venv venv

      source venv/bin/activate  or `venv\Scripts\activate` on Windows








=





=

3. Install dependencies:

.. code-block:: bash

      pip install -r requirements.txt
      pip install -r requirements-dev.txt

Code Style


----------





----------





----------





----------





----------




- Follow PEP 8 guidelines
- Use type hints
- Write docstrings in Google style
- Keep functions focused and small
- Add unit tests for new features

Testing


-------





-------





-------





-------





-------




Run tests before submitting PR:

.. code-block:: bash

      pytest
      pytest --cov=src tests/

Documentation


-------------





-------------





-------------





-------------





-------------




- Update docs for new features
- Include docstrings
- Add examples where helpful

- Build docs locally to verify:

.. code-block:: bash

      cd docs
      make html

Pull Request Process


--------------------





--------------------





--------------------





--------------------





--------------------




1. Update CHANGELOG.md
2. Add tests for new features
3. Update documentation
4. Get code review
5. Address feedback
6. Squash commits
7. Merge when approved

Questions?


----------





----------





----------





----------





----------




- Open an issue
- Join our Discord
- Email the maintainers

Indices and Tables


------------------





------------------





------------------





------------------





------------------








\* :ref:`modindex`*
