export const NODE_W = 196
export const NODE_H = 92
export const X_GAP = 30
export const Y_GAP = 108
export const COUPLE_DROP = 22
export const ROW_H = NODE_H + Y_GAP

const SLOT_W = NODE_W + X_GAP

function pairKey(a, b) {
  return a <= b ? `${a},${b}` : `${b},${a}`
}

/**
 * A couple is either an explicitly recorded union, or two people who are father and
 * mother of the same child. Deriving the second kind means a marriage never has to be
 * entered twice: recording both parents of a child is enough to draw the couple.
 */
function effectiveCouples(persons, unions) {
  const couples = new Map()

  for (const union of unions) {
    if (union.partner_a_id == null || union.partner_b_id == null) continue
    couples.set(pairKey(union.partner_a_id, union.partner_b_id), {
      id: `union-${union.id}`,
      a: union.partner_a_id,
      b: union.partner_b_id,
      recorded: true,
      status: union.status,
      start_date: union.start_date,
    })
  }

  for (const person of persons) {
    const { father_id: father, mother_id: mother } = person
    if (father == null || mother == null) continue
    const key = pairKey(father, mother)
    if (!couples.has(key)) {
      couples.set(key, { id: `derived-${key}`, a: father, b: mother, recorded: false })
    }
  }

  return [...couples.values()]
}

function generationMap(persons, couples) {
  const byId = new Map(persons.map((p) => [p.id, p]))
  const gen = new Map(persons.map((p) => [p.id, 0]))

  const raw = (pid, stack) => {
    const person = byId.get(pid)
    if (!person || stack.has(pid)) return 0
    const parents = [person.father_id, person.mother_id].filter(
      (value) => value != null && byId.has(value),
    )
    if (!parents.length) return 0
    const next = new Set(stack)
    next.add(pid)
    return Math.max(...parents.map((value) => raw(value, next))) + 1
  }

  for (const person of persons) gen.set(person.id, raw(person.id, new Set()))

  for (let pass = 0; pass < 12; pass += 1) {
    let changed = false
    for (const couple of couples) {
      if (gen.has(couple.a) && gen.has(couple.b)) {
        const high = Math.max(gen.get(couple.a), gen.get(couple.b))
        if (gen.get(couple.a) !== high) {
          gen.set(couple.a, high)
          changed = true
        }
        if (gen.get(couple.b) !== high) {
          gen.set(couple.b, high)
          changed = true
        }
      }
    }
    for (const person of persons) {
      const parents = [person.father_id, person.mother_id].filter(
        (value) => value != null && gen.has(value),
      )
      if (parents.length) {
        const want = Math.max(...parents.map((value) => gen.get(value))) + 1
        if (gen.get(person.id) < want) {
          gen.set(person.id, want)
          changed = true
        }
      }
    }
    if (!changed) break
  }

  return gen
}

function parentKey(person) {
  const ids = [person.father_id, person.mother_id]
    .filter((value) => value != null)
    .sort((a, b) => a - b)
  return ids.length ? ids.join(',') : null
}

function birthValue(person) {
  const match = String(person.birth_date || '').match(/\d{4}/)
  return match ? Number(match[0]) : Number.MAX_SAFE_INTEGER
}

function roundedBranch(sx, busY, cx, cy) {
  const dist = Math.abs(cx - sx)
  if (dist < 2) return `M ${sx} ${busY} V ${cy}`
  const dir = cx > sx ? 1 : -1
  const r = Math.min(12, dist / 2, Math.max(0, (cy - busY) / 2))
  if (r < 1) return `M ${sx} ${busY} H ${cx} V ${cy}`
  return `M ${sx} ${busY} H ${cx - dir * r} Q ${cx} ${busY} ${cx} ${busY + r} V ${cy}`
}

export function computeLayout(persons, unions) {
  if (!persons.length) {
    return { nodes: [], coupleLinks: [], paths: [], width: 0, height: 0, generations: 0 }
  }

  const byId = new Map(persons.map((p) => [p.id, p]))
  const couples = effectiveCouples(persons, unions)
  const gen = generationMap(persons, couples)

  const couplesByPerson = new Map()
  for (const couple of couples) {
    for (const pid of [couple.a, couple.b]) {
      if (!couplesByPerson.has(pid)) couplesByPerson.set(pid, [])
      couplesByPerson.get(pid).push(couple)
    }
  }

  const otherPartner = (couple, pid) => (couple.a === pid ? couple.b : couple.a)

  const byGen = new Map()
  for (const person of persons) {
    const g = gen.get(person.id) ?? 0
    if (!byGen.has(g)) byGen.set(g, [])
    byGen.get(g).push(person)
  }

  const gens = [...byGen.keys()].sort((a, b) => a - b)
  const colIndex = new Map()

  for (const g of gens) {
    const people = byGen.get(g)
    const placed = new Set()
    const order = []

    const groups = new Map()
    for (const person of people) {
      const key = parentKey(person)
      if (!key) continue
      if (!groups.has(key)) groups.set(key, { key, anchor: Infinity, members: [] })
      const parentIds = key.split(',').map(Number)
      const xs = parentIds.map((pid) => colIndex.get(pid)).filter((value) => value != null)
      groups.get(key).anchor = Math.min(
        groups.get(key).anchor,
        xs.length ? xs.reduce((sum, v) => sum + v, 0) / xs.length : Infinity,
      )
      groups.get(key).members.push(person)
    }

    const orderedGroups = [...groups.values()].sort((a, b) => a.anchor - b.anchor)
    for (const group of orderedGroups) {
      group.members.sort((a, b) => birthValue(a) - birthValue(b) || a.id - b.id)
      for (const member of group.members) {
        placed.add(member.id)
        order.push(member)
      }
    }

    // Pull partners (recorded or derived from their children) next to each other, which is
    // what lets a marriage line sit between them and the children drop from its middle.
    const remaining = people
      .filter((person) => !placed.has(person.id))
      .sort((a, b) => a.id - b.id)

    for (const person of remaining) {
      if (placed.has(person.id)) continue
      placed.add(person.id)
      let index = -1
      for (const couple of couplesByPerson.get(person.id) || []) {
        const partnerId = otherPartner(couple, person.id)
        if (partnerId != null && placed.has(partnerId)) {
          const partnerIdx = order.findIndex((q) => q.id === partnerId)
          if (partnerIdx >= 0) {
            index = partnerIdx + 1
            while (index < order.length) {
              const candidate = order[index]
              const sharesSpouse = (couplesByPerson.get(candidate.id) || []).some(
                (c) => otherPartner(c, candidate.id) === partnerId,
              )
              if (!sharesSpouse) break
              index += 1
            }
            break
          }
        }
      }
      if (index >= 0) order.splice(index, 0, person)
      else order.push(person)
    }

    // Partners can still end up apart when both have parents of their own, because the
    // grouping pass above placed each under their own family. Move the partner from the
    // smaller sibling group next to the other, so the marriage line has somewhere to sit.
    const partnerKeys = new Set(couples.map((couple) => pairKey(couple.a, couple.b)))
    const rowIndex = (pid) => order.findIndex((q) => q.id === pid)
    const adjacentPartners = (pid) =>
      (couplesByPerson.get(pid) || []).filter((couple) => {
        const other = rowIndex(otherPartner(couple, pid))
        const self = rowIndex(pid)
        return other >= 0 && self >= 0 && Math.abs(other - self) === 1
      }).length

    const groupSize = new Map()
    for (const group of orderedGroups) {
      for (const member of group.members) groupSize.set(member.id, group.members.length)
    }

    for (const couple of couples) {
      const indexA = rowIndex(couple.a)
      const indexB = rowIndex(couple.b)
      if (indexA < 0 || indexB < 0 || Math.abs(indexA - indexB) === 1) continue

      // Never drag someone away from a partner they already sit beside.
      const countA = adjacentPartners(couple.a)
      const countB = adjacentPartners(couple.b)
      let moveId
      if (countA !== countB) moveId = countA < countB ? couple.a : couple.b
      else {
        const sizeA = groupSize.get(couple.a) ?? Number.MAX_SAFE_INTEGER
        const sizeB = groupSize.get(couple.b) ?? Number.MAX_SAFE_INTEGER
        moveId = sizeA <= sizeB ? couple.a : couple.b
      }
      const anchorId = moveId === couple.a ? couple.b : couple.a

      const [moved] = order.splice(rowIndex(moveId), 1)
      let index = rowIndex(anchorId) + 1
      while (index < order.length && partnerKeys.has(pairKey(order[index].id, anchorId))) {
        index += 1
      }
      order.splice(index, 0, moved)
    }

    // With two partners, put the person between them (partner - person - partner) so both
    // marriage lines touch them instead of one line reaching across the other spouse.
    for (const person of people) {
      const partnerIds = (couplesByPerson.get(person.id) || [])
        .map((couple) => otherPartner(couple, person.id))
        .filter((pid) => pid != null && rowIndex(pid) >= 0)
      if (partnerIds.length !== 2) continue
      const [firstId, secondId] = partnerIds
      const selfIdx = rowIndex(person.id)
      if (
        Math.abs(rowIndex(firstId) - selfIdx) === 1 &&
        Math.abs(rowIndex(secondId) - selfIdx) === 1
      ) {
        continue
      }
      order.splice(rowIndex(firstId), 1)
      order.splice(rowIndex(secondId), 1)
      const personIdx = rowIndex(person.id)
      order.splice(personIdx, 0, byId.get(firstId))
      order.splice(personIdx + 2, 0, byId.get(secondId))
    }

    order.forEach((person, i) => colIndex.set(person.id, i))
  }

  const rowWidth = (count) => (count ? (count - 1) * SLOT_W + NODE_W : 0)
  const maxWidth = Math.max(...gens.map((g) => rowWidth(byGen.get(g).length)))
  const height = (gens.length - 1) * ROW_H + NODE_H

  const nodes = []
  const position = new Map()
  for (const g of gens) {
    const people = byGen.get(g)
    const offset = (maxWidth - rowWidth(people.length)) / 2
    for (const person of people) {
      const x = offset + colIndex.get(person.id) * SLOT_W
      const y = g * ROW_H
      position.set(person.id, { x, y })
      nodes.push({ person, x, y, gen: g })
    }
  }

  const centerX = (pid) => {
    const p = position.get(pid)
    return p ? p.x + NODE_W / 2 : null
  }

  const coupleLinks = []
  const coupleBarY = new Map()
  for (const couple of couples) {
    const a = position.get(couple.a)
    const b = position.get(couple.b)
    if (!a || !b || a.y !== b.y) continue
    const ax = a.x + NODE_W / 2
    const bx = b.x + NODE_W / 2
    const rowBottom = a.y + NODE_H
    const y = rowBottom + COUPLE_DROP
    coupleLinks.push({
      id: couple.id,
      recorded: couple.recorded,
      status: couple.status,
      start_date: couple.start_date,
      d: `M ${ax} ${rowBottom} V ${y} M ${bx} ${rowBottom} V ${y} M ${ax} ${y} H ${bx}`,
      y,
      midX: (ax + bx) / 2,
    })
    coupleBarY.set(pairKey(couple.a, couple.b), y)
  }

  const childGroups = new Map()
  for (const person of persons) {
    const g = gen.get(person.id) ?? 0
    if (g === 0) continue
    const key = parentKey(person)
    if (!key) continue
    if (!childGroups.has(key)) {
      childGroups.set(key, { key, parents: key.split(',').map(Number), children: [] })
    }
    childGroups.get(key).children.push(person)
  }

  const paths = []
  for (const group of childGroups.values()) {
    const available = group.parents.filter((pid) => position.has(pid))
    if (!available.length) continue
    const parentPositions = available.map((pid) => position.get(pid))
    const parentBottom = Math.max(...parentPositions.map((p) => p.y + NODE_H))
    const sourceX =
      available.map((pid) => centerX(pid)).reduce((sum, v) => sum + v, 0) / available.length
    const sourceY =
      (available.length === 2 ? coupleBarY.get(pairKey(available[0], available[1])) : null) ??
      parentBottom

    const children = group.children.filter((child) => {
      const childPos = position.get(child.id)
      return childPos && childPos.y > sourceY
    })
    if (!children.length) continue

    const childTop = Math.min(...children.map((c) => position.get(c.id).y))
    const busY = sourceY + Math.max(14, (childTop - sourceY) * 0.5)

    let d = `M ${sourceX} ${sourceY} V ${busY}`
    for (const child of children) {
      d += ' ' + roundedBranch(sourceX, busY, centerX(child.id), position.get(child.id).y)
    }
    paths.push({ key: group.key, d })
  }

  return { nodes, coupleLinks, paths, width: maxWidth, height, generations: gens.length }
}
