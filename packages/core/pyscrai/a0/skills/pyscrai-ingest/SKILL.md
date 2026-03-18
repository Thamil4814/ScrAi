# PyScrAI Ingestion Skill

## Overview
This skill provides procedures for document ingestion and knowledge extraction in PyScrAI. It implements a local-first pipeline for processing documents, extracting entities and relations, and building knowledge graphs.

## Prerequisites
- PyScrAI core package installed (`pyscrai`)
- Agent Zero bridge module available (`pyscrai.agents.agent_zero_bridge`)
- Access to project artifacts directory
- Local models available (embeddings, NER)

## Procedures

### 1. Ingest Document
**Objective**: Process a document through the local-first ingestion pipeline.

**Steps**:
1. Use `AgentZeroBridge` to ingest a document.
2. The bridge will delegate to the `pyscrai-ingest` subordinate.
3. The pipeline will: normalize → chunk → embed → extract entities/relations
4. Return the ingestion result with extracted artifacts.

**Example**:
```python
from pyscrai.agents.agent_zero_bridge import AgentZeroBridge

bridge = AgentZeroBridge()
result = bridge.ingest_document(
    project_id="project-123",
    file_path="/path/to/document.pdf",
    document_type="pdf"
)
print(f"Document ingested: {result['document_id']}")
print(f"Entities extracted: {len(result['entities'])}")
print(f"Relations extracted: {len(result['relations'])}")
```

### 2. Extract Entities
**Objective**: Extract entities from text using local NER models.

**Steps**:
1. Use `AgentZeroBridge` to extract entities.
2. The bridge will delegate to the `pyscrai-ingest` subordinate.
3. Local NER model processes the text.
4. Return extracted entities with confidence scores.

**Example**:
```python
result = bridge.extract_entities(
    project_id="project-123",
    text="Admiral Johnson commanded the fleet in the Persian Gulf."
)
for entity in result['entities']:
    print(f"{entity['name']} ({entity['type']}) - confidence: {entity['confidence']}")
```

### 3. Extract Relations
**Objective**: Extract relationships between entities.

**Steps**:
1. Use `AgentZeroBridge` to extract relations.
2. The bridge will delegate to the `pyscrai-ingest` subordinate.
3. Local extraction model identifies relationships.
4. Return extracted relations.

**Example**:
```python
result = bridge.extract_relations(
    project_id="project-123",
    text="Admiral Johnson commanded the fleet in the Persian Gulf.",
    entities=[{"name": "Admiral Johnson", "type": "person"}, {"name": "fleet", "type": "organization"}]
)
for relation in result['relations']:
    print(f"{relation['source']} --[{relation['type'}]--> {relation['target']}")
```

### 4. Build Knowledge Graph
**Objective**: Build or update a knowledge graph from extracted entities and relations.

**Steps**:
1. Use `AgentZeroBridge` to build the knowledge graph.
2. The bridge will delegate to the `pyscrai-ingest` subordinate.
3. Entities and relations are deduplicated and linked.
4. Return the updated graph summary.

**Example**:
```python
result = bridge.build_knowledge_graph(project_id="project-123")
print(f"Graph nodes: {result['node_count']}")
print(f"Graph edges: {result['edge_count']}")
```

### 5. Query Knowledge Graph
**Objective**: Query the knowledge graph for specific information.

**Steps**:
1. Use `AgentZeroBridge` to query the graph.
2. The bridge will delegate to the `pyscrai-ingest` subordinate.
3. Return matching entities and relations.

**Example**:
```python
result = bridge.query_knowledge_graph(
    project_id="project-123",
    query="military commanders in the Persian Gulf"
)
for match in result['matches']:
    print(f"{match['entity']}: {match['relevance']}")
```

## Local-First Pipeline

The ingestion pipeline follows a local-first approach:

### Local Responsibilities (No LLM)
1. **Input Acquisition**: Read and normalize documents
2. **Chunking**: Split documents into manageable chunks
3. **Embeddings**: Generate vector embeddings locally
4. **Entity Extraction**: Extract named entities using local NER
5. **Relation Extraction**: Identify relationships locally
6. **Classification**: Categorize content locally
7. **Deduplication**: Remove duplicate entities/relations

### LLM Escalation Points
1. **Semantic Disambiguation**: When entity meaning is ambiguous
2. **Contextual Synthesis**: When deeper understanding is needed
3. **Ambiguity Resolution**: When multiple interpretations exist
4. **Complex Reasoning**: When inference beyond local models is required

## Scripts

### `scripts/ingest_document.py`
A command-line script for ingesting a document.

**Usage**:
```bash
python /path/to/skill/scripts/ingest_document.py --project-id project-123 --file /path/to/document.pdf
```

### `scripts/extract_entities.py`
Extract entities from text.

**Usage**:
```bash
python /path/to/skill/scripts/extract_entities.py --project-id project-123 --text "Your text here"
```

### `scripts/query_graph.py`
Query the knowledge graph.

**Usage**:
```bash
python /path/to/skill/scripts/query_graph.py --project-id project-123 --query "your query"
```

## Integration Points
- **Agent Zero Bridge**: All procedures go through the bridge module.
- **ArtifactRepository**: The bridge uses the repository for persistence.
- **Ingest Subordinate**: Handles document processing and knowledge extraction.
- **Local Models**: Embeddings and NER models run locally.
- **LLM Providers**: Used only for escalation when local methods are insufficient.

## Error Handling
- If local models are unavailable, escalate to LLM providers.
- If the bridge is unavailable, fall back to direct CLI calls.
- Validate document formats before ingestion.
- Handle partial ingestion gracefully (some chunks may fail).

## Notes
- This skill is designed to be used by Agent Zero agents and subordinates.
- Always prefer local processing to control costs and latency.
- Reserve LLM calls for semantic reasoning and disambiguation.
- The pipeline supports PDF, HTML, Office documents, and plain text.
