export function getPlacementDesignWidth(item) {
  return item?.kind === 'team' ? 560 : item?.kind === 'manager' ? 320 : 188
}

function getHierarchyBranchSize(item) {
  const children = item?.children || []
  const baseWidth = 220
  const baseHeight = 68

  if (!children.length) {
    return { width: baseWidth, height: baseHeight }
  }

  const childSizes = children.map((child) => getHierarchyBranchSize(child))
  const maxPerRow = 2
  const gapX = 12
  const gapY = 16
  const rows = []

  for (let index = 0; index < childSizes.length; index += maxPerRow) {
    rows.push(childSizes.slice(index, index + maxPerRow))
  }

  const childrenWidth = Math.max(
    ...rows.map((row) => row.reduce((sum, child) => sum + child.width, 0) + gapX * Math.max(0, row.length - 1)),
    0,
  )
  const childrenHeight =
    rows.reduce((sum, row) => sum + Math.max(...row.map((child) => child.height)), 0) +
    gapY * Math.max(0, rows.length - 1)

  return {
    width: Math.max(baseWidth, childrenWidth + 24),
    height: baseHeight + 32 + childrenHeight,
  }
}

export function getPlacementDesignHeight(item) {
  const children = item?.children || []
  const childCount = children.length

  if (item?.kind === 'team') {
    if (!childCount) return 176
    const hierarchy = children.map((child) => getHierarchyBranchSize(child))
    const tallestBranch = Math.max(...hierarchy.map((child) => child.height), 0)
    return 176 + tallestBranch + 32
  }

  if (item?.kind === 'manager') {
    if (!childCount) return 132
    const stackedChildrenHeight =
      children.reduce((sum, child) => sum + getPlacementDesignHeight(child), 0) + 12 * Math.max(0, childCount - 1)
    return 132 + 56 + stackedChildrenHeight
  }

  return 88
}

export function getPlacementBounds(
  items,
  { minWidth = 0, minHeight = 0, padding = 0 } = {},
) {
  if (!items?.length) {
    return {
      minX: 0,
      minY: 0,
      maxX: minWidth,
      maxY: minHeight,
      width: minWidth,
      height: minHeight,
      offsetX: 0,
      offsetY: 0,
    }
  }

  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity

  items.forEach((item) => {
    const x = Number(item.x || 0)
    const y = Number(item.y || 0)
    const width = getPlacementDesignWidth(item)
    const height = getPlacementDesignHeight(item)

    minX = Math.min(minX, x)
    minY = Math.min(minY, y)
    maxX = Math.max(maxX, x + width)
    maxY = Math.max(maxY, y + height)
  })

  const contentWidth = maxX - minX + padding * 2
  const contentHeight = maxY - minY + padding * 2
  const width = Math.max(minWidth, contentWidth)
  const height = Math.max(minHeight, contentHeight)
  const extraX = Math.max(0, width - contentWidth)
  const extraY = Math.max(0, height - contentHeight)

  return {
    minX,
    minY,
    maxX,
    maxY,
    width,
    height,
    offsetX: padding - minX + extraX / 2,
    offsetY: padding - minY + extraY / 2,
  }
}
