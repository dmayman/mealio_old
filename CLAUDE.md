# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**For Mealio-specific technical patterns and architecture details, see PROJECT_PATTERNS.md.**

## 🚨 AUTOMATED CHECKS ARE MANDATORY
**ALL linting/testing issues are BLOCKING - EVERYTHING must be ✅ GREEN!**  
No errors. No formatting issues. No linting problems. Zero tolerance.  
These are not suggestions. Fix ALL issues before continuing.

## CRITICAL WORKFLOW - ALWAYS FOLLOW THIS!

### Research → Plan → Implement
**NEVER JUMP STRAIGHT TO CODING!** Always follow this sequence:
1. **Research**: Explore the codebase, understand existing patterns (check PROJECT_PATTERNS.md)
2. **Plan**: Create a detailed implementation plan and verify it with me  
3. **Implement**: Execute the plan with validation checkpoints

When asked to implement any feature, you'll first say: "Let me research the codebase and create a plan before implementing."

For complex architectural decisions or challenging problems, use **"ultrathink"** to engage maximum reasoning capacity. Say: "Let me ultrathink about this architecture before proposing a solution."

### Make sure you are in the right directory!
Do not make critical errors like installing packages in the wrong directory or deleting files in the wrong directory. Always double check your current directory before running commands.

### USE MULTIPLE AGENTS!
*Leverage subagents aggressively* for better results:

* Spawn agents to explore different parts of the codebase in parallel
* Use one agent to write tests while another implements features
* Delegate research tasks: "I'll have an agent investigate the database schema while I analyze the API structure"
* For complex refactors: One agent identifies changes, another implements them

Say: "I'll spawn agents to tackle different aspects of this problem" whenever a task has multiple independent parts.

### Reality Checkpoints
**Stop and validate** at these moments:
- After implementing a complete feature
- Before starting a new major component  
- When something feels wrong
- Before declaring "done"
- **WHEN LINTING/TESTS FAIL WITH ERRORS** ❌

Run appropriate checks:
- Python: `ruff format && ruff check && pytest`
- Next.js: `pnpm lint && pnpm type-check && pnpm test`
- Supabase: `supabase db push --dry-run`

> Why: You can lose track of what's actually working. These checkpoints prevent cascading failures.

## Working Memory Management

### When context gets long:
- Re-read this CLAUDE.md file
- Update PROGRESS.md with current status
- Document current state before major changes
- Reference PROJECT_PATTERNS.md for technical details

### ALWAYS Maintain These Working Files:

#### TODO.md:
```markdown
## Current Task
- [ ] What we're doing RIGHT NOW

## Completed  
- [x] What's actually done and tested

## Next Steps
- [ ] What comes next

## Blocked/Issues
- [ ] Items waiting on decisions or fixes
```

#### PROGRESS.md:
```markdown
## Current Session Summary
Brief overview of what we're working on

## Recent Achievements
- [Date] What was completed

## Current Status
Where we are right now

## Next Steps
What's planned next

## Open Questions
Items needing clarification or decisions
```

**Update these files frequently!** They help maintain context across long sessions.

## Implementation Standards

### FORBIDDEN - NEVER DO THESE:
- **NO** keeping old and new code together
- **NO** migration functions or compatibility layers  
- **NO** versioned function names (processV2, handleNew)
- **NO** TODOs in final code
- **NO** unused imports or variables
- **NO** console.log in production code

### Required Standards:
- **Delete** old code when replacing it
- **Meaningful names**: `user_id` not `id`, `recipe_data` not `data`
- **Early returns** to reduce nesting
- **Type hints** in Python functions
- **Proper error handling**: Use try/catch appropriately
- **Consistent formatting**: Use ruff for Python, prettier for JS/TS

### Our code is complete when:
- ✅ All linters pass with zero issues
- ✅ All tests pass  
- ✅ Feature works end-to-end
- ✅ Old code is deleted
- ✅ Proper type annotations (Python) / TypeScript types
- ✅ No unused imports or dead code
- ✅ TODO.md and PROGRESS.md updated

### Testing Strategy
- Complex business logic → Write tests first
- Simple CRUD → Write tests after  
- API endpoints → Test with realistic data
- Skip tests for simple utility functions

## Problem-Solving Together

When you're stuck or confused:
1. **Stop** - Don't spiral into complex solutions
2. **Delegate** - Consider spawning agents for parallel investigation
3. **Ultrathink** - For complex problems, say "I need to ultrathink through this challenge" to engage deeper reasoning
4. **Step back** - Re-read the requirements and check PROJECT_PATTERNS.md
5. **Simplify** - The simple solution is usually correct
6. **Ask** - "I see two approaches: [A] vs [B]. Which do you prefer?"

My insights on better approaches are valued - please ask for them!

## Communication Protocol

### Progress Updates:
```
✓ Implemented recipe parsing (all tests passing)
✓ Added household invitation system  
✗ Found issue with ingredient confidence scores - investigating
```

### Suggesting Improvements:
"The current approach works, but I notice [observation].
Would you like me to [specific improvement]?"

### When Learning New Patterns:
"I discovered [pattern/solution]. Should I document this in PROJECT_PATTERNS.md for future reference?"

## Working Together

- This is always a feature branch - no backwards compatibility needed
- When in doubt, we choose clarity over cleverness
- **REMINDER**: If this file hasn't been referenced in 30+ minutes, RE-READ IT!
- **UPDATE PROJECT_PATTERNS.md** when you learn new technical patterns
- **UPDATE PROGRESS.md** at major milestones

Avoid complex abstractions or "clever" code. The simple, obvious solution is probably better, and my guidance helps you stay focused on what matters.