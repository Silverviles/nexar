import { motion, type HTMLMotionProps } from 'framer-motion'

interface FadeInProps extends Omit<HTMLMotionProps<'div'>, 'whileInView'> {
  delay?: number
  scale?: boolean
  /** Trigger on scroll-into-view instead of on mount -- for long marketing pages where content starts below the fold. */
  inView?: boolean
}

/** Shared reveal, replacing frontend's animate-fade-in/animate-scale-in utility classes. */
function FadeIn({ delay = 0, scale = false, inView = false, className, children, ...props }: FadeInProps) {
  const animation = { opacity: 1, y: 0, scale: 1 }
  const viewProps = inView
    ? { whileInView: animation, viewport: { once: true, margin: '-80px' } }
    : { animate: animation }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: scale ? 0.98 : 1 }}
      transition={{ duration: 0.25, delay, ease: [0.4, 0, 0.2, 1] }}
      className={className}
      {...viewProps}
      {...props}
    >
      {children}
    </motion.div>
  )
}

export { FadeIn }
