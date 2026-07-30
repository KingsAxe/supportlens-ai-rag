# SupportLens AI

**Customer Support Intelligence RAG Agent**

SupportLens AI is an end-to-end Retrieval-Augmented Generation application for customer-support teams. It helps agents and support managers search historical support cases, retrieve relevant policies and resolution playbooks, and generate grounded response recommendations with citations.

The project is built for the DataTalksClub LLM Zoomcamp 2026 final project and demonstrates a production-style LLM application with automated ingestion, hybrid retrieval, reranking, query rewriting, evaluation, user feedback, monitoring, Docker-based reproducibility, and optional GCP deployment.

## What It Does

* Ingests support tickets, customer utterances, support policies, and resolution playbooks
* Builds a searchable knowledge base with keyword and vector retrieval
* Evaluates keyword, vector, hybrid, and reranked retrieval approaches
* Rewrites user queries to improve retrieval quality
* Generates grounded answers with citations from retrieved evidence
* Collects user feedback on answer quality
* Tracks latency, token usage, retrieval method, and feedback trends
* Provides a Streamlit interface and monitoring dashboard
* Runs locally with Docker Compose
* Can be deployed to GCP Cloud Run
