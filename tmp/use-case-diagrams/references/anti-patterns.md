# Anti-Patterns

Use this reference when the user shares bad examples or when a draft diagram starts to feel crowded, confusing, or amateur.

## 1. Starburst actor

Symptom:
- One actor on the side connects diagonally to many use cases across the whole system boundary.

Why it is bad:
- The actor becomes the main visual object instead of the user goals.
- The diagram turns into a fan of lines before the reader can see structure.

Fix:
- Raise the abstraction and keep fewer core use cases.
- Split the scenario into a smaller diagram if needed.
- Use actor generalization only when it is semantically true, not as a cosmetic trick.

## 2. Support use cases floating too far away

Symptom:
- Included or extending use cases sit far from the base use case, forcing long dashed arrows.

Why it is bad:
- Dashed relations become the dominant visual pattern.
- The reader loses the main story.

Fix:
- Move support use cases next to the base use case.
- Create a side support column instead of scattering them.

## 3. Mixed abstraction levels

Symptom:
- High-level goals, low-level technical actions, errors, and admin maintenance tasks all appear in one small diagram.

Why it is bad:
- The diagram stops describing user goals and starts describing implementation noise.

Fix:
- Keep one abstraction level per diagram.
- Replace low-level steps with a higher-level goal or move them into another diagram.

## 4. Invalid or invented stereotypes

Symptom:
- Labels such as `<<exclude>>` or other made-up relation names appear.

Why it is bad:
- The diagram is no longer standard UML.
- The reader cannot trust the semantics.

Fix:
- Use only valid relations such as association, `<<include>>`, `<<extend>>`, and generalization.
- If the intended meaning is conflict or invalid input handling, model it as an extension, alternative flow, or textual note outside the diagram.

## 5. Internal components acting as pseudo-actors

Symptom:
- Databases or internal modules are shown as actors without a clear reason.

Why it is bad:
- The system boundary becomes conceptually blurry.
- The diagram mixes architectural structure with user goals.

Fix:
- Use actors only for external roles or genuinely external systems.
- Keep internal implementation details out of a normal use case diagram.

## 6. Narrow boundary, too many bubbles

Symptom:
- The system rectangle is crowded with many ovals, leaving almost no whitespace.

Why it is bad:
- Readability collapses even when the semantics might be correct.

Fix:
- Reduce the number of use cases.
- Widen the layout.
- Split into multiple diagrams if the scenario truly needs more scope.

## 7. Decorative complexity

Symptom:
- The diagram keeps adding more bubbles, colors, and arrows without making the use case story clearer.

Why it is bad:
- It looks busy instead of informative.

Fix:
- Remove any use case or relation that does not help explain the main user goals or assignment-required relations.

## 8. Fake use-case shapes

Symptom:
- Use cases render as rounded rectangles, cards, capsules, or generic boxes instead of ellipses.

Why it is bad:
- The diagram stops looking like a proper UML use case diagram.
- The reader immediately sees the notation is wrong.

Fix:
- Use a renderer and source format that preserve ellipse use-case shapes.
- Reject the render and rerender if the shape is wrong.

## Final rejection test

Reject or redesign the draft if any of these are true:
- one actor dominates with a starburst of lines
- more than two dashed relations cross each other
- the reader cannot identify the main scenario in three seconds
- the diagram uses invented stereotypes
- the diagram mixes user goals with obvious implementation internals
- the use cases are not rendered as ellipses
