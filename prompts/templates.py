QUERY_FANOUT_PROMPT = """You are a search query decomposition system that mirrors how Google AI Overviews, ChatGPT Search, and Perplexity internally fan out a single user query into multiple sub-queries for comprehensive retrieval.

This process is based on the query fan-out architecture documented in Google Patent US12158907B1 ("Thematic Search") and industry research on LLM-driven query decomposition.

## Your Task

Given the seed query: "{seed_keyword}"

Execute the following pipeline:

### Stage 1: Query Analysis
Analyze the seed query to determine:
- User intent (informational, transactional, navigational, or commercial_investigation)
- Query complexity (simple factual vs. complex multi-faceted)
- Key entities and attributes involved

### Stage 2: Generate Fan-Out Sub-Queries
Decompose the seed query into sub-queries across ALL 8 fan-out types. These are the same categories that search engines and AI systems use internally to ensure complete topic coverage:

1. **Equivalent Queries** (3-5): Alternative phrasings that express the identical information need. Different words, same meaning. These help retrieve documents that use different terminology.

2. **Follow-Up Queries** (4-6): Logical next questions a user would naturally ask after getting an answer to the seed query. These represent the sequential information journey.

3. **Generalization Queries** (3-4): Broader versions of the seed query that capture the parent topic or wider context. Moving up the topic hierarchy.

4. **Specification Queries** (5-7): Narrower, more detailed versions that drill into specific aspects, attributes, or sub-components of the seed query. Moving down the topic hierarchy.

5. **Canonicalization Queries** (2-3): Standardized, normalized phrasings — the "official" or most common way to express this query. How a knowledge base or encyclopedia would phrase it.

6. **Language Translation Queries** (2-3): The query expressed in different languages relevant to the topic's audience, OR translations between technical jargon and plain language.

7. **Entailment Queries** (4-6): Questions that are logically implied by the seed query — if the user is asking X, they must also need to know Y. These are the hidden, unstated information needs.

8. **Clarification Queries** (3-5): Disambiguation questions that resolve ambiguity in the seed query. "Did you mean X or Y?" These represent the different possible interpretations.

### Stage 3: Self-Critique
For each generated sub-query, evaluate:
- Is this query genuinely distinct from others in the list? (remove duplicates)
- Would a real search engine actually generate this sub-query? (remove implausible ones)
- Does this query add retrieval coverage that no other sub-query provides? (remove redundant ones)

Only include queries that pass all three checks.

## Output Format

For EACH sub-query, provide:
- "query_text": The exact sub-query text
- "intent": The intent category (informational | transactional | navigational | commercial_investigation)
- "query_type": One of: equivalent, follow_up, generalization, specification, canonicalization, language_translation, entailment, clarification
- "rationale": One sentence explaining what retrieval coverage this sub-query adds that the seed query alone would miss

Return your response as a valid JSON array. Each element must have these exact keys:
"query_text", "intent", "query_type", "rationale"

Return ONLY the JSON array, no markdown fencing, no explanation before or after."""


CONTENT_ANALYSIS_PROMPT = """You are a content strategist analyzing an existing article to find optimal placement for new query targets.

## Existing Content Structure:
{content_sections_json}

## Queries to Place:
{selected_queries_json}

For each query, determine:
1. Which existing section is the best placement target (by section_index)
2. Whether to:
   - "expand_existing": Add a paragraph within the existing section
   - "new_subsection": Create a new H3/H4 subsection under the target section
   - "new_paragraph": Add standalone paragraph content
3. A suggested heading (if new_subsection)
4. A content brief: 2-3 sentences describing what should be written to naturally target this query while fitting the article's voice and flow
5. Your reasoning for this placement

Important rules:
- Never suggest placing content that contradicts or redundantly overlaps existing content
- Distribute queries across the article; avoid clustering all in one section
- Respect the logical flow of the existing content
- If a query maps to a topic not yet in the article, suggest placing it at the most thematically logical position

Return a JSON array where each element has:
"query_text", "target_section_index", "placement_type", "suggested_heading" (null if not new_subsection), "content_brief", "reasoning"

Return ONLY the JSON array."""


CONTENT_GENERATION_PROMPT = """You are an expert content writer. Write the actual content for the following query placement within an existing article.

## Article Title: {article_title}
## Article URL: {article_url}

## Target Section: {section_heading}
## Existing Section Content (for context and tone matching):
{section_body}

## Query to Target: {query_text}
## Placement Type: {placement_type}
## Suggested Heading: {suggested_heading}
## Content Brief: {content_brief}
{brand_guidelines_section}
Write the full content that should be added. Follow these rules:
- Naturally incorporate the target query into the content
- If placement_type is "new_subsection", start with the heading as an H3 (### Heading)
- Write 150-300 words of substantive, useful content
- Do NOT use filler phrases like "In today's world" or "It's important to note"
- Be specific, actionable, and informative
- Do NOT include any JSON or metadata — just write the content as it should appear in the article
- If brand guidelines are provided above, follow them EXACTLY — match the brand's tone, voice, terminology, sentence structure, and formatting rules. The brand guidelines take priority over all other style instructions.
- If no brand guidelines are provided, match the tone and writing style of the existing article.

Write ONLY the content, nothing else."""


BRAND_EXTRACTION_PROMPT = """You are a brand voice analyst. Analyze the following brand guidelines document and extract a structured brand voice profile.

## Raw Brand Guidelines:
{guidelines_text}

Extract and organize the following into a clear, concise profile that a content writer can follow:

### 1. Brand Voice & Tone
- Overall tone (e.g., formal, conversational, authoritative, friendly, technical)
- Voice characteristics (e.g., first-person plural "we", second-person "you", third-person)
- Emotional register (e.g., empathetic, confident, urgent, calm)

### 2. Writing Style
- Sentence structure preferences (short/punchy vs. long/detailed)
- Paragraph length preferences
- Use of headers and subheaders
- Formatting preferences (bullet points, numbered lists, bold text usage)

### 3. Terminology & Language
- Preferred terms and phrases the brand uses
- Banned or avoided words/phrases
- Industry jargon stance (use it freely vs. explain it vs. avoid it)
- Capitalization rules for brand-specific terms

### 4. Audience & Persona
- Who the brand is writing for
- Assumed knowledge level of the reader
- How the brand addresses the reader

### 5. Content Rules
- Any specific dos and don'ts
- Call-to-action style
- How the brand handles statistics, claims, and citations
- Any formatting or structural requirements

If any section is not covered in the provided guidelines, note it as "Not specified in guidelines."

Return the profile as clean, readable text (not JSON). Be concise but complete."""
