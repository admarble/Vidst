
Output Processing

=================











Overview


--------





--------





--------





--------





--------




The output processing module handles formatting and delivery of video processing results.

Components


----------





----------





----------





----------





----------








Classes


-------



























Base Classes

























Core output processing classes:




* ``_ResultValidato```_``_```_r`_`_ - Validates output da*t*a*`*_*`*_*








ProcessingResult

























Represents the result of video processing:

.. code-block:: python

      result = ProcessingResult(
         video_id="123",
         scenes=[...],
         transcription="...",
         metadata={...}
      )

Functions


---------





---------





---------





---------





---------




format_output




























Formats processing results for output:

.. code-block:: python

      formatted = format_output(result, format="json")

validate_output




























Validates output before delivery:

.. code-block:: python

      is_valid = validate_output(result)

write_output




























Writes output to storage:

.. code-block:: python

      write_output(result, path="output/video_123.json")

Usage Examples


--------------





--------------





--------------





--------------





--------------







Basic Output

























.. code-block:: python

      result = process_video("video.mp4")
      output = format_output(result)
      write_output(output, "results.json")




Custom Formatting

























.. code-block:: python

      formatter = OutputFormatter(
         include_metadata=True,
         pretty_print=True
      )
      output = formatter.format(result)




Error Handling

























.. code-block:: python

      try:
         write_output(result)
      except OutputError as e:
         handle_output_error(e)

Best Practices


--------------





--------------





--------------





--------------





--------------







\* Use appropriate formats*





\* Document output schema*

Indices and Tables


------------------





------------------





------------------





------------------





------------------







\* :ref:`modindex`*
