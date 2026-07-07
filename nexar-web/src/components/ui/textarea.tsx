import * as React from 'react'
import { cn } from '@/lib/utils'

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => (
    <textarea
      className={cn(
        'flex min-h-[80px] w-full rounded-none border-0 border-b border-hairline bg-surface-1 px-4 py-2 text-sm text-ink placeholder:text-ink-subtle transition-colors carbon-focus-input focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 font-mono',
        className
      )}
      ref={ref}
      {...props}
    />
  )
)
Textarea.displayName = 'Textarea'

export { Textarea }
