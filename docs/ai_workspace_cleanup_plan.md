# AI Workspace Organization Plan

This plan outlines a strategy to clean up the root directories of your projects and your main GitHub folder by centralizing AI-related settings, memory files, and session logs.

## User Review Required

> [!WARNING]
> Some AI tools (like Claude Desktop, RooCode/Cline, or Cursor) hardcode the paths they look for certain files (e.g., `.cursorrules`, `.clinerules`, or the `.claude` workspace folder). Moving these might break their functionality unless they can be configured to look elsewhere.
> 
> Please review the proposed folder structure below and confirm if you are okay with potentially having to update settings in your extensions to point to the new paths, or if we should use symbolic links (symlinks) to keep the tools happy while keeping the physical files organized.

## Open Questions

> [!IMPORTANT]
> 1. **Global Folders**: You have `.claude` and `.superpowers` in `C:\Users\drewb\Documents\GitHub\`. `.claude` contains VS Code-like `settings.json` for Claude plugins. Do you want to move these into a centralized global folder (e.g., `GitHub/.ai-workspace`), or leave them at the root to avoid breaking the Claude extension?
> 2. **Symlinks**: For files that *must* be at the root (like `.agentrules` or `.clinerules` for certain extensions), would you prefer we move the real file into the organized folder and leave a shortcut/symlink at the root, or just leave those specific files at the root?
> 3. **The Folder Name**: I propose `.ai/` as the standard folder name for each project. Does that work for you?

## Proposed Changes

### 1. Per-Project Cleanup (The `.ai` Directory)
For every project (e.g., `apps/uhaul-load-planner`, `apps/daily-planner`), we will create a dedicated `.ai/` directory and move the scattered files inside it:

#### [MODIFY] [apps/uhaul-load-planner/.ai/](file:///C:/Users/drewb/Documents/GitHub/apps/uhaul-load-planner/.ai/)
- Move `SESSION_LOG.md` -> `.ai/SESSION_LOG.md`
- Move `.agentrules` -> `.ai/.agentrules` (or leave at root if required by extension)
- Move `.memory` (if any exist) -> `.ai/.memory`
- Consolidate AI tool folders (like `.gemini`, `.claude` inside the project) into `.ai/` if the tools support custom paths.

### 2. Global Workspace Cleanup (`C:\Users\drewb\Documents\GitHub\`)
If you approve, we can create a `C:\Users\drewb\Documents\GitHub\.ai-global\` folder to house:
- `.superpowers`
- `.claude` (if it can be safely moved)
- Global agent memories or notes.

### 3. Update GitIgnores
#### [MODIFY] [.gitignore](file:///C:/Users/drewb/Documents/GitHub/apps/uhaul-load-planner/.gitignore)
Update project `.gitignore` files to properly manage the `.ai/` directory:
```gitignore
# Ignore AI logs and ephemeral memory
.ai/SESSION_LOG.md
.ai/.memory

# But DO track agent rules and instructions
!.ai/.agentrules
```

## Verification Plan
1. Manually move the files in `uhaul-load-planner` as a test case.
2. Update the `.gitignore`.
3. Verify that the AI tools (like me, or your Claude extension) can still read the rules and write to the logs in the new location.
4. If successful, apply the same structure to the rest of the projects in the `apps/` and `agents/` directories using a script.
