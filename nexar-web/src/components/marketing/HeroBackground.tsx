import { motion } from 'framer-motion'

const CENTER = { x: 600, y: 230 }
const STEPS = 32

interface Ring {
  rx: number
  ry: number
  rotate: number
  color: string
  duration: number
  dot: number
  reverse?: boolean
}

const RINGS: Ring[] = [
  { rx: 580, ry: 200, rotate: 0, color: 'var(--color-quantum)', duration: 26, dot: 6 },
  { rx: 580, ry: 200, rotate: 60, color: 'var(--color-hybrid)', duration: 32, dot: 5.5, reverse: true },
  { rx: 580, ry: 200, rotate: 120, color: 'var(--color-classical)', duration: 38, dot: 5 },
]

function ringPoints(ring: Ring) {
  const dir = ring.reverse ? -1 : 1
  const rad = (ring.rotate * Math.PI) / 180
  const cos = Math.cos(rad)
  const sin = Math.sin(rad)
  const cx: number[] = []
  const cy: number[] = []
  for (let i = 0; i <= STEPS; i++) {
    const t = (i / STEPS) * Math.PI * 2 * dir
    const ex = ring.rx * Math.cos(t)
    const ey = ring.ry * Math.sin(t)
    cx.push(CENTER.x + ex * cos - ey * sin)
    cy.push(CENTER.y + ex * sin + ey * cos)
  }
  return { cx, cy }
}

/** Subtle background decoration for the hero -- tilted orbit rings with drifting
    dots, scaled to span the full section, echoing the brand mark without
    competing with the headline. Hidden below `sm` where the hero is too narrow
    for the pattern to read well; `preserveAspectRatio="none"` fills the section
    exactly on larger screens instead of center-cropping the sides. */
function HeroBackground() {
  return (
    <svg
      className="pointer-events-none absolute inset-0 hidden h-full w-full opacity-50 sm:block"
      viewBox="0 0 1200 460"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      {RINGS.map((ring, i) => {
        const { cx, cy } = ringPoints(ring)
        return (
          <g key={i}>
            <ellipse
              cx={CENTER.x}
              cy={CENTER.y}
              rx={ring.rx}
              ry={ring.ry}
              transform={`rotate(${ring.rotate} ${CENTER.x} ${CENTER.y})`}
              fill="none"
              stroke={ring.color}
              strokeWidth={1}
              strokeOpacity={0.25}
              strokeDasharray="2 5"
            />
            <motion.circle
              r={ring.dot}
              fill={ring.color}
              animate={{ cx, cy }}
              transition={{ duration: ring.duration, repeat: Infinity, ease: 'linear' }}
            />
          </g>
        )
      })}
    </svg>
  )
}

export { HeroBackground }
