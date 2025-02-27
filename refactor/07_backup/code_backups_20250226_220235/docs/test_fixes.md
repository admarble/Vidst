# Video Processing Guide

This is a test document with various documentation issues to fix.

## Code Blocks with Issues

Here's a directory tree with incorrect formatting:

```text
                src/
                ├── core/
                │   ├── input/
                │   ├── processing/
                │   └── output/
                └── ai/
                    └── models/
```text
```text
                Here's a code block without proper indentation:
```python
def process_video(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    return process_content(content)
```text
                ```text
                Here's a console output:
```console
$ python scripts/process.py
Processing video: test.mp4
Done!
```text
                ```text
                ## Cross References with Issues

                See the :ref:`test_fixes_md__configuration_guide`for more details.
                Check the :doc:`/api/core/config` documentation.
                Look at the :doc:`/guides/configuration`page.
                See the :doc:`/core/exceptions` for error handling.
                Check the :ref:`genindex` for all entries.

                ## Section Hierarchy Issues

                # Wrong Level 1

                ### Wrong Level 3

                ## Correct Level 2

                #### Wrong Level 4

                ## Function References

                Use :py:py:py:py:func:`process_video` to handle videos.
                The :py:py:py:py:func:`core.utils.validate` function checks input.

                ## Code Block with Tree
```tree
project/
├── src/
│   ├── core/
│   └── utils/
└── tests/
    └── unit/
```text
```text
