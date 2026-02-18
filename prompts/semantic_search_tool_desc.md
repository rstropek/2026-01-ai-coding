SemanticSearch`: semantic search that finds code by meaning, not exact text

### When to Use This Tool

Use `SemanticSearch` when you need to:
- Explore unfamiliar codebases
- Ask \"how / where / what\" questions to understand behavior
- Find code by meaning rather than exact text

### When NOT to Use

Skip `SemanticSearch` for:
1. Exact text matches (use `Grep`)
2. Reading known files (use `Read`)
3. Simple symbol lookups (use `Grep`)
4. Find file by name (use `Glob`)

### Examples

<example>
  Query: \"Where is interface MyInterface implemented in the frontend?\"
<reasoning>
  Good: Complete question asking about implementation location with specific context (frontend).
</reasoning>
</example>

<example>
  Query: \"Where do we encrypt user passwords before saving?\"
<reasoning>
  Good: Clear question about a specific process with context about when it happens.
</reasoning>
</example>

<example>
  Query: \"MyInterface frontend\"
<reasoning>
  BAD: Too vague; use a specific question instead. This would be better as \"Where is MyInterface used in the frontend?\"
</reasoning>
</example>

<example>
  Query: \"AuthService\"
<reasoning>
  BAD: Single word searches should use `Grep` for exact text matching instead.
</reasoning>
</example>

<example>
  Query: \"What is AuthService? How does AuthService work?\"
<reasoning>
  BAD: Combines two separate queries. A single semantic search is not good at looking for multiple things in parallel. Split into separate parallel searches: like \"What is AuthService?\" and \"How does AuthService work?\"
</reasoning>
</example>

### Target Directories

- Provide ONE directory or file path; [] searches the whole repo. No globs or wildcards.
  Good:
  - [\"backend/api/\"]   - focus directory
  - [\"src/components/Button.tsx\"] - single file
  - [] - search everywhere when unsure
  BAD:
  - [\"frontend/\", \"backend/\"] - multiple paths
  - [\"src/**/utils/**\"] - globs
  - [\"*.ts\"] or [\"**/*\"] - wildcard paths

### Search Strategy

1. Start with exploratory queries - semantic search is powerful and often finds relevant context in one go. Begin broad with [] if you're not sure where relevant code is.
2. Review results; if a directory or file stands out, rerun with that as the target.
3. Break large questions into smaller ones (e.g. auth roles vs session storage).
4. For big files (>1K lines) run `SemanticSearch`, or `Grep` if you know the exact symbols you're looking for, scoped to that file instead of reading the entire file.

<example>
  Step 1: { \"query\": \"How does user authentication work?\", \"target_directories\": [], \"explanation\": \"Find auth flow\" }
  Step 2: Suppose results point to backend/auth/ → rerun:
          { \"query\": \"Where are user roles checked?\", \"target_directories\": [\"backend/auth/\"], \"explanation\": \"Find role logic\" }
<reasoning>
  Good strategy: Start broad to understand overall system, then narrow down to specific areas based on initial results.
</reasoning>
</example>

<example>
  Query: \"How are websocket connections handled?\"
  Target: [\"backend/services/realtime.ts\"]
<reasoning>
  Good: We know the answer is in this specific file, but the file is too large to read entirely, so we use semantic search to find the relevant parts.
</reasoning>
</example>

### Usage
- When full chunk contents are provided, avoid re-reading the exact same chunk contents using the Read tool.
- Sometimes, just the chunk signatures and not the full chunks will be shown. Chunk signatures are usually Class or Function signatures that chunks are contained in. Use the Read or Grep tools to explore these chunks or files if you think they might be relevant.
- When reading chunks that weren't provided as full chunks (e.g. only as line ranges or signatures), you'll sometimes want to expand the chunk ranges to include the start of the file to see imports, expand the range to include lines from the signature, or expand the range to read multiple chunks from a file at once.