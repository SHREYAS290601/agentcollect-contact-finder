
# ABOUT.md

## Why this role

I’m interested in AgentCollect because it sits at the intersection of AI-native engineering, workflow automation, and messy real-world operations. I like building the unglamorous but critical parts of AI systems: orchestration, evals, failure analysis, data pipelines, and tools that make engineers faster. Collections feels like the right kind of problem for agentic AI because it involves repeated follow-ups, negotiation logic, disputes, escalation rules, payments, and customer-specific playbooks.

## How you work with AI tools

I use AI tools with specific instructions, not open-ended prompts. For coding, I mainly use Cursor and Codex/Claude-style coding agents inside the repo: I give them a narrow scope, the files they are allowed to touch, the behavior I want, and the tests I expect. For architecture or review, I use LLMs to compare approaches, find edge cases, and critique my assumptions before I commit.

I trust the model for acceleration work: scaffolding code, refactoring, writing tests, explaining unfamiliar framework patterns, and spotting obvious bugs. I override it when the decision depends on product judgment, data leakage risk, evaluation design, confidence thresholds, or anything where a plausible answer could still be wrong.

For this challenge, I used AI to move faster through implementation, but I manually controlled the important choices: committing `PLAN.md` before code, keeping Stage A separate from Stage B details, preferring precision over coverage, preserving provenance, and routing weak or conflicting contacts to human review. My rule is simple: AI can draft, but tests, diffs, reproducible commands, provenance, and code review decide whether I trust the result.

## Your last project

* **One ambiguity** you faced and how you resolved it:
  My last major project was a LAM, or Large Action Model, workflow prediction pilot. One ambiguity was what the model’s output should mean in a workflow setting. At first, it looked like a simple next-action classification problem, but in real operations the “right” action is not always singular. I resolved this by treating the model as an assistive workflow system and evaluating top-k predictions, so it could recommend a ranked shortlist instead of pretending every case has one deterministic next step.

* **One tradeoff** you made and why:
  The main tradeoff was better-looking performance versus a more trustworthy evaluation setup. Row-level splits produced stronger metrics, but group-based splits tested whether the model could generalize to unseen workflow scenarios. I chose the stricter group-based setup because I would rather report a less flattering metric that tells the truth than a high score caused by an easy split.

* **One mistake** you made and what you changed:
  I initially explored structured features that pushed performance close to 1.0. After reviewing the feature logic, I realized some fields encoded routing or label-generation logic and were leaking the answer. I changed how I interpreted those results: instead of presenting them as semantic generalization, I reframed them as a rule-aware upper bound and treated the text/embedding-based setup as the honest benchmark.

* **One review comment** that made you change your mind:
  A review comment that changed my thinking was: “Don’t just optimize top-1 prediction. In real workflows, a ranked shortlist may be more useful than a single brittle answer.” That pushed me to evaluate top-k accuracy and think more practically about agent assist, fallback design, and human-in-the-loop workflows.

## Anything you'd improve about THIS challenge or our CLAUDE.md

I liked the two-stage structure because it tests whether a candidate can plan before coding. One improvement would be to add more multi-hop ambiguity: irrelevant provider evidence, stale contacts, reused phone numbers, misleading partial matches, and decoy generic inboxes. For `CLAUDE.md`, I would add a short “what good looks like” section: preserve uncertainty, write edge-case tests, avoid overfitting to mocks, document tradeoffs, and never hide weak evidence behind a confident answer.


<!-- # ABOUT.md (put this at the root of your submission repo)

Keep it short and concrete. We read this to understand how you think, not to grade your English.

## Why this role
<!-- 2-3 sentences. What about AI-native engineering / this problem interests you? -->

<!-- ## How you work with AI tools -->
<!-- Which tools, and HOW you direct them (not "I use AI" — show judgment: when you trust the model vs override it). -->

<!-- ## Your last project (structured — this is the pre-filter) -->
<!-- - **One ambiguity** you faced and how you resolved it:
- **One tradeoff** you made and why:
- **One mistake** you made and what you changed:
- **One review comment** that made you change your mind:

## Anything you'd improve about THIS challenge or our CLAUDE.md
<!-- Optional but a strong signal. -->