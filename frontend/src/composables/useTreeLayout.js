export const NODE_W = 196
export const NODE_H = 92
export const X_GAP = 30
export const Y_GAP = 108
export const COUPLE_DROP = 22
export const ROW_H = NODE_H + Y_GAP

const SLOT_W = NODE_W + X_GAP

function generationMap(persons, unions) {
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
    for (const union of unions) {
      const { partner_a_id: a, partner_b_id: b } = union
      if (a != null && b != null && gen.has(a) && gen.has(b)) {
        const high = Math.max(gen.get(a), gen.get(b))
        if (gen.get(a) !== high) {
          gen.set(a, high)
          changed = true
        }
        if (gen.get(b) !== high) {
          gen.set(b, high)
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
  const gen = generationMap(persons, unions)

  const unionsByPerson = new Map()
  for (const union of unions) {
    for (const pid of [union.partner_a_id, union.partner_b_id]) {
      if (pid == null) continue
      if (!unionsByPerson.has(pid)) unionsByPerson.set(pid, [])
      unionsByPerson.get(pid).push(union)
    }
  }

  const otherPartner = (union, pid) =>
    union.partner_a_id === pid ? union.partner_b_id : union.partner_a_id

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

    const remaining = people
      .filter((person) => !placed.has(person.id))
      .sort((a, b) => a.id - b.id)

    for (const person of remaining) {
      if (placed.has(person.id)) continue
      placed.add(person.id)
      let index = -1
      for (const union of unionsByPerson.get(person.id) || []) {
        const partnerId = otherPartner(union, person.id)
        if (partnerId != null && placed.has(partnerId)) {
          const partnerIdx = order.findIndex((q) => q.id === partnerId)
          if (partnerIdx >= 0) {
            index = partnerIdx + 1
            while (index < order.length) {
              const candidate = order[index]
              const sharesSpouse = (unionsByPerson.get(candidate.id) || []).some(
                (u) => otherPartner(u, candidate.id) === partnerId,
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

  // Marriage bars are drawn just below the row, so a spouse who is not adjacent
  // (a second marriage) never has its line drawn across another person's card,
  // and the year label always has clear space to sit in.
  const coupleLinks = []
  const coupleByKey = new Map()
  for (const union of unions) {
    const a = position.get(union.partner_a_id)
    const b = union.partner_b_id != null ? position.get(union.partner_b_id) : null
    if (!a || !b || a.y !== b.y) continue
    const ax = a.x + NODE_W / 2
    const bx = b.x + NODE_W / 2
    const rowBottom = a.y + NODE_H
    const y = rowBottom + COUPLE_DROP
    const d = `M ${ax} ${rowBottom} V ${y} M ${bx} ${rowBottom} V ${y} M ${ax} ${y} H ${bx}`
    coupleLinks.push({
      id: union.id,
      status: union.status,
      start_date: union.start_date,
      d,
      y,
      midX: (ax + bx) / 2,
    })
    const key = [union.partner_a_id, union.partner_b_id].sort((m, n) => m - n).join(',')
    coupleByKey.set(key, y)
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
    const sourceY = coupleByKey.get([...available].sort((m, n) => m - n).join(',')) ?? parentBottom

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
