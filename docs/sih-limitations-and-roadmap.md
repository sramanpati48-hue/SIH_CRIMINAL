# Limitations and Roadmap

## Current Limitations

1. **Synthetic Data Only:** 
   - **Limitation:** The system has been developed, tested, and demonstrated exclusively using synthetic data. It has not been exposed to real-world complexities, slang, or inconsistencies present in actual law enforcement or financial records.
   - **Impact:** The NLP models may require significant retraining or fine-tuning to perform accurately on real data.

2. **No Automated Browser Testing:**
   - **Limitation:** Comprehensive end-to-end automated browser testing (e.g., Cypress, Playwright) is currently deferred. Testing relies on unit tests and manual verification checklists.

3. **Scale and Performance Limits:**
   - **Limitation:** While architected for scalability, the current demonstration deployment is not load-tested for millions of nodes and edges. Graph traversal performance at extreme scale remains unverified in this environment.

4. **Limited NLP Scope:**
   - **Limitation:** Entity extraction is currently optimized for a specific set of predefined entities (e.g., Person, Organization, Location, Phone, Account) and may miss nuanced or novel relationship types.

## Future Roadmap

### Phase 1: Hardening and Real-World Readiness
- **Data Pipeline Secure Ingestion:** Develop secure APIs for ingesting actual structured and unstructured reports under strict legal and compliance frameworks.
- **Domain-Specific Model Fine-Tuning:** Retrain NLP/extraction models on anonymized, domain-specific text corpora to improve accuracy on real-world jargon and report structures.
- **Comprehensive E2E Testing:** Implement automated browser testing and rigorous load testing.

### Phase 2: Advanced Analytics & Collaboration
- **Temporal Graph Analysis:** Enhance Neo4j queries to better visualize and analyze how networks evolve over time (e.g., communication patterns leading up to an event).
- **Inter-Agency Collaboration:** Develop secure, federated sharing protocols allowing different agencies to query overlapping graph segments without exposing underlying sensitive case files.

### Phase 3: Production Deployment
- **High Availability:** Deploy PostgreSQL and Neo4j in clustered, high-availability configurations.
- **Advanced RBAC & Audit:** Implement granular, attribute-based access control (ABAC) and immutable audit logging for every read/write action within the system.
