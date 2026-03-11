# Relationship Drill

Use this reference when relation choice, arrow direction, or readability is the main risk.

## Quick drill

### 1. `<<include>>`

Use `include` when a base use case always invokes another use case as required reusable behavior.

Checklist:
- The base use case is not complete without the included behavior.
- The included behavior is worth factoring out because it is reused or must stay explicit.
- The relation can be explained as `A always includes B`.

Drawing:
- Dashed dependency line.
- Open arrow points to the included use case.
- Label the dependency `<<include>>`.

Typical example:
- `Borrow Book` includes `Check Fine`.
- If checking fines happens every time a book is borrowed, the relation is valid.

Anti-example:
- `Borrow Book` extends `Check Fine` is wrong if checking fines is always required.

### 2. `<<extend>>`

Use `extend` when one use case adds optional, conditional, or exceptional behavior to another use case that can stand on its own.

Checklist:
- The base use case is meaningful even without the extra behavior.
- The extra behavior occurs only in some situations.
- The relation can be explained as `B extends A when condition X holds`.

Drawing:
- Dashed dependency line.
- Open arrow points to the extended base use case.
- Label the dependency `<<extend>>`.
- Show an extension point inside the base use case only when it improves understanding.

Typical example:
- `Apply Discount` extends `Checkout` when the customer enters a valid coupon.

Anti-example:
- If the extra step always happens, use `include`, not `extend`.

### 3. Generalization

Use generalization when a child actor or child use case is a true specialized form of a parent.

Checklist:
- The child has the meaning of the parent plus something more specific.
- Replacing the child with the parent still makes semantic sense.
- The relation can be explained as `Child is a kind of Parent`.

Drawing:
- Solid line.
- Hollow triangle points to the parent.

Typical actor example:
- `Premium Customer` generalizes `Customer`.

Typical use-case example:
- `Search by Author` and `Search by ISBN` generalize `Search Catalog`.

Anti-example:
- Do not use generalization just to avoid drawing two associations.

## Readability rules

- Prefer one main actor per side instead of scattering actors around the boundary.
- Keep included use cases near the center or slightly below the base use cases that reuse them.
- Keep extending use cases close to the base use case they modify so the dashed arrow stays short.
- Put child actors or child use cases below their parent when possible; the triangle should point upward or inward consistently.
- Prefer 6 to 8 use cases for student assignments unless the subject genuinely needs more.
- Remove decorative decomposition. If a use case is not helping the reader understand user goals or required relations, leave it out.

## Selection preference

When several valid designs exist, prefer the one with:
- fewer bubbles
- fewer dashed arrows
- shorter relation lines
- clearer actor responsibilities
- one obvious main scenario
