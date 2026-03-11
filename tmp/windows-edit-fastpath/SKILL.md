---
name: "windows-edit-fastpath"
description: "Speed up file creation and edits in Windows sandboxed workspaces by avoiding repeated rejected patch attempts. Use when Codex is about to scaffold or update multiple files, write into paths outside writable roots such as .codex/skills, create or update a skill, or recover from a rejected edit and needs a stage-validate-copy workflow."
---

# Windows Edit Fastpath

Reduce rejected edit attempts by changing strategy early instead of retrying the same patch.

## Core Rules

1. Classify the target path before editing.
   - Edit directly only when the destination is inside the writable workspace.
   - Stage the result inside the current workspace first when the final destination is outside writable roots.
2. Prefer generators and existing scripts before hand-written multi-file patches.
   - Use scaffolding, validators, and regenerators when they already produce the required structure.
   - Hand-write only the smallest set of files that the task still needs.
3. Keep patches small and path-stable.
   - Use workspace-relative paths in patch headers.
   - Create parent directories before adding files.
   - Patch one file at a time unless the change is trivial and tightly coupled.
4. Treat the first rejection as a signal to change strategy.
   - Re-read the exact file or directory state.
   - Fix the path, context, or patch shape.
   - Do not repeat the same patch more than once.
5. Validate before moving files out of the workspace.
   - Run the smallest validator that proves the staged result is structurally sound.
   - Request one escalated copy or move only after the staged result is ready.

## Fast Workflow

1. Inspect writable roots, current directory, and target path.
2. Create a staging folder under the current workspace when the final destination is outside it.
3. Generate or patch files in small increments.
4. Validate the staged result.
5. Install or copy once.

## Skill Creation Shortcut

When creating another skill:

1. Read the creator instructions only as needed.
2. Scaffold in the workspace, not directly in `.codex/skills`.
3. Generate `agents/openai.yaml` from the final skill content when tooling exists; otherwise write a minimal valid file manually.
4. Copy the finished skill to the user skills directory in one step.

## Ask Only When Needed

Pause and ask the user only when the final destination is ambiguous, a required external asset is missing, or validation exposes a real content issue instead of a path issue.
