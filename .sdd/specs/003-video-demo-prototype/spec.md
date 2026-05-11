# Feature Specification: Video Demo Prototype

## User Scenarios & Testing

### User Story 1 - Review a 3-minute demo structure (Priority: P1)

The team needs a clear prototype for a hackathon demo video that explains the B2G GTM Toolkit through Andrea, an AE selling to public sector buyers.

Independent Test: Open the storyboard and confirm it covers hook, one-prompt gesture, pipeline, deliverables, and quantified close in 180 seconds.

Acceptance Scenarios:

- Given the video brief, when the storyboard is reviewed, then each block has timing, visual direction, and narration.
- Given no final recordings yet, when the prototype is opened, then the timeline still communicates the intended composition with placeholders.

### User Story 2 - Assemble media later (Priority: P2)

The team needs a Remotion project where HeyGen videos, screen recordings, and Notion captures can be inserted without redesigning the video.

Independent Test: Inspect the Remotion source and verify media placeholders are named and documented.

Acceptance Scenarios:

- Given final MP4/PNG assets, when they are copied into the media folder, then producers know which scene each asset belongs to.
- Given the timeline, when counters and captions are reviewed, then the core hackathon numbers appear in the closing story.

## Requirements

### Functional Requirements

- FR-001: The prototype MUST target a 180-second video at 1080p.
- FR-002: The prototype MUST include the five narrative blocks from the final brief.
- FR-003: The prototype MUST include Spanish narration/captions.
- FR-004: The prototype MUST include animated counters for entities, SECOP processes, opportunities, and detected pipeline value.
- FR-005: The prototype MUST provide documented slots for HeyGen, screen recordings, and Notion captures.

## Success Criteria

- SC-001: A reviewer can understand the full video without final recorded assets.
- SC-002: A producer can replace placeholders with real MP4/PNG assets in less than 30 minutes.
- SC-003: The final structure keeps the demo under 3 minutes.
