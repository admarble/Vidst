
OpenAI Model




















.. py:module:: src.ai.models.openai.model






















Overview





















The OpenAI model module provides integration with OpenAI's GPT-4V model for video content analysis.






















Classes










































OpenAIModel
























.. py:class:: OpenAIModel

   Integration with OpenAI's GPT-4V model.

   .. py:method:: process(input_data: Dict[str, Any]) -> Dict[str, Any]

      Process input data using GPT-4V.

      :param input_data: Input data containing video frames and metadata
      :returns: Model predictions and analysis
      :raises ModelError: If processing fails




   .. py:method:: retry_with_backoff(func: Callable, *arg*s*,*__ESCAPED_42*_*_* **kwargs) -> **A***n***y******

      Retry a function call with exponential backoff.

      :param func: Function to retry
      :param args: Positional arguments
      :param kwargs: Keyword arguments
      :returns: Function result
      :raises ModelError: If all retries fail




See Also































- :class:`src.ai.models.base.BaseMod`_e`_l`_
- :class:`src.ai.models.twelve_labs.model.TwelveLabsMod`_e`_l`_
