import { useState } from 'react'
import { Check, Copy } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const METHOD_BADGE_VARIANT = {
  GET: 'default',
  POST: 'success',
  DELETE: 'destructive',
} as const

interface CodeBlockProps {
  code: string
  method?: keyof typeof METHOD_BADGE_VARIANT
  path?: string
  className?: string
}

function CodeBlock({ code, method, path, className }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  const hasHeader = Boolean(method || path)

  return (
    <div className={cn('border border-hairline bg-surface-1', className)}>
      {hasHeader && (
        <div className="flex items-center justify-between gap-3 border-b border-hairline px-4 py-2">
          <div className="flex items-center gap-3">
            {method && <Badge variant={METHOD_BADGE_VARIANT[method]}>{method}</Badge>}
            {path && <span className="font-mono text-sm text-ink-muted">{path}</span>}
          </div>
          <button
            type="button"
            onClick={handleCopy}
            aria-label="Copy code"
            className="text-ink-muted transition-colors hover:text-ink"
          >
            {copied ? <Check className="h-4 w-4 text-success" /> : <Copy className="h-4 w-4" />}
          </button>
        </div>
      )}
      <div className="relative">
        {!hasHeader && (
          <button
            type="button"
            onClick={handleCopy}
            aria-label="Copy code"
            className="absolute right-3 top-3 text-ink-muted transition-colors hover:text-ink"
          >
            {copied ? <Check className="h-4 w-4 text-success" /> : <Copy className="h-4 w-4" />}
          </button>
        )}
        <pre className={cn('overflow-x-auto p-4 font-mono text-sm text-ink', !hasHeader && 'pr-10')}>
          <code>{code}</code>
        </pre>
      </div>
    </div>
  )
}

export { CodeBlock }
