# Milestone 11 Limitations

1. **Synthetic Data**: The training dataset is purely synthetic. The model will overfit to the templated structures of the mock data generator.
2. **spaCy Constraints**: We utilize the default CPU-optimized efficiency pipeline for spaCy.
3. **Hardware Acceleration**: We intentionally bypass GPU constraints to ensure cross-platform compatibility on basic development machines.
4. **Future Steps**: Integration of HuggingFace / LoRA transformer pipelines remains an option for future milestones but was intentionally omitted here to prevent bloated dependency trees and avoid massive download penalties during initialization.
