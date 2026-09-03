# Shared Package (`packages/shared`)

## Purpose
This package serves as a central reference for shared data models, TypeScript interfaces, and Pydantic schemas shared across the frontend and backend applications in the SIH 26189 system.

## Planned Contents
- **Entity Schemas:** Shared definitions for `Person`, `Alias`, `PhoneNumber`, `Account`, `Vehicle`, `Location`, `Organization`, `Case`, and `Event`.
- **Relationship Schemas:** Shared schemas for candidate links, evidence references, and verification statuses (`PENDING`, `ACCEPTED`, `REJECTED`, `CORRECTED`).
- **API Request/Response Models:** Standardized JSON payload contracts.

## Safety & Ethics
- All shared types and schemas must enforce evidence traceability metadata (`source_text_snippet`, `confidence_score`, `verification_status`).
- Shared schemas must never store production secrets or real PII.
