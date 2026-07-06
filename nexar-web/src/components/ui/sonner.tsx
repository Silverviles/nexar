import { Toaster as Sonner, type ToasterProps } from 'sonner'
import { useTheme } from '@/contexts/ThemeContext'

/** Single, Carbon-flat toast system for the whole app -- replaces frontend's duplicate Toaster+Sonner mount. */
function Toaster({ ...props }: ToasterProps) {
  const { theme } = useTheme()

  return (
    <Sonner
      theme={theme}
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            'group toast rounded-none! border! border-hairline! bg-canvas! text-ink! shadow-none!',
          description: 'text-ink-muted',
          actionButton: 'bg-primary! text-on-primary! rounded-none!',
          cancelButton: 'bg-surface-1! text-ink! rounded-none!',
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
export { toast } from 'sonner'
