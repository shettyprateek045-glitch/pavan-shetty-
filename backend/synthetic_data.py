"""
TALENTRANK AI — Synthetic High-Fidelity Data Store
Realistic candidate resumes, job descriptions, and audit cohorts.
All candidate profiles are realistic synthetic representations for testing and evaluation.
"""

from typing import List, Dict, Any

JOBS_DATABASE: List[Dict[str, Any]] = [
    {
        "id": "job-lead-backend",
        "title": "Staff Backend Distributed Systems Engineer",
        "company": "TalentRank Core Platform",
        "department": "Infrastructure & Data Services",
        "location": "San Francisco, CA / Remote",
        "experience_required": 6,
        "salary_range": "$190,000 - $240,000",
        "type": "Full-time",
        "status": "Active",
        "required_skills": [
            "Go",
            "Python",
            "Distributed Systems",
            "PostgreSQL",
            "Kafka",
            "gRPC",
            "Kubernetes",
            "Redis"
        ],
        "nice_to_have_skills": [
            "Rust",
            "ClickHouse",
            "eBPF",
            "OpenTelemetry"
        ],
        "description": """About the Role:
We are seeking a Staff Backend Distributed Systems Engineer to lead the architecture and resilience of our real-time candidate processing engine. You will own high-throughput ingestion pipelines, distributed event streams, and low-latency query APIs.

Responsibilities:
- Architect, build, and operate fault-tolerant distributed microservices handling 10k+ requests/sec.
- Design low-latency message streaming pipelines using Kafka, RabbitMQ, and PostgreSQL partition indexing.
- Optimize caching topologies, connection pooling, and database query planners for high-concurrency read/write operations.
- Mentor senior engineers, author architecture RFCs, and lead operational excellence post-mortems.

Requirements:
- 6+ years of production experience designing and maintaining distributed systems at scale.
- Deep expertise in Go or modern Python (FastAPI/AsyncIO) with solid concurrency patterns.
- Strong knowledge of relational database internals (PostgreSQL schema design, indexing, MVCC).
- Production experience with event-driven architectures (Apache Kafka, message brokers).
- Familiarity with containerization and orchestration (Docker, Kubernetes, Helm).
- Excellent track record of performance profiling (pprof, tracing, p99 latency mitigation)."""
    },
    {
        "id": "job-sr-ml-engineer",
        "title": "Senior AI/ML Semantic Search Engineer",
        "company": "TalentRank Core Platform",
        "department": "Applied Machine Learning",
        "location": "New York, NY / Hybrid",
        "experience_required": 4,
        "salary_range": "$180,000 - $225,000",
        "type": "Full-time",
        "status": "Active",
        "required_skills": [
            "Python",
            "PyTorch",
            "Vector Databases",
            "Sentence Transformers",
            "NLP",
            "FastAPI",
            "Scikit-learn",
            "Docker"
        ],
        "nice_to_have_skills": [
            "Qdrant",
            "ONNX Runtime",
            "Triton Inference Server",
            "LangChain"
        ],
        "description": """About the Role:
We are looking for a Senior Machine Learning Engineer specializing in Natural Language Processing and Semantic Retrieval to build state-of-the-art embedding pipelines for resume-job matching and explainability.

Responsibilities:
- Build and evaluate dense embedding models, bi-encoders, and cross-encoders for candidate-job semantic alignment.
- Integrate vector search indexing (Milvus, Qdrant, Pinecone) with hybrid lexical BM25 retrieval.
- Implement model explainability modules (SHAP, attention attribution, requirement decomposition).
- Ensure zero-bias enforcement and implement continuous fairness evaluation pipelines.

Requirements:
- 4+ years of industry experience developing and deploying production NLP / ML systems.
- Strong proficiency in Python, PyTorch/TensorFlow, and Scikit-learn.
- Hands-on experience with transformer architectures (BERT, RoBERTa, Sentence-BERT).
- Production experience deploying REST/gRPC ML microservices via Docker and FastAPI."""
    },
    {
        "id": "job-principal-frontend",
        "title": "Principal Frontend UI/UX Architect",
        "company": "TalentRank Core Platform",
        "department": "Product Engineering",
        "location": "Remote (US/EU)",
        "experience_required": 7,
        "salary_range": "$200,000 - $250,000",
        "type": "Full-time",
        "status": "Active",
        "required_skills": [
            "React",
            "TypeScript",
            "Tailwind CSS",
            "Design Systems",
            "Performance Optimization",
            "State Management",
            "Accessibility (a11y)",
            "Next.js"
        ],
        "nice_to_have_skills": [
            "WebSockets",
            "Web Workers",
            "Framer Motion",
            "Playwright"
        ],
        "description": """About the Role:
We are hiring a Principal Frontend Architect to drive the frontend architecture, design system, and user experience for our recruitment intelligence platform.

Responsibilities:
- Own the modular frontend component design system built with React, TypeScript, and modern styling.
- Ensure sub-100ms interaction latency for data-heavy tables, complex filtering, and interactive charts.
- Champion accessibility (WCAG 2.1 AA compliance), keyboard navigation, and responsive typography.
- Partner with product design to craft interfaces that rival Linear and Stripe in feel and polish."""
    }
]

CANDIDATES_DATABASE: List[Dict[str, Any]] = [
    {
        "id": "cand-01",
        "name": "Elena Rostova",
        "email": "elena.rostova@devmail.io",
        "title": "Senior Distributed Systems Engineer",
        "location": "Seattle, WA",
        "experience_years": 8.0,
        "current_company": "CloudStream Systems",
        "education": "M.S. Computer Science, University of Washington",
        "skills": ["Go", "Distributed Systems", "Kafka", "PostgreSQL", "gRPC", "Kubernetes", "Redis", "Docker", "Prometheus"],
        "status": "Shortlisted",
        "applied_date": "2026-11-12",
        "gender_proxy": "Female",
        "edu_tier": "Tier-1 University",
        "resume_text": """ELENA ROSTOVA
Seattle, WA | elena.rostova@devmail.io | github.com/erostova

PROFESSIONAL SUMMARY
Senior Distributed Systems Engineer with 8 years of experience building resilient microservice platforms in Go and C++. Proven track record of architecting event-driven pipelines processing over 45,000 events/second with sub-15ms p99 latency. Core contributor to internal gRPC routing mesh and distributed caching tiers.

EXPERIENCE
CloudStream Systems — Staff Infrastructure Engineer (2022 - Present)
- Architected a distributed transaction ledger in Go and PostgreSQL handling 2.4 billion daily records with 99.995% uptime.
- Deployed Apache Kafka clusters configured with SASL/SCRAM and custom partitioning, cutting message lag by 74%.
- Engineered gRPC connection pooling and circuit-breaking protocols across 40+ Kubernetes microservices.
- Introduced Redis Cluster distributed lock management and local LRU tiered caching, saving $380k in annual cloud spend.

FinVenture Corp — Senior Backend Engineer (2018 - 2022)
- Designed real-time event streaming pipeline processing stock market feeds using Go, Kafka, and TimescaleDB.
- Optimized PostgreSQL indexing and query execution plans, reducing analytical report execution times from 3.8s to 180ms.
- Mentored junior engineers, established code review rigor, and maintained 92% automated test coverage.

EDUCATION
- M.S. in Computer Science, University of Washington (2018)
- B.S. in Computer Engineering, University of Minnesota (2016)

SKILLS
Go (expert), C++, PostgreSQL, Kafka, Redis, gRPC, Kubernetes, Docker, Linux Internals, OpenTelemetry, Distributed Consensus (Raft)."""
    },
    {
        "id": "cand-02",
        "name": "Marcus Vance",
        "email": "marcus.vance@techvault.org",
        "title": "Staff Backend Engineer",
        "location": "Austin, TX",
        "experience_years": 9.5,
        "current_company": "Apex Data Labs",
        "education": "B.S. Software Engineering, UT Austin",
        "skills": ["Go", "Python", "Distributed Systems", "PostgreSQL", "Kafka", "Redis", "Kubernetes", "gRPC", "AWS"],
        "status": "Shortlisted",
        "applied_date": "2026-11-14",
        "gender_proxy": "Male",
        "edu_tier": "Tier-1 University",
        "resume_text": """MARCUS VANCE
Austin, TX | marcus.vance@techvault.org

SUMMARY
Staff Backend Engineer with over 9 years of hands-on experience designing cloud-native distributed backends. Extensive production experience with Go, Python, Kafka, and PostgreSQL. Passionate about system observability, high concurrency, and clean API design.

EXPERIENCE
Apex Data Labs — Staff Backend Architect (2021 - Present)
- Spearheaded the complete re-architecture of a monolithic ingest service into a high-concurrency Go microservices cluster on EKS.
- Built an event-driven synchronization service utilizing Apache Kafka and Redis streams handling 18k requests per second.
- Tuned PostgreSQL connection pools and write-ahead logging (WAL), decreasing write lock contention by 60%.
- Led cross-functional incident retrospectives and established SLOs/SLIs across 6 platform teams.

Kinetix Solutions — Senior Backend Developer (2017 - 2021)
- Developed REST and gRPC microservices in Python (FastAPI, Celery) and Go for financial reconciliation.
- Automated CI/CD deployments using Helm charts, Terraform, and GitHub Actions across multi-region Kubernetes clusters.

EDUCATION
- B.S. in Software Engineering, University of Texas at Austin (2015)

SKILLS
Languages: Go, Python, SQL, Bash
Infrastructure: Kubernetes, Docker, AWS, Kafka, Redis, PostgreSQL, gRPC, Terraform."""
    },
    {
        "id": "cand-03",
        "name": "Tariq Al-Mansoor",
        "email": "tariq.mansoor@codeworks.dev",
        "title": "Senior Cloud Infrastructure & Backend Engineer",
        "location": "Chicago, IL",
        "experience_years": 6.5,
        "current_company": "Nexus Distributed",
        "education": "B.S. Computer Science, University of Illinois Urbana-Champaign",
        "skills": ["Go", "Python", "Kubernetes", "PostgreSQL", "Kafka", "Docker", "Redis", "Distributed Systems"],
        "status": "Review",
        "applied_date": "2026-11-13",
        "gender_proxy": "Male",
        "edu_tier": "Tier-1 University",
        "resume_text": """TARIQ AL-MANSOOR
Chicago, IL | tariq.mansoor@codeworks.dev

PROFESSIONAL EXPERIENCE
Nexus Distributed — Senior Systems Engineer (2022 - Present)
- Engineered scalable backend microservices in Go and Python, processing ingestion of high-volume telemetry data.
- Built message queues with Apache Kafka for asynchronous task coordination, handling 12k msg/sec.
- Deployed PostgreSQL failover replicas using Patroni, maintaining 99.99% availability during cloud zone migrations.
- Configured Redis caching patterns for session management and rate limiting across 25 endpoints.

BlueOrbit Tech — Backend Software Engineer (2018 - 2022)
- Built internal tooling and APIs in Python and Go for database migration orchestration.
- Managed Kubernetes deployments, ingress controllers, and secrets management via Vault.

EDUCATION
- B.S. in Computer Science, UIUC (2018)

CORE COMPETENCIES
Go, Python, PostgreSQL, Kafka, Kubernetes, Docker, Redis, Distributed Systems, Linux."""
    },
    {
        "id": "cand-04",
        "name": "Maya Lin",
        "email": "maya.lin@datasphere.ai",
        "title": "Machine Learning Engineer & NLP Specialist",
        "location": "San Francisco, CA",
        "experience_years": 5.2,
        "current_company": "SemanticCraft AI",
        "education": "M.S. Artificial Intelligence, Stanford University",
        "skills": ["Python", "PyTorch", "NLP", "Sentence Transformers", "Vector Databases", "FastAPI", "Scikit-learn", "Docker"],
        "status": "Shortlisted",
        "applied_date": "2026-11-10",
        "gender_proxy": "Female",
        "edu_tier": "Tier-1 University",
        "resume_text": """MAYA LIN
San Francisco, CA | maya.lin@datasphere.ai

PROFILE
Applied Machine Learning Engineer with 5+ years specializing in transformer models, vector similarity search, and high-performance neural retrieval systems.

EXPERIENCE
SemanticCraft AI — Senior ML Engineer (2022 - Present)
- Trained and fine-tuned Sentence-BERT bi-encoders and cross-encoders for legal document semantic search, improving Top-5 recall by 34%.
- Integrated Qdrant and Milvus vector databases with HNSW indexing for 15M document embeddings with 18ms p95 latency.
- Implemented model explainability using integrated gradients and SHAP feature attributions.
- Built real-time inference microservices using FastAPI, ONNX Runtime, and Docker with automated GPU batching.

NeuralWave Systems — Machine Learning Engineer (2019 - 2022)
- Developed Named Entity Recognition (NER) models using PyTorch, Hugging Face Transformers, and SpaCy.
- Created semantic clustering pipelines using Scikit-learn, UMAP, and HDBSCAN.

EDUCATION
- M.S. in Artificial Intelligence, Stanford University (2019)
- B.S. in Mathematics & Computer Science, UC Berkeley (2017)

SKILLS
Python, PyTorch, Transformers, Sentence-BERT, Scikit-learn, FastAPI, Qdrant, Docker, NLP, Vector Embeddings."""
    },
    {
        "id": "cand-05",
        "name": "Sofia Delgado",
        "email": "sofia.delgado@fullstacknet.co",
        "title": "Staff Frontend Engineer & UI Architect",
        "location": "Denver, CO",
        "experience_years": 8.0,
        "current_company": "VividDesign Labs",
        "education": "B.A. Digital Media & B.S. Computer Science, UC San Diego",
        "skills": ["React", "TypeScript", "Tailwind CSS", "Design Systems", "Next.js", "Performance Optimization", "Accessibility (a11y)"],
        "status": "Shortlisted",
        "applied_date": "2026-11-15",
        "gender_proxy": "Female",
        "edu_tier": "Tier-1 University",
        "resume_text": """SOFIA DELGADO
Denver, CO | sofia.delgado@fullstacknet.co

OVERVIEW
Staff Frontend Engineer with 8 years of experience building mission-critical web applications, enterprise design systems, and hyper-responsive user interfaces.

EXPERIENCE
VividDesign Labs — Staff UI Architect (2021 - Present)
- Designed and authored the enterprise design system used by 80+ engineers across 6 product lines in React, TypeScript, and Tailwind CSS.
- Optimized bundle sizes and rendering cycles, boosting Lighthouse performance scores from 64 to 98.
- Enforced WCAG 2.1 AA accessibility standards, keyboard-first navigation patterns, and ARIA live regions.
- Mentored 12 frontend engineers and established rigorous component testing pipelines using Playwright and Vitest.

Aether Web Technologies — Senior Frontend Developer (2017 - 2021)
- Built interactive analytics dashboards with Next.js, React, and SVG/Canvas charting.
- Implemented state management and optimistic updates for collaborative workspace tooling.

EDUCATION
- B.S. Computer Science, UC San Diego (2016)

SKILLS
React, TypeScript, Tailwind CSS, Next.js, Design Systems, Web Performance, a11y, Vitest."""
    },
    {
        "id": "cand-06",
        "name": "Devin Chen",
        "email": "devin.chen@cloudsystems.net",
        "title": "Backend Systems Developer",
        "location": "Boston, MA",
        "experience_years": 4.5,
        "current_company": "Beacon Tech",
        "education": "B.S. Computer Engineering, Northeastern University",
        "skills": ["Python", "Go", "PostgreSQL", "Docker", "Redis", "Distributed Systems", "gRPC"],
        "status": "Review",
        "applied_date": "2026-11-11",
        "gender_proxy": "Non-Binary",
        "edu_tier": "Tier-2 University",
        "resume_text": """DEVIN CHEN
Boston, MA | devin.chen@cloudsystems.net

EXPERIENCE
Beacon Tech — Senior Software Engineer (2022 - Present)
- Developed asynchronous microservices in Python (FastAPI) and Go for enterprise asset tracking.
- Designed relational schemas and partitioned tables in PostgreSQL supporting 10M rows.
- Implemented Redis key eviction policies and distributed cache warming pipelines.
- Implemented gRPC endpoints for low-overhead inter-service communications.

Vertex Solutions — Junior Developer (2020 - 2022)
- Built RESTful endpoints in Python Flask and wrote automated unit and integration tests.

EDUCATION
- B.S. Computer Engineering, Northeastern University (2020)

SKILLS
Python, Go, PostgreSQL, Redis, gRPC, Docker, Git, Linux."""
    },
    {
        "id": "cand-07",
        "name": "Aisha Kamara",
        "email": "aisha.kamara@kernelcraft.org",
        "title": "Distributed Systems & Infrastructure Engineer",
        "location": "Atlanta, GA",
        "experience_years": 7.0,
        "current_company": "OmniStream Global",
        "education": "B.S. Electrical & Computer Engineering, Georgia Tech",
        "skills": ["Go", "Kafka", "Distributed Systems", "PostgreSQL", "Kubernetes", "Redis", "gRPC"],
        "status": "Shortlisted",
        "applied_date": "2026-11-09",
        "gender_proxy": "Female",
        "edu_tier": "Tier-1 University",
        "resume_text": """AISHA KAMARA
Atlanta, GA | aisha.kamara@kernelcraft.org

SUMMARY
7 years of distributed systems engineering specializing in high-throughput message streaming with Kafka, Go microservices, and Kubernetes platform management.

EXPERIENCE
OmniStream Global — Senior Systems Engineer (2021 - Present)
- Led the migration of legacy batch processes to event-driven Kafka streams in Go, processing 50M events daily.
- Implemented multi-region PostgreSQL synchronization and read-replica routing.
- Configured Kubernetes custom controllers and auto-scaling rules based on Kafka consumer lag metrics.

Pinnacle Digital — Software Engineer (2018 - 2021)
- Developed backend microservices in Go and Python, architecting REST and gRPC interfaces.
- Managed Redis cluster configurations and caching invalidation strategies.

EDUCATION
- B.S. in Electrical & Computer Engineering, Georgia Institute of Technology (2017)

SKILLS
Go, Kafka, Kubernetes, PostgreSQL, gRPC, Redis, Distributed Systems, Docker."""
    },
    {
        "id": "cand-08",
        "name": "Julian Brooks",
        "email": "julian.brooks@selfcode.io",
        "title": "Senior Backend Software Engineer",
        "location": "Portland, OR",
        "experience_years": 7.5,
        "current_company": "Independent / Open Source Contributor",
        "education": "Self-Taught / Apprenticeship Program",
        "skills": ["Python", "Go", "PostgreSQL", "Kafka", "Distributed Systems", "Docker", "Redis"],
        "status": "Review",
        "applied_date": "2026-11-08",
        "gender_proxy": "Male",
        "edu_tier": "Non-Traditional / Self-Taught",
        "resume_text": """JULIAN BROOKS
Portland, OR | julian.brooks@selfcode.io | github.com/julianbrooks

SUMMARY
Self-taught senior engineer with 7.5 years of verifiable production experience. Core maintainer of popular open-source Go utilities and distributed task queue libraries.

EXPERIENCE
Open Source Maintainer & Consultant (2022 - Present)
- Author of a distributed queue library in Go downloaded 1.2M times with zero external dependencies.
- Consulted for Series-A startups to optimize PostgreSQL query latency and index utilization.

RelayWave Technologies — Senior Backend Developer (2019 - 2022)
- Built high-throughput API endpoints in Go and Python (FastAPI).
- Integrated Apache Kafka for event-based audit logging and notification triggers.
- Maintained Docker compose development environments and CI pipelines.

EDUCATION
- Self-Taught Software Engineer; Completed Turing School of Software & Design Apprenticeship (2017)

SKILLS
Go, Python, PostgreSQL, Kafka, Redis, Distributed Systems, Docker, Open Source."""
    },
    {
        "id": "cand-09",
        "name": "Priya Nair",
        "email": "priya.nair@datascalelab.com",
        "title": "Machine Learning Platform Engineer",
        "location": "San Jose, CA",
        "experience_years": 6.0,
        "current_company": "Cerebral Analytics",
        "education": "M.S. Data Science, Carnegie Mellon University",
        "skills": ["Python", "PyTorch", "NLP", "Scikit-learn", "FastAPI", "Docker", "Vector Databases"],
        "status": "Shortlisted",
        "applied_date": "2026-11-07",
        "gender_proxy": "Female",
        "edu_tier": "Tier-1 University",
        "resume_text": """PRIYA NAIR
San Jose, CA | priya.nair@datascalelab.com

SUMMARY
6 years of experience in ML engineering, semantic search, and model serving. Strong foundation in NLP, sentence embeddings, and vector databases.

EXPERIENCE
Cerebral Analytics — Lead ML Engineer (2021 - Present)
- Built semantic recommendation system using Sentence Transformers and Milvus vector DB.
- Deployed PyTorch neural models on Kubernetes using FastAPI and Docker.
- Spearheaded fairness auditing pipelines to detect sentiment skew across demographic cohorts.

InnoData Systems — Data Scientist & ML Engineer (2018 - 2021)
- Developed classification and regression pipelines using Scikit-learn, XGBoost, and Pandas.
- Handled data pre-processing and feature engineering for millions of unstructured text documents.

EDUCATION
- M.S. Data Science, Carnegie Mellon University (2018)
- B.Tech Computer Engineering, NIT Trichy (2016)

SKILLS
Python, PyTorch, Scikit-learn, NLP, FastAPI, Docker, Milvus, Vector Search, Pandas."""
    },
    {
        "id": "cand-10",
        "name": "Liam O'Connor",
        "email": "liam.oconnor@dublintech.ie",
        "title": "Backend Software Developer",
        "location": "Raleigh, NC",
        "experience_years": 3.8,
        "current_company": "Apex Point Solutions",
        "education": "B.S. Computer Science, University of North Carolina",
        "skills": ["Python", "PostgreSQL", "Docker", "Redis", "REST APIs"],
        "status": "Under Review",
        "applied_date": "2026-11-13",
        "gender_proxy": "Male",
        "edu_tier": "Tier-2 University",
        "resume_text": """LIAM O'CONNOR
Raleigh, NC | liam.oconnor@dublintech.ie

EXPERIENCE
Apex Point Solutions — Backend Developer (2022 - Present)
- Developed REST API endpoints using Python (FastAPI and Django).
- Maintained PostgreSQL schemas and implemented database migrations.
- Set up Redis caching for authentication tokens and frequently accessed lookups.

CodeCraft Labs — Junior Software Engineer (2020 - 2022)
- Wrote automated tests and assisted with Docker container setup for microservices.

EDUCATION
- B.S. in Computer Science, UNC Chapel Hill (2020)

SKILLS
Python, PostgreSQL, Docker, Redis, Git, Linux."""
    },
    {
        "id": "cand-11",
        "name": "Zachary Zhao",
        "email": "zach.zhao@sysarch.dev",
        "title": "Staff Platform Engineer",
        "location": "San Francisco, CA",
        "experience_years": 10.0,
        "current_company": "HyperScale Networks",
        "education": "B.S. & M.S. EECS, UC Berkeley",
        "skills": ["Go", "Distributed Systems", "Kafka", "PostgreSQL", "Kubernetes", "gRPC", "Redis", "Rust"],
        "status": "Shortlisted",
        "applied_date": "2026-11-05",
        "gender_proxy": "Male",
        "edu_tier": "Tier-1 University",
        "resume_text": """ZACHARY ZHAO
San Francisco, CA | zach.zhao@sysarch.dev

EXPERIENCE
HyperScale Networks — Staff Platform Architect (2020 - Present)
- Architected global routing fabric in Go and Rust handling 60B monthly network packet events.
- Directed Apache Kafka streaming deployment with zero data loss over 4 years.
- Authored internal RFCs for multi-tenant PostgreSQL sharding and schema isolation.

CloudGate Inc — Senior Infrastructure Engineer (2016 - 2020)
- Implemented distributed consensus modules (Raft) and gRPC services in Go.
- Automated Kubernetes infrastructure provisioning using Terraform.

EDUCATION
- M.S. EECS, UC Berkeley (2016)
- B.S. EECS, UC Berkeley (2014)

SKILLS
Go, Rust, Distributed Systems, Kafka, PostgreSQL, Kubernetes, gRPC, Redis."""
    },
    {
        "id": "cand-12",
        "name": "Hannah Berg",
        "email": "hannah.berg@nordicdev.io",
        "title": "Senior Frontend Engineer",
        "location": "New York, NY",
        "experience_years": 6.5,
        "current_company": "Slate & Grid",
        "education": "B.S. Informatics, University of Michigan",
        "skills": ["React", "TypeScript", "Tailwind CSS", "Design Systems", "Next.js", "Accessibility (a11y)"],
        "status": "Shortlisted",
        "applied_date": "2026-11-14",
        "gender_proxy": "Female",
        "edu_tier": "Tier-1 University",
        "resume_text": """HANNAH BERG
New York, NY | hannah.berg@nordicdev.io

EXPERIENCE
Slate & Grid — Senior UI Engineer (2022 - Present)
- Created component libraries with React, TypeScript, Tailwind CSS, and Storybook.
- Conducted regular screen reader and keyboard accessibility audits ensuring WCAG 2.1 compliance.
- Migrated legacy single-page application to Next.js App Router, decreasing initial page load times by 45%.

PixelCraft Interactive — Frontend Engineer (2018 - 2022)
- Built client-side web interfaces with React and Redux Toolkit.
- Collaborated with UX researchers to conduct usability interviews and prototype features.

EDUCATION
- B.S. in Informatics, University of Michigan (2018)

SKILLS
React, TypeScript, Tailwind CSS, Next.js, Design Systems, Storybook, a11y."""
    },
    {
        "id": "cand-13",
        "name": "Carlos Mendez",
        "email": "carlos.mendez@devcraft.mx",
        "title": "Backend Distributed Systems Engineer",
        "location": "Miami, FL",
        "experience_years": 5.5,
        "current_company": "FinTech Matrix",
        "education": "B.S. Computer Engineering, Florida International University",
        "skills": ["Go", "Python", "Kafka", "PostgreSQL", "Docker", "Redis"],
        "status": "Review",
        "applied_date": "2026-11-06",
        "gender_proxy": "Male",
        "edu_tier": "Tier-2 University",
        "resume_text": """CARLOS MENDEZ
Miami, FL | carlos.mendez@devcraft.mx

EXPERIENCE
FinTech Matrix — Backend Systems Engineer (2022 - Present)
- Built payment reconciliation pipelines in Go and Kafka.
- Optimized PostgreSQL queries and managed partition archival strategies.
- Configured Redis caching for currency conversion exchange rates.

BrightLabs Software — Software Developer (2019 - 2022)
- Implemented Python REST APIs and maintained unit test suites.

EDUCATION
- B.S. Computer Engineering, Florida International University (2019)

SKILLS
Go, Python, Kafka, PostgreSQL, Redis, Docker, Git."""
    },
    {
        "id": "cand-14",
        "name": "Ananya Patel",
        "email": "ananya.patel@algorithmic.io",
        "title": "Lead AI & Search Scientist",
        "location": "Sunnyvale, CA",
        "experience_years": 8.5,
        "current_company": "VectorPath Systems",
        "education": "Ph.D. Computer Science, University of Texas at Austin",
        "skills": ["Python", "PyTorch", "NLP", "Sentence Transformers", "Vector Databases", "Scikit-learn", "Docker"],
        "status": "Shortlisted",
        "applied_date": "2026-11-04",
        "gender_proxy": "Female",
        "edu_tier": "Tier-1 University",
        "resume_text": """ANANYA PATEL, Ph.D.
Sunnyvale, CA | ananya.patel@algorithmic.io

EXPERIENCE
VectorPath Systems — Lead AI Scientist (2021 - Present)
- Invented hybrid dense-sparse neural retrieval ranking pipeline combining BM25 and Cross-Encoders.
- Managed vector embeddings cluster storing 50M records with sub-25ms response time.
- Published 4 peer-reviewed papers on neural ranking calibration and demographic parity in AI screening.

DeepSearch Labs — Senior Research Scientist (2018 - 2021)
- Trained custom transformer architectures in PyTorch for specialized legal and technical domain queries.

EDUCATION
- Ph.D. in Computer Science (NLP focus), UT Austin (2018)
- B.S. in Computer Science, Cornell University (2013)

SKILLS
Python, PyTorch, Transformers, NLP, Vector DBs, Scikit-learn, Fairness in AI, Docker."""
    },
    {
        "id": "cand-15",
        "name": "Lucas Weber",
        "email": "lucas.weber@sysforge.de",
        "title": "Systems Software Engineer",
        "location": "Boston, MA",
        "experience_years": 4.0,
        "current_company": "CoreByte Systems",
        "education": "B.S. Computer Science, Boston University",
        "skills": ["Go", "Distributed Systems", "Docker", "PostgreSQL", "Redis"],
        "status": "Under Review",
        "applied_date": "2026-11-15",
        "gender_proxy": "Male",
        "edu_tier": "Tier-2 University",
        "resume_text": """LUCAS WEBER
Boston, MA | lucas.weber@sysforge.de

EXPERIENCE
CoreByte Systems — Software Engineer (2022 - Present)
- Developed network packet monitoring daemon in Go.
- Wrote database schema migrations and indexing in PostgreSQL.
- Implemented Redis pub/sub for real-time dashboard notifications.

EDUCATION
- B.S. Computer Science, Boston University (2022)

SKILLS
Go, Docker, PostgreSQL, Redis, Linux, Git."""
    }
]

FAIRNESS_AUDIT_BENCHMARK = {
    "total_evaluated": 184,
    "total_selected": 46,
    "selection_rate_overall": 0.25,
    "protected_groups": [
        {
            "category": "Gender Proxy (Linguistic)",
            "groups": [
                {
                    "name": "Group A (Female-identifying proxies)",
                    "evaluated": 82,
                    "selected": 22,
                    "selection_rate": 0.268,
                    "disparate_impact_ratio": 1.05,
                    "parity_difference": 0.018,
                    "status": "Compliant"
                },
                {
                    "name": "Group B (Male-identifying proxies)",
                    "evaluated": 94,
                    "selected": 24,
                    "selection_rate": 0.255,
                    "disparate_impact_ratio": 1.00,
                    "parity_difference": 0.000,
                    "status": "Benchmark"
                },
                {
                    "name": "Group C (Non-binary / Neutral proxies)",
                    "evaluated": 8,
                    "selected": 2,
                    "selection_rate": 0.250,
                    "disparate_impact_ratio": 0.98,
                    "parity_difference": -0.005,
                    "status": "Compliant"
                }
            ]
        },
        {
            "category": "Educational Pedigree",
            "groups": [
                {
                    "name": "Tier-1 / Elite Universities",
                    "evaluated": 110,
                    "selected": 30,
                    "selection_rate": 0.272,
                    "disparate_impact_ratio": 1.00,
                    "parity_difference": 0.000,
                    "status": "Benchmark"
                },
                {
                    "name": "State & Tier-2 Universities",
                    "evaluated": 52,
                    "selected": 12,
                    "selection_rate": 0.231,
                    "disparate_impact_ratio": 0.85,
                    "parity_difference": -0.041,
                    "status": "Compliant"
                },
                {
                    "name": "Self-Taught & Non-traditional Bootcamps",
                    "evaluated": 22,
                    "selected": 4,
                    "selection_rate": 0.182,
                    "disparate_impact_ratio": 0.67,
                    "parity_difference": -0.090,
                    "status": "Warning (Review Recommended)"
                }
            ]
        },
        {
            "category": "Experience Cohort",
            "groups": [
                {
                    "name": "Mid-Level (3-5 Years)",
                    "evaluated": 64,
                    "selected": 14,
                    "selection_rate": 0.218,
                    "disparate_impact_ratio": 0.77,
                    "parity_difference": -0.065,
                    "status": "Warning"
                },
                {
                    "name": "Senior Level (6-9 Years)",
                    "evaluated": 92,
                    "selected": 26,
                    "selection_rate": 0.283,
                    "disparate_impact_ratio": 1.00,
                    "parity_difference": 0.000,
                    "status": "Benchmark"
                },
                {
                    "name": "Staff+ Level (10+ Years)",
                    "evaluated": 28,
                    "selected": 6,
                    "selection_rate": 0.214,
                    "disparate_impact_ratio": 0.76,
                    "parity_difference": -0.069,
                    "status": "Compliant"
                }
            ]
        }
    ],
    "disparate_impact_threshold": 0.80, # 4/5ths rule
    "nyc_local_law_144": {
        "status": "Compliant",
        "last_independent_audit_date": "2026-10-18",
        "compliance_score": 96.4,
        "adverse_impact_flag": False
    },
    "audit_history": [
        {
            "id": "AUD-2026-1102",
            "timestamp": "2026-11-02 14:32:00",
            "job_title": "Staff Backend Distributed Systems Engineer",
            "sample_size": 184,
            "demographic_parity_diff": 0.018,
            "equal_opportunity_diff": 0.024,
            "status": "Passed",
            "auditor": "System Automated Verification"
        },
        {
            "id": "AUD-2026-1025",
            "timestamp": "2026-10-25 09:15:00",
            "job_title": "Senior AI/ML Semantic Search Engineer",
            "sample_size": 142,
            "demographic_parity_diff": 0.022,
            "equal_opportunity_diff": 0.019,
            "status": "Passed",
            "auditor": "Compliance Officer (J. Miller)"
        },
        {
            "id": "AUD-2026-1010",
            "timestamp": "2026-10-10 16:40:00",
            "job_title": "Principal Frontend UI/UX Architect",
            "sample_size": 96,
            "demographic_parity_diff": 0.014,
            "equal_opportunity_diff": 0.018,
            "status": "Passed",
            "auditor": "System Automated Verification"
        }
    ]
}
