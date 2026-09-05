# Environment Variables

The system requires several environment variables to function correctly. **Never commit actual secrets to version control.** Use a `.env` file for local development and secure secret managers in deployment environments.

| Variable Name | Description | Example Value |
| :--- | :--- | :--- |
| `APP_ENV` | Defines the environment. Controls behavior like the synthetic demo reset. Must be `development`, `demo`, or `production`. | `demo` |
| `SECRET_KEY` | Cryptographic key used for signing JWT tokens and other security operations. | `super-secret-key-change-me` |
| `DATABASE_URL` | Connection string for the PostgreSQL database. | `postgresql://user:pass@localhost:5432/sih_db` |
| `NEO4J_URI` | Connection URI for the Neo4j graph database. | `bolt://localhost:7687` |
| `NEO4J_USER` | Username for Neo4j. | `neo4j` |
| `NEO4J_PASSWORD` | Password for Neo4j. | `neo4j_password` |
| `CORS_ORIGINS` | Comma-separated list of allowed origins for Cross-Origin Resource Sharing. | `http://localhost:3000,https://demo.example.com` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Lifespan of the JWT authentication token in minutes. | `30` |
| `BCRYPT_ROUNDS` | Number of rounds for password hashing. | `12` |
| `REPORT_EXPORT_LIMIT` | Maximum number of records that can be exported in a single report. | `1000` |
