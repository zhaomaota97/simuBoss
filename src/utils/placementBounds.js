export function getPlacementDesignWidth(item) {
  return item?.kind === 'team' ? 304 : item?.kind === 'manager' ? 260 : 188
}

export function getPlacementDesignHeight(item) {
  const childCount = item?.children?.length || 0

  if (item?.kind === 'team') {
    const rows = childCount ? Math.ceil(childCount / 3) : 0
    return 176 + rows * 116
  }

  if (item?.kind === 'manager') {
    const rows = childCount ? Math.ceil(childCount / 2) : 0
    return 132 + rows * 104
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
