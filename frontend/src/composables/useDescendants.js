/**
 * Everything at or below a person: themselves, their partners, and all of their descendants
 * (with each descendant's partner included so couples sit side by side). Used for the
 * "family tree from here" view on a profile.
 *
 * Partners are taken from recorded unions *and* from shared children, so a couple shows up
 * even when the marriage was never entered as a separate record.
 */
export function descendantSubset(rootId, persons, unions) {
  const id = Number(rootId)
  const byId = new Map(persons.map((p) => [p.id, p]))
  if (!byId.has(id)) return { persons: [], unions: [] }

  const descendants = new Set([id])
  let grew = true
  while (grew) {
    grew = false
    for (const person of persons) {
      if (descendants.has(person.id)) continue
      const fromFather = person.father_id != null && descendants.has(person.father_id)
      const fromMother = person.mother_id != null && descendants.has(person.mother_id)
      if (fromFather || fromMother) {
        descendants.add(person.id)
        grew = true
      }
    }
  }

  const partnersOf = new Map()
  const link = (a, b) => {
    if (a == null || b == null) return
    if (!partnersOf.has(a)) partnersOf.set(a, new Set())
    if (!partnersOf.has(b)) partnersOf.set(b, new Set())
    partnersOf.get(a).add(b)
    partnersOf.get(b).add(a)
  }
  for (const union of unions) link(union.partner_a_id, union.partner_b_id)
  for (const person of persons) link(person.father_id, person.mother_id)

  const keep = new Set(descendants)
  for (const personId of descendants) {
    for (const partnerId of partnersOf.get(personId) || []) keep.add(partnerId)
  }

  return {
    persons: persons.filter((person) => keep.has(person.id)),
    unions: unions.filter(
      (union) =>
        union.partner_b_id != null &&
        keep.has(union.partner_a_id) &&
        keep.has(union.partner_b_id),
    ),
  }
}
