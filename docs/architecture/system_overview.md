# System Overview

This document provides a high-level overview of the Vidst system architecture for the POC.

## Core Components

Vidst is built with a modular architecture that allows for flexible integration of different video analysis capabilities:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Video Input    │────▶│  Processing     │────▶│  Storage        │
│                 │     │  Pipeline       │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │                 │
                        │  Analysis       │
                        │  Components     │
                        │                 │
                        └─────────────────┘
                               │
                               ▼
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  Query Engine   │◀───▶│  Results        │
│                 │     │  Interface      │
└─────────────────┘     └─────────────────┘
```

## Component Descriptions

### Video Input

Handles video file uploads and validation. Supports common video formats (MP4, MOV, AVI).

### Processing Pipeline

Coordinates the flow of video data through various analysis components. Manages job queues and processing status.

### Analysis Components

Individual modules that perform specific analysis tasks:

- **Scene Detection**: Identifies scene changes (implemented)
- **Audio Transcription**: Converts speech to text (in progress)
- **Vector Storage**: Stores and retrieves vector embeddings (in progress)

### Storage

Manages persistent storage of video files, analysis results, and metadata.

### Query Engine

Provides an interface for querying video content based on analysis results.

### Results Interface

Presents analysis results to users through API endpoints.

## Technology Stack

- **Backend**: Python with FastAPI
- **Storage**: PostgreSQL + Vector extensions
- **External APIs**: Twelve Labs, Whisper
- **Deployment**: Docker containers

## Current Limitations

For the POC, the following limitations apply:

- Maximum video size: 500MB
- Maximum video duration: 30 minutes
- Supported formats: MP4, MOV
- Processing time: ~2-5 minutes per video (depending on length)
