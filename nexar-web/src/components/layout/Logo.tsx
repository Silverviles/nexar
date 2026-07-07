import { Link } from 'react-router-dom'
import { useTheme } from '@/contexts/ThemeContext'
import { cn } from '@/lib/utils'

interface LogoProps {
  /** 'full' renders the icon+wordmark lockup, 'mark' renders the icon alone */
  variant?: 'full' | 'mark'
  /** Force the dark-background logo variant regardless of theme (e.g. a panel that's always dark) */
  inverse?: boolean
  className?: string
  linkTo?: string | null
}

export function Logo({ variant = 'full', inverse = false, className, linkTo = '/' }: LogoProps) {
  const { theme } = useTheme()
  const isDarkBg = inverse || theme === 'dark'
  const src = variant === 'mark' ? '/favicon.png' : isDarkBg ? '/logo-dark-nexar.png' : '/logo-light-nexar.png'
  const img = <img src={src} alt="Nexar" className={cn('h-8 w-auto', className)} />

  if (linkTo === null) return img

  return (
    <Link to={linkTo} className="inline-flex items-center">
      {img}
    </Link>
  )
}
