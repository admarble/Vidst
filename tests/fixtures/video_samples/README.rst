Video Test Fixtures






This directory contains video samples for testing the video processing pipeline.

Directory Structure


-----------------




.. code-block:: text

    video_samples/
    ├── valid/              # Valid video files for testing
    │   ├── short/         # Short videos (<10s)
    │   ├── medium/        # Medium length videos (10s-2min)
    │   └── long/          # Long videos (>2min)
    ├── invalid/           # Invalid/corrupted video files
    │   ├── corrupt/       # Corrupted video files
    │   ├── oversized/     # Files exceeding 2GB limit
    │   └── wrong_format/  # Files with incorrect formats
    └── scene_detection/   # Videos for scene detection testing
        ├── known_scenes/  # Videos with known scene transitions
        ├── rapid_scenes/  # Videos with many quick scenes
        └── gradual/       # Videos with gradual transitions

Valid Video Files


---------------




Short Videos





\* ``basic.mp4`` - Basic 5s video with single scene*
\* ``multiple_scenes.mp4`` - 8s video with 3 distinct scenes*
\* ``no_audio.mp4`` - 5s video without audio track*

Medium Videos





\* ``presentation.mp4`` - 1min tutorial video with slides*
\* ``interview.mp4`` - 90s interview with multiple speakers*
\* ``coding.mp4`` - 45s screen recording of coding*

Long Videos





\* ``lecture.mp4`` - 5min educational video*
\* ``documentary.mp4`` - 3min nature documentary*
\* ``compilation.mp4`` - 4min video with various scenes*

Invalid Video Files


----------------




Corrupt Files





\* ``header_corrupt.mp4`` - File with corrupted header*
\* ``partial_data.mp4`` - Incomplete video data*
\* ``broken_index.mp4`` - Corrupted index table*

Oversized Files





\* ``large_2gb.mp4`` - Exactly 2GB file*
\* ``over_2gb.mp4`` - File exceeding 2GB limit*

Wrong Format Files





\* ``fake.mp4`` - Text file with .mp4 extension*
\* ``renamed.jpg`` - Image file renamed to .mp4*
\* ``empty.mp4`` - Empty file with .mp4 extension*

Scene Detection Test Files


-----------------------




Known Scenes





\* ``exact_scenes.mp4`` - Video with precisely timed scene changes*
\* ``mixed_transitions.mp4`` - Video with various transition types*
\* ``benchmark.mp4`` - Reference video for accuracy testing*

Rapid Scenes





\* ``quick_cuts.mp4`` - Video with rapid scene changes*
\* ``music_video.mp4`` - Fast-paced content*
\* ``action.mp4`` - Action sequence with quick cuts*

Gradual Transitions





\* ``fade_transitions.mp4`` - Video with fade effects*
\* ``dissolve.mp4`` - Video with dissolve transitions*
\* ``mixed_gradual.mp4`` - Various gradual transitions*

Usage


----




1. Use these fixtures in unit tests:

   .. code-block:: python

       def test_scene_detection(video_file):
           video_path = "tests/fixtures/video_samples/scene_detection/known_scenes/exact_scenes.mp4"
           # Test implementation

2. Use in integration tests:

   .. code-block:: python

       def test_end_to_end_processing():
           video_path = "tests/fixtures/video_samples/valid/medium/presentation.mp4"
           # Test implementation

3. Use in performance tests:

   .. code-block:: python

       def test_processing_speed():
           video_path = "tests/fixtures/video_samples/valid/long/lecture.mp4"
           # Test implementation

Contributing


----------




When adding new test fixtures:

1. Follow the naming convention
2. Update this README
3. Include file metadata
4. Document known timestamps
5. Maintain file size limits
