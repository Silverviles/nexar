import { useEffect, useRef, useState } from 'react'
import { animate, useInView } from 'framer-motion'

interface AnimatedNumberProps {
  value: string
  className?: string
}

/** Animates the leading numeric portion of a stat string (e.g. "99.9%", "10K+", "50ms") on scroll into view. */
function AnimatedNumber({ value, className }: AnimatedNumberProps) {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true, margin: '-80px' })
  const [display, setDisplay] = useState(value)

  useEffect(() => {
    const match = value.match(/^(\d+(?:\.\d+)?)(.*)$/)
    if (!isInView || !match) return

    const target = parseFloat(match[1])
    const suffix = match[2]
    const decimals = match[1].includes('.') ? 1 : 0

    const controls = animate(0, target, {
      duration: 1.2,
      ease: [0.4, 0, 0.2, 1],
      onUpdate: (v) => setDisplay(`${v.toFixed(decimals)}${suffix}`),
    })

    return () => controls.stop()
  }, [isInView, value])

  return (
    <span ref={ref} className={className}>
      {display}
    </span>
  )
}

export { AnimatedNumber }
