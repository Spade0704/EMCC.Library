---
title: "Foo Framework"
type: framework
visibility: internal
completion: 60
status: solid
last_updated: 2026-05-01
blocking_questions: ["What is X?", "How does Y work?"]
---

# Foo Framework

Two open questions. Title "Foo Framework" intentionally differs from filename "Foo" so the wikilink-uses-filename-stem test has something to bite on.

This prose contains BadTerm and should be flagged at file line 15.

```python
# BadTerm inside a backtick fence — should NOT match.
print("BadTerm")
```

~~~text
BadTerm inside a tilde fence — should NOT match.
~~~

The inline `BadTerm` here is single-backtick wrapped — should NOT match.

Final line: BadTerm here at file line 28 verifies stripping preserved line counts.
