# Preferred Style

Use this reference when the user wants diagrams to resemble the approved examples provided in this thread.

## What the approved examples have in common

- They are simple first and complete second.
- The reader can see the main actor immediately.
- The main use cases form a clear vertical backbone.
- Included or extending use cases sit close to the related base use case instead of floating far away.
- The system boundary is obvious and not overloaded.
- The diagram is readable even before the reader studies the labels.

## Preferred visual structure

Prefer this arrangement:
- primary actor on the left
- optional secondary actor on the right
- main use cases in one vertical column
- secondary support use cases in a nearby side column
- generalization stacked vertically
- mostly horizontal actor links and short dashed dependency links

## Preferred visual tone

- Use a light background.
- Use one restrained accent color family, ideally pale blue or another soft neutral.
- Keep line thickness light and consistent.
- Avoid dark themes unless the user explicitly asks for them.
- Avoid too many different fill colors in the final submission.

## Preferred level of detail

- Keep only the use cases needed to explain the scenario and required UML relations.
- Use extension points only when they materially clarify the `extend` relation.
- If the diagram is for final submission, remove teaching annotations such as red arrows naming `Actor`, `Association`, or `Extension Point`.
- If the diagram is for study or explanation, those annotations are acceptable as a temporary teaching layer.

## Preferred composition patterns from the examples

### Pattern 1: Vertical backbone with side support cases

Use when one actor drives several core actions and a few support actions.

Structure:
- actor on the left
- 3 to 5 main use cases stacked vertically near the center-left
- included or extending use cases in a short right-hand column

### Pattern 2: Many actions sharing one included use case

Use when several core actions all require one mandatory prerequisite, such as `Login`.

Structure:
- main actions stacked on the left inside the system
- one shared included use case near the center-right
- optional failure handling or abort handling close to that shared use case

### Pattern 3: Repeated `extend` examples for teaching

Use only when the goal is to demonstrate `extend` repeatedly.

Structure:
- base use cases in one column
- one optional extension next to each base use case
- keep actors and other relations sparse so the repeated extend pattern remains readable

## What to avoid if matching this style

- centered bubble clouds with no visual hierarchy
- long dashed arrows running across the entire boundary
- too many actors on both sides unless the scenario truly needs them
- mixing explanation markup and final submission markup in the same deliverable
- over-engineering the diagram just because more space is available
