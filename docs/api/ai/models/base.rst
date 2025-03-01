
Base AI Models




















.. py:module:: src.ai.models.base






















Base Model





















.. py:class:: BaseModel

   Base class for all AI models in the system.

   .. py:method:: process(input_data: Any) -> Any

      :abstractmethod:

      Process input data using the model.

      :param input_data: Input data to process
      :returns: Processed result
      :raises ProcessingError: If processing fails




   .. py:method:: retry_with_backoff(func: Callable, *arg*s*,*__ESCAPED_42*_*_* **kwargs) -> **A***n***y******

      Retry a function call with exponential backoff.

      :param func: Function to retry
      :param args: Positional arguments
      :param kwargs: Keyword arguments
      :returns: Function result
      :raises ModelError: If all retries fail

























Exceptions





















.. py:exception:: ModelError

   :module: src.core.exceptions

   Base exception for model-related errors.

.. py:exception:: ProcessingError

   :module: src.core.exceptions

   Exception raised when processing fails.

.. py:exception:: ResourceError

   :module: src.core.exceptions

   Exception raised when resource limits are exceeded.






















See Also





















- :class:`src.ai.models.twelve_labs.model.TwelveLabsMod`_e`_l`_
- :class:`src.ai.models.openai.model.OpenAIMod`_e`_l`_

API Reference


-------------





-------------





-------------





-------------





-------------




.. automodule:: src.ai.models.base

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Indices and tables


------------------





------------------





------------------





------------------





------------------










\* :ref:`modindex`*
