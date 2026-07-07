import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-none text-sm font-normal tracking-[0.16px] transition-colors duration-150 focus-visible:outline-none focus-visible:carbon-focus disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        default: 'bg-primary text-on-primary hover:bg-primary-hover active:bg-primary-pressed',
        destructive: 'bg-error text-on-primary hover:opacity-90',
        outline: 'border border-primary bg-canvas text-primary hover:bg-surface-1',
        secondary: 'bg-ink text-inverse-ink hover:bg-[#292929]',
        ghost: 'bg-transparent text-primary hover:bg-surface-1',
        link: 'bg-transparent text-primary underline-offset-4 hover:underline p-0 h-auto',
        quantum: 'bg-primary text-on-primary hover:bg-primary-hover active:bg-primary-pressed',
        success: 'bg-success text-on-primary hover:opacity-90',
        warning: 'bg-warning text-ink hover:opacity-90',
        glass: 'bg-surface-1 text-ink border border-hairline hover:bg-surface-2',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-8 px-3 text-sm',
        lg: 'h-12 px-6 text-base',
        xl: 'h-14 px-8 text-base',
        icon: 'h-10 w-10 p-0',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    if (asChild && React.isValidElement(props.children)) {
      const child = props.children as React.ReactElement<{ className?: string }>
      return React.cloneElement(child, {
        className: cn(buttonVariants({ variant, size, className }), child.props.className),
      })
    }
    return <button className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }
