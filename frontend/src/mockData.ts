import { Job, Candidate, FairnessBenchmark } from './types';

export const INITIAL_JOBS: Job[] = [
  {
    id: "job-lead-backend",
    title: "Staff Backend Distributed Systems Engineer",
    company: "TalentRank Core Platform",
    department: "Infrastructure & Data Services",
    location: "San Francisco, CA / Remote",
    experience_required: 6,
    salary_range: "$190,000 - $240,000",
    type: "Full-time",
    status: "Active",
    required_skills: [
      "Go",
      "Python",
      "Distributed Systems",
      "PostgreSQL",
      "Kafka",
      "gRPC",
      "Kubernetes",
      "Redis"
    ],
    nice_to_have_skills: [
      "Rust",
      "ClickHouse",
      "eBPF",
      "OpenTelemetry"
    ],
    description: `About the Role:
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
- Excellent track record of performance profiling (pprof, tracing, p99 latency mitigation).`
  },
  {
    id: "job-sr-ml-engineer",
    title: "Senior AI/ML Semantic Search Engineer",
    company: "TalentRank Core Platform",
    department: "Applied Machine Learning",
    location: "New York, NY / Hybrid",
    experience_required: 4,
    salary_range: "$180,000 - $225,000",
    type: "Full-time",
    status: "Active",
    required_skills: [
      "Python",
      "PyTorch",
      "Vector Databases",
      "Sentence Transformers",
      "NLP",
      "FastAPI",
      "Scikit-learn",
      "Docker"
    ],
    nice_to_have_skills: [
      "Qdrant",
      "ONNX Runtime",
      "Triton Inference Server",
      "LangChain"
    ],
    description: `About the Role:
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
- Production experience deploying REST/gRPC ML microservices via Docker and FastAPI.`
  },
  {
    id: "job-principal-frontend",
    title: "Principal Frontend UI/UX Architect",
    company: "TalentRank Core Platform",
    department: "Product Engineering",
    location: "Remote (US/EU)",
    experience_required: 7,
    salary_range: "$200,000 - $250,000",
    type: "Full-time",
    status: "Active",
    required_skills: [
      "React",
      "TypeScript",
      "Tailwind CSS",
      "Design Systems",
      "Performance Optimization",
      "State Management",
      "Accessibility (a11y)",
      "Next.js"
    ],
    nice_to_have_skills: [
      "WebSockets",
      "Web Workers",
      "Framer Motion",
      "Playwright"
    ],
    description: `About the Role:
We are hiring a Principal Frontend Architect to drive the frontend architecture, design system, and user experience for our recruitment intelligence platform.

Responsibilities:
- Own the modular frontend component design system built with React, TypeScript, and modern styling.
- Ensure sub-100ms interaction latency for data-heavy tables, complex filtering, and interactive charts.
- Champion accessibility (WCAG 2.1 AA compliance), keyboard navigation, and responsive typography.`
  }
];

export const INITIAL_CANDIDATES: Candidate[] = [
  {
    id: "cand-01",
    rank: 1,
    name: "Elena Rostova",
    email: "elena.rostova@devmail.io",
    title: "Senior Distributed Systems Engineer",
    location: "Seattle, WA",
    experience_years: 8.0,
    current_company: "CloudStream Systems",
    education: "M.S. Computer Science, University of Washington",
    skills: ["Go", "Distributed Systems", "Kafka", "PostgreSQL", "gRPC", "Kubernetes", "Redis", "Docker", "Prometheus"],
    status: "Shortlisted",
    applied_date: "2026-11-12",
    gender_proxy: "Female",
    edu_tier: "Tier-1 University",
    keyword_score: 96.0,
    semantic_score: 95.2,
    experience_score: 98.0,
    overall_score: 95.8,
    matched_skills: ["Go", "Distributed Systems", "PostgreSQL", "Kafka", "gRPC", "Kubernetes", "Redis"],
    missing_skills: ["Python"],
    explanation: {
      summary: "Elena Rostova demonstrates exceptional alignment with the Staff Backend specification, exhibiting verified architecture depth in Go, Kafka, and Redis caching topologies.",
      strengths: [
        "Architected distributed transaction ledgers handling 2.4B daily records in Go.",
        "Exceeds minimum experience threshold (8.0 yrs vs 6 yrs required).",
        "Deep production experience with SASL Kafka partitioning and gRPC circuit breaking."
      ],
      gaps: [
        "Unverified Python concurrency usage in production context."
      ],
      metrics: {
        keyword_match_pct: 96.0,
        semantic_similarity_pct: 95.2,
        experience_fit_pct: 98.0,
        skills_matched_count: 7,
        skills_missing_count: 1
      }
    },
    resume_text: `ELENA ROSTOVA
Seattle, WA | elena.rostova@devmail.io | github.com/erostova

SUMMARY
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
Go (expert), C++, PostgreSQL, Kafka, Redis, gRPC, Kubernetes, Docker, Linux Internals, OpenTelemetry, Distributed Consensus (Raft).`
  },
  {
    id: "cand-02",
    rank: 2,
    name: "Marcus Vance",
    email: "marcus.vance@techvault.org",
    title: "Staff Backend Engineer",
    location: "Austin, TX",
    experience_years: 9.5,
    current_company: "Apex Data Labs",
    education: "B.S. Software Engineering, UT Austin",
    skills: ["Go", "Python", "Distributed Systems", "PostgreSQL", "Kafka", "Redis", "Kubernetes", "gRPC", "AWS"],
    status: "Shortlisted",
    applied_date: "2026-11-14",
    gender_proxy: "Male",
    edu_tier: "Tier-1 University",
    keyword_score: 98.2,
    semantic_score: 93.6,
    experience_score: 100.0,
    overall_score: 95.1,
    matched_skills: ["Go", "Python", "Distributed Systems", "PostgreSQL", "Kafka", "gRPC", "Kubernetes", "Redis"],
    missing_skills: [],
    explanation: {
      summary: "Marcus Vance satisfies 100% of the core required technical skill criteria with 9.5 years of verifiable production experience in high-concurrency Go and Python.",
      strengths: [
        "100% verified coverage across all mandatory technical requirements.",
        "Extensive seniority (+3.5 yrs over required baseline).",
        "Experience leading architectural migrations from monoliths to event-driven Go on EKS."
      ],
      gaps: [],
      metrics: {
        keyword_match_pct: 98.2,
        semantic_similarity_pct: 93.6,
        experience_fit_pct: 100.0,
        skills_matched_count: 8,
        skills_missing_count: 0
      }
    },
    resume_text: `MARCUS VANCE
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
Infrastructure: Kubernetes, Docker, AWS, Kafka, Redis, PostgreSQL, gRPC, Terraform.`
  },
  {
    id: "cand-11",
    rank: 3,
    name: "Zachary Zhao",
    email: "zach.zhao@sysarch.dev",
    title: "Staff Platform Engineer",
    location: "San Francisco, CA",
    experience_years: 10.0,
    current_company: "HyperScale Networks",
    education: "B.S. & M.S. EECS, UC Berkeley",
    skills: ["Go", "Distributed Systems", "Kafka", "PostgreSQL", "Kubernetes", "gRPC", "Redis", "Rust"],
    status: "Shortlisted",
    applied_date: "2026-11-05",
    gender_proxy: "Male",
    edu_tier: "Tier-1 University",
    keyword_score: 94.0,
    semantic_score: 94.8,
    experience_score: 100.0,
    overall_score: 94.6,
    matched_skills: ["Go", "Distributed Systems", "PostgreSQL", "Kafka", "gRPC", "Kubernetes", "Redis"],
    missing_skills: ["Python"],
    explanation: {
      summary: "Zachary Zhao exhibits premier platform architecture expertise, having designed global routing fabrics handling 60B monthly network events.",
      strengths: [
        "10 years of systems engineering at HyperScale Networks.",
        "Authored RFCs for multi-tenant PostgreSQL sharding and consensus protocols.",
        "Demonstrated proficiency with high-performance low-level languages (Go, Rust)."
      ],
      gaps: [
        "Missing modern Python asynchronous framework experience."
      ],
      metrics: {
        keyword_match_pct: 94.0,
        semantic_similarity_pct: 94.8,
        experience_fit_pct: 100.0,
        skills_matched_count: 7,
        skills_missing_count: 1
      }
    },
    resume_text: `ZACHARY ZHAO
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
Go, Rust, Distributed Systems, Kafka, PostgreSQL, Kubernetes, gRPC, Redis.`
  },
  {
    id: "cand-07",
    rank: 4,
    name: "Aisha Kamara",
    email: "aisha.kamara@kernelcraft.org",
    title: "Distributed Systems & Infrastructure Engineer",
    location: "Atlanta, GA",
    experience_years: 7.0,
    current_company: "OmniStream Global",
    education: "B.S. Electrical & Computer Engineering, Georgia Tech",
    skills: ["Go", "Kafka", "Distributed Systems", "PostgreSQL", "Kubernetes", "Redis", "gRPC"],
    status: "Shortlisted",
    applied_date: "2026-11-09",
    gender_proxy: "Female",
    edu_tier: "Tier-1 University",
    keyword_score: 92.5,
    semantic_score: 91.0,
    experience_score: 96.0,
    overall_score: 92.2,
    matched_skills: ["Go", "Distributed Systems", "PostgreSQL", "Kafka", "gRPC", "Kubernetes", "Redis"],
    missing_skills: ["Python"],
    explanation: {
      summary: "Aisha Kamara brings verified event-driven Kafka and Go microservice capability, successfully executing migrations handling 50M daily events.",
      strengths: [
        "7 years of production infrastructure engineering.",
        "Built auto-scaling Kubernetes controllers based on Kafka consumer lag metrics.",
        "Solid PostgreSQL multi-region replication experience."
      ],
      gaps: [
        "Python backend frameworks not highlighted."
      ],
      metrics: {
        keyword_match_pct: 92.5,
        semantic_similarity_pct: 91.0,
        experience_fit_pct: 96.0,
        skills_matched_count: 7,
        skills_missing_count: 1
      }
    },
    resume_text: `AISHA KAMARA
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
Go, Kafka, Kubernetes, PostgreSQL, gRPC, Redis, Distributed Systems, Docker.`
  },
  {
    id: "cand-03",
    rank: 5,
    name: "Tariq Al-Mansoor",
    email: "tariq.mansoor@codeworks.dev",
    title: "Senior Cloud Infrastructure & Backend Engineer",
    location: "Chicago, IL",
    experience_years: 6.5,
    current_company: "Nexus Distributed",
    education: "B.S. Computer Science, University of Illinois Urbana-Champaign",
    skills: ["Go", "Python", "Kubernetes", "PostgreSQL", "Kafka", "Docker", "Redis", "Distributed Systems"],
    status: "Review",
    applied_date: "2026-11-13",
    gender_proxy: "Male",
    edu_tier: "Tier-1 University",
    keyword_score: 89.0,
    semantic_score: 88.4,
    experience_score: 94.0,
    overall_score: 89.5,
    matched_skills: ["Go", "Python", "Distributed Systems", "PostgreSQL", "Kafka", "Kubernetes", "Redis"],
    missing_skills: ["gRPC"],
    explanation: {
      summary: "Tariq Al-Mansoor matches almost all required skills and satisfies the 6-year experience mandate.",
      strengths: [
        "Dual proficiency in Go and Python microservices.",
        "Hands-on experience with Patroni failover for PostgreSQL.",
        "Built asynchronous task streaming via Kafka handling 12k msg/sec."
      ],
      gaps: [
        "gRPC not explicitly listed on resume."
      ],
      metrics: {
        keyword_match_pct: 89.0,
        semantic_similarity_pct: 88.4,
        experience_fit_pct: 94.0,
        skills_matched_count: 7,
        skills_missing_count: 1
      }
    },
    resume_text: `TARIQ AL-MANSOOR
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
Go, Python, PostgreSQL, Kafka, Kubernetes, Docker, Redis, Distributed Systems, Linux.`
  },
  {
    id: "cand-08",
    rank: 6,
    name: "Julian Brooks",
    email: "julian.brooks@selfcode.io",
    title: "Senior Backend Software Engineer",
    location: "Portland, OR",
    experience_years: 7.5,
    current_company: "Independent / Open Source Contributor",
    education: "Self-Taught / Apprenticeship Program",
    skills: ["Python", "Go", "PostgreSQL", "Kafka", "Distributed Systems", "Docker", "Redis"],
    status: "Review",
    applied_date: "2026-11-08",
    gender_proxy: "Male",
    edu_tier: "Non-Traditional / Self-Taught",
    keyword_score: 86.0,
    semantic_score: 87.2,
    experience_score: 96.0,
    overall_score: 88.1,
    matched_skills: ["Go", "Python", "Distributed Systems", "PostgreSQL", "Kafka", "Redis"],
    missing_skills: ["Kubernetes", "gRPC"],
    explanation: {
      summary: "Julian Brooks shows impressive real-world backend craftsmanship as an open-source distributed queue author with 1.2M downloads.",
      strengths: [
        "Demonstrated mastery of concurrency in Go and distributed queue design.",
        "Exceeds experience requirements (7.5 yrs).",
        "Deep understanding of zero-dependency systems."
      ],
      gaps: [
        "Lacks documented Kubernetes cluster administration and gRPC service definitions."
      ],
      metrics: {
        keyword_match_pct: 86.0,
        semantic_similarity_pct: 87.2,
        experience_fit_pct: 96.0,
        skills_matched_count: 6,
        skills_missing_count: 2
      }
    },
    resume_text: `JULIAN BROOKS
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
Go, Python, PostgreSQL, Kafka, Redis, Distributed Systems, Docker, Open Source.`
  },
  {
    id: "cand-06",
    rank: 7,
    name: "Devin Chen",
    email: "devin.chen@cloudsystems.net",
    title: "Backend Systems Developer",
    location: "Boston, MA",
    experience_years: 4.5,
    current_company: "Beacon Tech",
    education: "B.S. Computer Engineering, Northeastern University",
    skills: ["Python", "Go", "PostgreSQL", "Docker", "Redis", "Distributed Systems", "gRPC"],
    status: "Review",
    applied_date: "2026-11-11",
    gender_proxy: "Non-Binary",
    edu_tier: "Tier-2 University",
    keyword_score: 82.0,
    semantic_score: 80.5,
    experience_score: 84.0,
    overall_score: 81.6,
    matched_skills: ["Go", "Python", "Distributed Systems", "PostgreSQL", "gRPC", "Redis"],
    missing_skills: ["Kafka", "Kubernetes"],
    explanation: {
      summary: "Devin Chen presents a solid backend foundation across Go, Python, and PostgreSQL, though seniority is slightly under the 6-year target.",
      strengths: [
        "Good experience with partitioned PostgreSQL tables and Redis cache warming.",
        "Production gRPC experience."
      ],
      gaps: [
        "Seniority is 4.5 years vs 6.0 years required.",
        "No documented Apache Kafka event streaming."
      ],
      metrics: {
        keyword_match_pct: 82.0,
        semantic_similarity_pct: 80.5,
        experience_fit_pct: 84.0,
        skills_matched_count: 6,
        skills_missing_count: 2
      }
    },
    resume_text: `DEVIN CHEN
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
Python, Go, PostgreSQL, Redis, gRPC, Docker, Git, Linux.`
  },
  {
    id: "cand-13",
    rank: 8,
    name: "Carlos Mendez",
    email: "carlos.mendez@devcraft.mx",
    title: "Backend Distributed Systems Engineer",
    location: "Miami, FL",
    experience_years: 5.5,
    current_company: "FinTech Matrix",
    education: "B.S. Computer Engineering, Florida International University",
    skills: ["Go", "Python", "Kafka", "PostgreSQL", "Docker", "Redis"],
    status: "Review",
    applied_date: "2026-11-06",
    gender_proxy: "Male",
    edu_tier: "Tier-2 University",
    keyword_score: 80.5,
    semantic_score: 79.2,
    experience_score: 88.0,
    overall_score: 81.1,
    matched_skills: ["Go", "Python", "PostgreSQL", "Kafka", "Redis"],
    missing_skills: ["Distributed Systems", "Kubernetes", "gRPC"],
    explanation: {
      summary: "Carlos Mendez possesses relevant payment pipeline experience in Go and Kafka, but needs more evidence of large-scale Kubernetes orchestration.",
      strengths: [
        "Solid hands-on experience with Kafka and Go.",
        "PostgreSQL query optimization and partition archival."
      ],
      gaps: [
        "Missing Kubernetes and gRPC specifications."
      ],
      metrics: {
        keyword_match_pct: 80.5,
        semantic_similarity_pct: 79.2,
        experience_fit_pct: 88.0,
        skills_matched_count: 5,
        skills_missing_count: 3
      }
    },
    resume_text: `CARLOS MENDEZ
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
Go, Python, Kafka, PostgreSQL, Redis, Docker, Git.`
  },
  {
    id: "cand-15",
    rank: 9,
    name: "Lucas Weber",
    email: "lucas.weber@sysforge.de",
    title: "Systems Software Engineer",
    location: "Boston, MA",
    experience_years: 4.0,
    current_company: "CoreByte Systems",
    education: "B.S. Computer Science, Boston University",
    skills: ["Go", "Distributed Systems", "Docker", "PostgreSQL", "Redis"],
    status: "Under Review",
    applied_date: "2026-11-15",
    gender_proxy: "Male",
    edu_tier: "Tier-2 University",
    keyword_score: 73.0,
    semantic_score: 74.5,
    experience_score: 80.0,
    overall_score: 75.1,
    matched_skills: ["Go", "Distributed Systems", "PostgreSQL", "Redis"],
    missing_skills: ["Python", "Kafka", "Kubernetes", "gRPC"],
    explanation: {
      summary: "Promising systems programmer with strong Go foundation, but lacks several platform requirements for Staff level.",
      strengths: [
        "Strong fundamentals in low-level Go network monitoring."
      ],
      gaps: [
        "Missing Kafka, Kubernetes, and gRPC.",
        "4.0 years experience vs 6.0 years required."
      ],
      metrics: {
        keyword_match_pct: 73.0,
        semantic_similarity_pct: 74.5,
        experience_fit_pct: 80.0,
        skills_matched_count: 4,
        skills_missing_count: 4
      }
    },
    resume_text: `LUCAS WEBER
Boston, MA | lucas.weber@sysforge.de

EXPERIENCE
CoreByte Systems — Software Engineer (2022 - Present)
- Developed network packet monitoring daemon in Go.
- Wrote database schema migrations and indexing in PostgreSQL.
- Implemented Redis pub/sub for real-time dashboard notifications.

EDUCATION
- B.S. Computer Science, Boston University (2022)

SKILLS
Go, Docker, PostgreSQL, Redis, Linux, Git.`
  },
  {
    id: "cand-10",
    rank: 10,
    name: "Liam O'Connor",
    email: "liam.oconnor@dublintech.ie",
    title: "Backend Software Developer",
    location: "Raleigh, NC",
    experience_years: 3.8,
    current_company: "Apex Point Solutions",
    education: "B.S. Computer Science, University of North Carolina",
    skills: ["Python", "PostgreSQL", "Docker", "Redis", "REST APIs"],
    status: "Under Review",
    applied_date: "2026-11-13",
    gender_proxy: "Male",
    edu_tier: "Tier-2 University",
    keyword_score: 65.0,
    semantic_score: 68.0,
    experience_score: 76.0,
    overall_score: 68.8,
    matched_skills: ["Python", "PostgreSQL", "Redis"],
    missing_skills: ["Go", "Distributed Systems", "Kafka", "Kubernetes", "gRPC"],
    explanation: {
      summary: "Liam O'Connor is early in his career and primarily experienced in Python REST APIs rather than high-throughput distributed systems.",
      strengths: [
        "Competent in Python web services and PostgreSQL migrations."
      ],
      gaps: [
        "Missing Go, Kafka, Kubernetes, and gRPC.",
        "Under-qualified for Staff engineering mandate (3.8 yrs vs 6 yrs)."
      ],
      metrics: {
        keyword_match_pct: 65.0,
        semantic_similarity_pct: 68.0,
        experience_fit_pct: 76.0,
        skills_matched_count: 3,
        skills_missing_count: 5
      }
    },
    resume_text: `LIAM O'CONNOR
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
Python, PostgreSQL, Docker, Redis, Git, Linux.`
  }
];

export const INITIAL_FAIRNESS: { benchmark: FairnessBenchmark } = {
  benchmark: {
    total_evaluated: 184,
    total_selected: 46,
    selection_rate_overall: 0.25,
    protected_groups: [
      {
        category: "Gender Proxy (Linguistic)",
        groups: [
          {
            name: "Group A (Female-identifying proxies)",
            evaluated: 82,
            selected: 22,
            selection_rate: 0.268,
            disparate_impact_ratio: 1.05,
            parity_difference: 0.018,
            status: "Compliant"
          },
          {
            name: "Group B (Male-identifying proxies)",
            evaluated: 94,
            selected: 24,
            selection_rate: 0.255,
            disparate_impact_ratio: 1.00,
            parity_difference: 0.000,
            status: "Benchmark"
          },
          {
            name: "Group C (Non-binary / Neutral proxies)",
            evaluated: 8,
            selected: 2,
            selection_rate: 0.250,
            disparate_impact_ratio: 0.98,
            parity_difference: -0.005,
            status: "Compliant"
          }
        ]
      },
      {
        category: "Educational Pedigree",
        groups: [
          {
            name: "Tier-1 / Elite Universities",
            evaluated: 110,
            selected: 30,
            selection_rate: 0.272,
            disparate_impact_ratio: 1.00,
            parity_difference: 0.000,
            status: "Benchmark"
          },
          {
            name: "State & Tier-2 Universities",
            evaluated: 52,
            selected: 12,
            selection_rate: 0.231,
            disparate_impact_ratio: 0.85,
            parity_difference: -0.041,
            status: "Compliant"
          },
          {
            name: "Self-Taught & Non-traditional Bootcamps",
            evaluated: 22,
            selected: 4,
            selection_rate: 0.182,
            disparate_impact_ratio: 0.67,
            parity_difference: -0.090,
            status: "Warning (Review Recommended)"
          }
        ]
      },
      {
        category: "Experience Cohort",
        groups: [
          {
            name: "Mid-Level (3-5 Years)",
            evaluated: 64,
            selected: 14,
            selection_rate: 0.218,
            disparate_impact_ratio: 0.77,
            parity_difference: -0.065,
            status: "Warning"
          },
          {
            name: "Senior Level (6-9 Years)",
            evaluated: 92,
            selected: 26,
            selection_rate: 0.283,
            disparate_impact_ratio: 1.00,
            parity_difference: 0.000,
            status: "Benchmark"
          },
          {
            name: "Staff+ Level (10+ Years)",
            evaluated: 28,
            selected: 6,
            selection_rate: 0.214,
            disparate_impact_ratio: 0.76,
            parity_difference: -0.069,
            status: "Compliant"
          }
        ]
      }
    ],
    disparate_impact_threshold: 0.80,
    nyc_local_law_144: {
      status: "Compliant",
      last_independent_audit_date: "2026-10-18",
      compliance_score: 96.4,
      adverse_impact_flag: false
    },
    audit_history: [
      {
        id: "AUD-2026-1102",
        timestamp: "2026-11-02 14:32:00",
        job_title: "Staff Backend Distributed Systems Engineer",
        sample_size: 184,
        demographic_parity_diff: 0.018,
        equal_opportunity_diff: 0.024,
        status: "Passed",
        auditor: "System Automated Verification"
      },
      {
        id: "AUD-2026-1025",
        timestamp: "2026-10-25 09:15:00",
        job_title: "Senior AI/ML Semantic Search Engineer",
        sample_size: 142,
        demographic_parity_diff: 0.022,
        equal_opportunity_diff: 0.019,
        status: "Passed",
        auditor: "Compliance Officer (J. Miller)"
      },
      {
        id: "AUD-2026-1010",
        timestamp: "2026-10-10 16:40:00",
        job_title: "Principal Frontend UI/UX Architect",
        sample_size: 96,
        demographic_parity_diff: 0.014,
        equal_opportunity_diff: 0.018,
        status: "Passed",
        auditor: "System Automated Verification"
      }
    ]
  }
};
