---
name: "use-case-diagrams"
description: "Create, refine, or review UML use case diagrams that must follow standard notation and assignment-specific constraints. Use when the user asks for a use case diagram, wants help choosing actors, use cases, system boundaries, or relations such as include, extend, and inheritance, or needs diagram source that can be edited later."
---

# Use Case Diagrams

Create diagrams that stay semantically correct before trying to satisfy diagram-count requirements.

Read [references/student-assignment.md](references/student-assignment.md) when the task matches the user's school assignment or similar coursework.

Read [references/use-case-rules.md](references/use-case-rules.md) when you need a compact reminder of notation, relation semantics, arrow direction, or review checks.

Read [references/relationship-drill.md](references/relationship-drill.md) when the task specifically depends on getting `<<include>>`, `<<extend>>`, generalization, or layout clarity right.

Read [references/layout-style.md](references/layout-style.md) when the task is to produce a cleaner-looking diagram, reduce clutter, or generate PlantUML that should render neatly on the first pass.

Read [references/preferred-style.md](references/preferred-style.md) when the user shares example diagrams and wants future outputs to match that style.

Read [references/anti-patterns.md](references/anti-patterns.md) when the user shares bad examples or when the diagram starts to look crowded, confusing, or semantically suspicious.

## Workflow

1. Identify the system being modeled, the system boundary name, the actors, and the requested output format.
2. Ask briefly for the domain or system name if the user gave only structural requirements and there is no safe way to infer the subject of the diagram.
3. List actors as external roles that interact with the system. Do not model internal modules, screens, or databases as actors unless the task explicitly treats them as external systems.
4. Write use cases as short goal-oriented verb phrases at a similar level of abstraction.
5. Keep the first candidate diagram small. Prefer roughly 6 to 8 use cases unless the user or domain clearly needs more.
6. Build the composition before drawing relations: choose one main actor on the left, at most one secondary actor group on the right, a central column of main use cases, included use cases in a nearby side column, extending use cases close to the base use case they modify, and specialized actors or use cases below their parent.
7. Use hidden layout links or column groupings in PlantUML when needed to keep the diagram stable and readable. Use them only for layout, not semantics.
8. Connect actors directly to the use cases they initiate or participate in. Avoid duplicating associations when actor generalization communicates the same meaning more clearly.
9. Use `include` only when the base use case always performs the included behavior. Draw a dashed dependency arrow from the base use case to the included use case and label it `<<include>>`.
10. Use `extend` only when additional behavior is optional, conditional, or exceptional. Draw a dashed dependency arrow from the extending use case to the extended base use case and label it `<<extend>>`. Use extension points only when they actually clarify where the optional behavior plugs in.
11. Use generalization only for a true specialization. Draw a solid line with a hollow triangle pointing to the parent actor or parent use case.
12. Prefer actor generalization over use-case generalization when the specialization is mainly about user roles. Use use-case generalization only when one goal is genuinely a specialized form of another goal.
13. If the diagram still needs long crisscrossing lines, change the selected use cases or the placement before adding more notation.
14. Run the anti-pattern check: too many actor associations, too many dashed arrows, invalid stereotypes, mixed abstraction, or internal implementation details pretending to be actors.
15. Check the final diagram for minimal crossing lines, clear labels, and a defensible rationale for every relation.

## Output Pattern

When creating a diagram from scratch, structure the answer in this order unless the user asks for something else:

1. State assumptions only when needed.
2. List actors.
3. List use cases.
4. Explain `include`, `extend`, and inheritance choices in one short sentence each.
5. Provide editable diagram source.

Default to PlantUML for editable source unless the user explicitly asks for another format or tool.
Default to the clean layout preset in [references/layout-style.md](references/layout-style.md) instead of ad hoc styling.
For final deliverables, omit tutorial arrows, red explanatory labels, and other teaching annotations unless the user explicitly asks for a study version.

## Quality Bar

- Keep the diagram at user-goal level, not UI click level.
- Avoid relations added only to satisfy a checklist if the semantics are wrong.
- Use the standard UML stereotype `<<extend>>` in outputs. Do not output misspellings such as `<<extends>>`, `<<extentds>>`, or invented labels such as `<<exclude>>`.
- If the assignment requires a relation that the chosen domain does not support naturally, say so and propose the closest valid redesign.
- Prefer fewer, clearer actors over role duplicates with nearly identical links.
- Prefer fewer bubbles and fewer crossings over exhaustive decomposition.
- If one actor needs more than about 4 direct associations in a student diagram, raise the abstraction or reduce scope before drawing.
- If more than two dashed relations cross each other, redesign the diagram instead of forcing it through.
- Keep names consistent across explanation and diagram source.
