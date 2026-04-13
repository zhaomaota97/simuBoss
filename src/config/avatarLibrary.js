function svgToDataUri(svg) {
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

function buildAvatarSvg({ bg, skin, hair, shirt }) {
  return `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" fill="none">
      <rect width="96" height="96" rx="28" fill="${bg}" />
      <circle cx="48" cy="38" r="18" fill="${skin}" />
      <path d="M26 34c2-14 14-22 22-22s20 8 22 22c-5-4-10-6-16-6-5 0-9 1-14 4-4 2-8 2-14 2Z" fill="${hair}" />
      <path d="M22 88c2-18 14-28 26-28s24 10 26 28H22Z" fill="${shirt}" />
      <circle cx="41.5" cy="39.5" r="2.5" fill="#1E293B" />
      <circle cx="54.5" cy="39.5" r="2.5" fill="#1E293B" />
      <path d="M42 49c2.5 3 9.5 3 12 0" stroke="#7C2D12" stroke-width="2.5" stroke-linecap="round" />
    </svg>
  `.trim()
}

const palette = [
  { id: 'avatar-amber', label: '琥珀', bg: '#FEF3C7', skin: '#F2C29B', hair: '#7C2D12', shirt: '#F59E0B' },
  { id: 'avatar-ocean', label: '海蓝', bg: '#DBEAFE', skin: '#E8BC96', hair: '#1D4ED8', shirt: '#0EA5E9' },
  { id: 'avatar-forest', label: '森林', bg: '#DCFCE7', skin: '#E5B089', hair: '#14532D', shirt: '#22C55E' },
  { id: 'avatar-rose', label: '玫瑰', bg: '#FCE7F3', skin: '#F1C7A5', hair: '#9D174D', shirt: '#EC4899' },
  { id: 'avatar-indigo', label: '靛蓝', bg: '#E0E7FF', skin: '#E6B794', hair: '#312E81', shirt: '#6366F1' },
  { id: 'avatar-slate', label: '石墨', bg: '#E2E8F0', skin: '#E9BC99', hair: '#334155', shirt: '#64748B' },
  { id: 'avatar-sunset', label: '夕照', bg: '#FFEDD5', skin: '#F0B48D', hair: '#9A3412', shirt: '#F97316' },
  { id: 'avatar-mint', label: '薄荷', bg: '#D1FAE5', skin: '#F2C6A2', hair: '#065F46', shirt: '#10B981' },
  { id: 'avatar-violet', label: '紫罗兰', bg: '#F3E8FF', skin: '#E9B894', hair: '#6D28D9', shirt: '#8B5CF6' },
  { id: 'avatar-sky', label: '晴空', bg: '#E0F2FE', skin: '#EABF9C', hair: '#075985', shirt: '#38BDF8' },
  { id: 'avatar-lime', label: '青柠', bg: '#ECFCCB', skin: '#E8B58E', hair: '#3F6212', shirt: '#84CC16' },
  { id: 'avatar-coral', label: '珊瑚', bg: '#FFE4E6', skin: '#F2C3A1', hair: '#BE123C', shirt: '#FB7185' },
]

export const AVATAR_LIBRARY = palette.map((item) => ({
  ...item,
  value: `avatar:${item.id}`,
  src: svgToDataUri(buildAvatarSvg(item)),
}))

const avatarMap = Object.fromEntries(AVATAR_LIBRARY.map((item) => [item.value, item]))

export function getAvatarByValue(value) {
  return avatarMap[value] || null
}

export function isAvatarValue(value) {
  return Boolean(getAvatarByValue(value))
}
