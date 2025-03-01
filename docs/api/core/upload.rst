
Video Upload API

================











Overview


--------





--------





--------





--------





--------




The Video Upload API provides functionality for uploading and validating video files in the Video Understanding AI system.

Components


----------





----------





----------





----------





----------








VideoUploader


-------------
























The main class responsible for handling video file uploads:

- Validates video format and size
- Handles chunked uploads for large files
- Manages upload sessions
- Provides progress tracking

Configuration


-------------





-------------





-------------





-------------





-------------







Upload Settings

























.. code-block:: python

      UPLOAD_CONFIG = {
         'max_file_size': '2GB',
         'allowed_formats': ['mp4', 'avi', 'mov'],
         'chunk_size': '8MB',
         'concurrent_uploads': 3
      }




Performance Settings

























.. code-block:: python

      PERFORMANCE_CONFIG = {

         'upload_timeout': 3600,  1 hour








"





"


         'retry_delay': 5  seconds








"





"


API Reference


-------------





-------------





-------------





-------------





-------------







Classes

























.. py:class:: VideoUploader

   Main class for handling video uploads.

   .. py:method:: upload_video(file_path: str) -> str

      Upload a video file and return its unique identifier.

   .. py:method:: validate_video(file_path: str) -> bool

      Validate a video file before upload.

   .. py:method:: get_upload_progress(upload_id: str) -> float

      Get the progress of an ongoing upload.




Exceptions

























.. py:exception:: VideoUploadError

   Base exception for upload-related errors.

.. py:exception:: VideoFormatError

   Raised when an unsupported video format is detected.

.. py:exception:: VideoSizeError

   Raised when a video exceeds the maximum allowed size.

Example Usage


-------------





-------------





-------------





-------------





-------------







Basic Upload

























.. code-block:: python

      from video_understanding import VideoUploader

      uploader = VideoUploader()
      video_id = uploader.upload_video("path/to/video.mp4")




Progress Tracking

























.. code-block:: python

      uploader = VideoUploader()
      video_id = uploader.upload_video("path/to/video.mp4")

      progress = uploader.get_upload_progress(video_id)
      print(f"Upload progress: {progress}%")
