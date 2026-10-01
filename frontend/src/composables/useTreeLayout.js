export const NODE_W = 196
export const NODE_H = 92
export const X_GAP = 30
export const Y_GAP = 108
export const COUPLE_DROP = 22
export const ROW_H = NODE_H + Y_GAP

/** Extra space between separate family units in the same row. */
export const CLUSTER_GAP = 48

const SLOT_W = NODE_W + X_GAP
const BUS_BASE = 18
const BUS_LANE = 15
const ORDER_PASSES = 4

function pairKey(a, b) {
  return a <= b ? `${a},${b}` : `${b},${a}`
}

/**
 * A couple is either an explicitly recorded union, or two people who are father and mother of
 * the same child. Deriving the second kind means a marriage never has to be entered twice.
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

  const known = new Set(persons.map((p) => p.id))
  for (const person of persons) {
    const { father_id: father, mother_id: mother } = person
    if (father == null || mother == null) continue
    if (!known.has(father) || !known.has(mother)) continue
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

function mean(values) {
  const real = values.filter((value) => Number.isFinite(value))
  if (!real.length) return null
  return real.reduce((sum, value) => sum + value, 0) / real.length
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

  // A person's birth family, used to keep blood siblings together and to group separate
  // families apart on the row.
  const birthFamilyKey = (person) => {
    const ids = [person.father_id, person.mother_id]
      .filter((value) => value != null && byId.has(value))
      .sort((a, b) => a - b)
    return ids.length ? `p:${ids.join(',')}` : null
  }

  const clusterKeyOf = new Map()
  for (const person of persons) {
    const candidates = []
    const own = birthFamilyKey(person)
    if (own) candidates.push(own)
    for (const couple of couplesByPerson.get(person.id) || []) {
      const partner = byId.get(otherPartner(couple, person.id))
      if (partner) {
        const partnerKey = birthFamilyKey(partner)
        if (partnerKey) candidates.push(partnerKey)
      }
    }
    if (candidates.length) {
      // Marrying in joins the partner's family; the lowest key keeps both partners together.
      clusterKeyOf.set(person.id, [...candidates].sort()[0])
    } else if ((couplesByPerson.get(person.id) || []).length) {
      const couple = couplesByPerson.get(person.id)[0]
      clusterKeyOf.set(person.id, `c:${pairKey(couple.a, couple.b)}`)
    } else {
      clusterKeyOf.set(person.id, `s:${person.id}`)
    }
  }

  const gens = [...new Set(persons.map((p) => gen.get(p.id) ?? 0))].sort((a, b) => a - b)
  const rows = gens.map((g) => persons.filter((p) => (gen.get(p.id) ?? 0) === g))

  const membersByCluster = rows.map((row) => {
    const map = new Map()
    for (const person of row) {
      const key = clusterKeyOf.get(person.id)
      if (!map.has(key)) map.set(key, [])
      map.get(key).push(person)
    }
    return map
  })

  // Order within one family: blood members by birth, then spouses beside their partner.
  const layoutWithinCluster = (members, key) => {
    const blood = members
      .filter((person) => birthFamilyKey(person) === key)
      .sort((a, b) => birthValue(a) - birthValue(b) || a.id - b.id)
    const others = members
      .filter((person) => birthFamilyKey(person) !== key)
      .sort((a, b) => a.id - b.id)

    const order = [...blood]
    const placed = new Set(order.map((person) => person.id))
    const isPartner = (x, y) => x != null && y != null && pairKey(x, y) !== null && couples.some((c) => (c.a === x && c.b === y) || (c.a === y && c.b === x))

    for (const person of others) {
      let index = -1
      for (const couple of couplesByPerson.get(person.id) || []) {
        const partnerId = otherPartner(couple, person.id)
        if (partnerId != null && placed.has(partnerId)) {
          const partnerIdx = order.findIndex((q) => q.id === partnerId)
          if (partnerIdx >= 0) {
            index = partnerIdx + 1
            while (index < order.length && isPartner(order[index].id, partnerId)) index += 1
            break
          }
        }
      }
      if (index >= 0) order.splice(index, 0, person)
      else order.push(person)
      placed.add(person.id)
    }
    return order
  }

  const clusterOrder = rows.map((_, r) => [...membersByCluster[r].keys()])

  const centringPass = (row) => {
    const rowIndex = (pid) => row.findIndex((q) => q.id === pid)
    for (const person of [...row]) {
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
      row.splice(rowIndex(firstId), 1)
      row.splice(rowIndex(secondId), 1)
      const personIdx = rowIndex(person.id)
      row.splice(personIdx, 0, byId.get(firstId))
      row.splice(personIdx + 2, 0, byId.get(secondId))
    }
    return row
  }

  const buildRows = () =>
    rows.map((_, r) => {
      const members = membersByCluster[r]
      const row = []
      for (const key of clusterOrder[r]) {
        row.push(...layoutWithinCluster(members.get(key) || [], key))
      }
      return centringPass(row)
    })

  let order = buildRows()
  const indexMap = (row) => new Map(row.map((person, i) => [person.id, i]))

  const parentPositions = (person, above) => {
    const ids = [person.father_id, person.mother_id].filter((id) => id != null)
    return ids.map((id) => above.get(id)).filter((value) => value != null)
  }
  const childPositions = (person, below) =>
    persons
      .filter((other) => other.father_id === person.id || other.mother_id === person.id)
      .map((child) => below.get(child.id))
      .filter((value) => value != null)

  // Alternate passes: pull children under their parents, then parents over their children.
  // This is what stops one family's line being drawn across another family's children.
  for (let pass = 0; pass < ORDER_PASSES; pass += 1) {
    const index = order.map(indexMap)

    for (let r = 1; r < rows.length; r += 1) {
      const above = index[r - 1]
      const barycentre = new Map(
        clusterOrder[r].map((key) => [
          key,
          mean(
            (membersByCluster[r].get(key) || []).flatMap((person) => parentPositions(person, above)),
          ),
        ]),
      )
      clusterOrder[r] = [...clusterOrder[r]].sort(
        (a, b) => (barycentre.get(a) ?? Infinity) - (barycentre.get(b) ?? Infinity),
      )
    }

    for (let r = rows.length - 2; r >= 0; r -= 1) {
      const below = index[r + 1]
      const barycentre = new Map(
        clusterOrder[r].map((key) => [
          key,
          mean(
            (membersByCluster[r].get(key) || []).flatMap((person) =>
              childPositions(person, below),
            ),
          ),
        ]),
      )
      clusterOrder[r] = [...clusterOrder[r]].sort(
        (a, b) => (barycentre.get(a) ?? Infinity) - (barycentre.get(b) ?? Infinity),
      )
    }

    order = buildRows()
  }

  // --- positions -----------------------------------------------------------
  const rowWidths = order.map((row) => {
    let cursor = 0
    row.forEach((person, i) => {
      if (i > 0 && clusterKeyOf.get(person.id) !== clusterKeyOf.get(row[i - 1].id)) {
        cursor += CLUSTER_GAP
      }
      cursor += SLOT_W
    })
    return cursor ? cursor - X_GAP : 0
  })
  const maxWidth = Math.max(...rowWidths, 0)
  const height = (gens.length - 1) * ROW_H + NODE_H

  const nodes = []
  const position = new Map()
  order.forEach((row, r) => {
    const offset = (maxWidth - rowWidths[r]) / 2
    let cursor = offset
    row.forEach((person, i) => {
      if (i > 0 && clusterKeyOf.get(person.id) !== clusterKeyOf.get(row[i - 1].id)) {
        cursor += CLUSTER_GAP
      }
      position.set(person.id, { x: cursor, y: r * ROW_H })
      nodes.push({ person, x: cursor, y: r * ROW_H, gen: gens[r] })
      cursor += SLOT_W
    })
  })

  const centerX = (pid) => {
    const p = position.get(pid)
    return p ? p.x + NODE_W / 2 : null
  }

  // --- marriage lines ------------------------------------------------------
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

  // --- child connectors ----------------------------------------------------
  const childGroups = new Map()
  for (const person of persons) {
    const g = gen.get(person.id) ?? 0
    if (g === 0) continue
    const ids = [person.father_id, person.mother_id]
      .filter((value) => value != null)
      .sort((a, b) => a - b)
    if (!ids.length) continue
    const key = ids.join(',')
    if (!childGroups.has(key)) {
      childGroups.set(key, { key, parents: ids, children: [], sourceX: 0, sourceY: 0 })
    }
    childGroups.get(key).children.push(person)
  }

  const prepared = []
  for (const group of childGroups.values()) {
    const available = group.parents.filter((pid) => position.has(pid))
    if (!available.length) continue
    const parentPositionsInRow = available.map((pid) => position.get(pid))
    const parentBottom = Math.max(...parentPositionsInRow.map((p) => p.y + NODE_H))
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
    prepared.push({ ...group, sourceX, sourceY, parentBottom, children })
  }

  // Give every family its own horizontal level, so two families' lines never sit on top of
  // each other and read as one.
  prepared.sort((a, b) => a.sourceX - b.sourceX)
  const lanesByRow = new Map()
  const paths = []
  for (const group of prepared) {
    const parentRow = Math.round((group.sourceY - COUPLE_DROP - NODE_H) / ROW_H)
    const lane = lanesByRow.get(parentRow) ?? 0
    lanesByRow.set(parentRow, lane + 1)

    const childTop = Math.min(...group.children.map((c) => position.get(c.id).y))
    const busY = Math.min(group.sourceY + BUS_BASE + lane * BUS_LANE, childTop - 6)

    let d = `M ${group.sourceX} ${group.parentBottom} V ${busY}`
    for (const child of group.children) {
      d += ' ' + roundedBranch(group.sourceX, busY, centerX(child.id), position.get(child.id).y)
    }
    paths.push({ key: group.key, d })
  }

  return { nodes, coupleLinks, paths, width: maxWidth, height, generations: gens.length }
}
