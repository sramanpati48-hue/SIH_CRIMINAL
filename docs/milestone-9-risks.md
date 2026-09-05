# Milestone 9 Risks & Mitigations

Introducing a local ML model (even open-weight) into a deterministic pipeline carries architectural and operational risks.

## 1. Dependency Bloat & Environment Breakage
**Risk:** Installing `torch` and `transformers` will add >2GB to the local virtual environment. This can break local development for developers with limited bandwidth or disk space, or cause deployment container bloat.
**Mitigation:** NER tools will be isolated in an `[optional]` dependency group. The core backend container will not install them by default. The `HuggingFaceExtractor` will elegantly fail-over or throw clear warnings if dependencies are missing, rather than crashing the API.

## 2. Model OOM (Out of Memory)
**Risk:** Running transformer models locally on laptops without dedicated GPUs can lead to high RAM usage or OOM kills.
**Mitigation:** We will restrict the default model to lightweight, quantized, or base models (e.g., `dslim/bert-base-NER` instead of large variants). Model inference will be run strictly on the CPU by default (`device=-1` in Hugging Face pipelines) for maximum local compatibility.

## 3. Downstream Graph Pollution (False Positives)
**Risk:** The NER model incorrectly identifies random text as a `PERSON` or hallucinated entity. If these sync to Neo4j, they corrupt graph analytics and similarity matching.
**Mitigation:** **Human-in-the-Loop strict enforcement**. The extraction pipeline inherently tags all ML outputs as `UNREVIEWED`. Graph synchronization explicitly filters out `UNREVIEWED` and `REJECTED` nodes. The model cannot bypass the human analyst.

## 4. Pipeline Latency
**Risk:** NLP inference on CPU takes hundreds of milliseconds per document, significantly slowing down the `process_document` ingestion workflow.
**Mitigation:** In future milestones, document processing will be offloaded to asynchronous background tasks (`ProcessingJob` model already exists) rather than blocking the HTTP response thread. For Milestone 9, we will evaluate batch sizes.
