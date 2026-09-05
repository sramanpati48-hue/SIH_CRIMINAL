# SIH Jury FAQ

**1. Why graph databases?**
Graph databases are optimized for querying and traversing complex relationships. In network analysis, understanding the connections between entities (e.g., people, locations, events) is more important than the entities themselves, which relational databases struggle to query efficiently at scale.

**2. Why Neo4j + PostgreSQL?**
PostgreSQL provides robust, ACID-compliant storage for structured relational data like users, roles, case metadata, and raw documents. Neo4j acts as the specialized engine for the highly connected knowledge graph, enabling rapid pattern matching and graph algorithms. This polyglot persistence model uses each database for its strengths.

**3. Why not just an LLM?**
LLMs hallucinate and lack explicit reasoning. They cannot be trusted to independently build and query a factual database. By extracting entities and storing them in a graph, we enforce strict schemas and traceability. The LLM acts as an extraction tool, while the graph serves as the source of truth, ensuring explainability.

**4. How are false positives addressed?**
Through a mandatory **Human-in-the-Loop** workflow. AI-generated links and entities are placed in a "pending" state. They only become official investigative leads when a human user reviews, accepts, or corrects them based on the provided source evidence and confidence scores.

**5. How do you protect privacy?**
The system is built to use **strictly synthetic data**. Real personally identifiable information (PII) is never used during development or demonstration. In a production environment, strict role-based access controls (RBAC) and data siloing would govern access.

**6. How does RBAC work?**
Role-Based Access Control ensures that users (e.g., Investigators, Analysts, Admins) only have access to the features and cases relevant to their duties. Permissions are enforced at the API route level using dependency injection in FastAPI.

**7. How are reports secured?**
Reports are generated dynamically based on the user's access level. They do not contain secrets. The application uses parameterized queries and secure API endpoints to prevent unauthorized access.

**8. How do models remain explainable?**
Every extracted relationship and alert includes **traceability**. The system records the source document, the exact text snippet, a timestamp, a confidence score, and the verification status (approved/rejected by a human). It does not output opaque "guilt scores."

**9. What happens when Neo4j or spaCy is unavailable?**
The system is designed for safe failure. If Neo4j is down, the FastAPI backend will gracefully handle the error and inform the frontend, preventing the application from crashing. Relational data (PostgreSQL) may still be accessible.

**10. How would the system scale?**
The backend uses FastAPI (asynchronous Python), which scales horizontally. Neo4j and PostgreSQL can be deployed in clustered configurations. The separation of frontend (Next.js) and backend (FastAPI) allows independent scaling of resources.

**11. Why synthetic data?**
To strictly adhere to ethical guidelines and project rules. Using synthetic data ensures zero risk of privacy violations, real-world biases, or misuse of sensitive police/banking records during the development and demonstration phases.

**12. What is the future production path?**
Moving to production would involve rigorous security audits, integration with official authentication providers, replacing synthetic data pipelines with secure ingestors for actual structured/unstructured reports, and fine-tuning extraction models on domain-specific corpora under strict legal oversight.
