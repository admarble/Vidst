"""
Basic usage example for the Video Understanding AI system.
This example demonstrates the core functionality of the system.
"""

from video_understanding import (
    VideoProcessor,
    ProcessorConfig,
    SceneDetector,
    SceneConfig,
    ObjectDetector,
    ModelConfig,
    TextRecognizer,
    OCRConfig,
    Video
)

def main():
    # Load video
    video = Video.from_file("path/to/your/video.mp4")

    # Initialize components with configurations
    processor_config = ProcessorConfig(
        detection_enabled=True,
        ocr_enabled=True
    )
    processor = VideoProcessor(processor_config)

    scene_config = SceneConfig(
        threshold=0.3,
        min_scene_length=2.0,
        analyze_content=True
    )
    scene_detector = SceneDetector(scene_config)

    detector_config = ModelConfig(
        confidence_threshold=0.5,
        nms_threshold=0.4,
        model_type="yolov5"
    )
    object_detector = ObjectDetector(detector_config)

    ocr_config = OCRConfig(
        language="en",
        min_confidence=0.7,
        enable_layout_analysis=True
    )
    text_recognizer = TextRecognizer(ocr_config)

    # Process video
    with processor.process(video) as context:
        # Detect scenes
        scenes = scene_detector.detect_scenes(video)
        print(f"Detected {len(scenes)} scenes")

        # Process each scene
        for i, scene in enumerate(scenes):
            print(f"\nAnalyzing scene {i+1}:")
            print(f"  Duration: {scene.end_time - scene.start_time:.2f}s")

            # Analyze scene content
            analysis = scene_detector.analyze_scene(scene)
            print(f"  Summary: {analysis.content_summary}")

            # Detect objects in keyframe
            detections = object_detector.detect_objects(scene.keyframe)
            print(f"  Objects detected: {len(detections)}")
            for detection in detections:
                print(f"    - {detection.class_name}: {detection.confidence:.2f}")

            # Extract text
            text_regions = text_recognizer.extract_text(scene.keyframe)
            print(f"  Text regions found: {len(text_regions)}")
            for region in text_regions:
                if region.confidence > 0.8:
                    print(f"    - {region.text[:50]}...")

if __name__ == "__main__":
    main()
