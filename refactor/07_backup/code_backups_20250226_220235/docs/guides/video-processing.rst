
Video Processing Guide

======================











This guide covers the video processing capabilities of Vidst, including scene detection, audio transcription, and text extraction.

Getting Started


---------------





---------------





---------------





---------------





---------------




Basic Video Processing


----------------------





----------------------





----------------------





----------------------





----------------------




.. code-block:: python

      from src.ai.pipeline import VideoPipeline
      from src.core.config import VideoConfig

      Initialize pipeline with default settings








=





=

      pipeline = VideoPipeline(config)

      Process a video file








=





=


      Access results








=





=

      print(f"Number of scenes: {len(result['scenes'])}")
      print(f"Duration: {result['metadata']['duration']} seconds")

Processing Features


-------------------





-------------------





-------------------





-------------------





-------------------








Scene Detection


---------------

































The system automatically detects scene changes in videos:

.. code-block:: python

      Process video with scene detection








^





"

         "video_path": "lecture.mp4",
         "task": "scene_detection",

         "min_scene_length": 2.0  minimum scene length in seconds








"





"


      Access scene information








"





"

         print(f"Scene from {scene['start_time']} to {scene['end_time']}")
         print(f"Description: {scene['description']}")

Audio Transcription


-------------------





-------------------





-------------------





-------------------





-------------------








-------------------










Extract and transcribe audio with speaker identification:

.. code-block:: python

      Process with audio transcription








"





"

         "video_path": "interview.mp4",
         "task": "transcription",
         "enable_speaker_diarization": True
      })

      Access transcription








"





"

         print(f"[{segment['speaker']}] {segment['text']}")
         print(f"Time: {segment['start']} - {segment['end']}")

Text Extraction


---------------





---------------





---------------





---------------





---------------








---------------










Extract text from video frames (e.g., slides, subtitles):

.. code-block:: python

      Process with text extraction








"





"

         "video_path": "presentation.mp4",
         "task": "text_extraction",

         "ocr_language": "en"  language code








"





"


      Access extracted text








"





"

         print(f"Frame {text_segment['frame_number']}")
         print(f"Text: {text_segment['text']}")

Advanced Features


-----------------





-----------------





-----------------





-----------------





-----------------







Custom Processing Pipeline


































Combine multiple processing tasks:

.. code-block:: python

      from src.ai.models import SceneDetector, TextExtractor, AudioTranscriber

      Create pipeline with specific models








"





"

      pipeline.add_model(SceneDetector())
      pipeline.add_model(TextExtractor())
      pipeline.add_model(AudioTranscriber())

      Process with all models








"





"

         "video_path": "video.mp4",
         "task": "full_analysis"
      })

Progress Monitoring


-------------------





-------------------





-------------------





-------------------





-------------------








-------------------










Monitor processing progress:

.. code-block:: python

      def progress_callback(status: dict):
         print(f"Progress: {status['progress']}%")
         print(f"Current task: {status['current_task']}")
         print(f"Time elapsed: {status['elapsed_time']}s")

      Process with progress monitoring








"





"

         "video_path": "video.mp4",
         "progress_callback": progress_callback
      })

Resource Management


-------------------





-------------------





-------------------





-------------------





-------------------








-------------------










Control resource usage:

.. code-block:: python

      Configure resource limits








"





"

         max_concurrent_jobs=2,
         memory_limit_per_job="4GB",
         enable_gpu=True
      )

      pipeline = VideoPipeline(config)

Best Practices


--------------





--------------





--------------





--------------





--------------







Video Preparation


































1. **Format Support**:

   - Use MP4, AVI, or MOV formats
   - Ensure video codec compatibility (H.264 recommended)
   - Keep file size under 2GB

2. **Quality Settings**:

   - Recommended resolution: 720p or 1080p
   - Frame rate: 24-30 fps
   - Bit rate: 2-8 Mbps

3. **Audio Quality**:

   - Sample rate: 44.1 kHz or 48 kHz
   - Channels: Stereo
   - Clear audio for better transcription

Processing Tips





















1. **Performance Optimization**:

   - Process in batches for multiple videos
   - Use appropriate task-specific settings
   - Enable GPU acceleration when available

2. **Error Handling**:

   - Implement proper error handling
   - Use retry mechanisms for transient failures
   - Validate input files before processing

3. **Resource Management**:

   - Monitor memory usage
   - Limit concurrent processing
   - Clean up temporary files

Common Issues




Processing Failures




If processing fails:

1. Check file format and codec support
2. Verify file permissions
3. Monitor system resources
4. Check API key validity
5. Review error logs

Performance Issues




If processing is slow:

1. Reduce video resolution/quality
2. Check system resource usage
3. Enable GPU acceleration
4. Adjust concurrent job limits
5. Consider batch processing

Quality Issues




If results are poor:

1. Improve input video quality
2. Adjust task-specific parameters
3. Check audio clarity
4. Verify language settings
5. Update model versions

Additional Resources




For more information, see:

- :doc:`/api/core/video` - Video processing API documentation
- :doc:`/api/core/pipeline` - Pipeline API documentation
- :doc:`/api/core/config` - Configuration API reference
- :doc:`error-handling` - Error handling guide

Indices and Tables









\* :doc:`/modindex`*
