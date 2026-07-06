/**
 * Pipeline Stepper
 * Horizontal step indicator showing pipeline progress.
 */

import type { ElementType } from 'react'
import { Check, Code, Brain, Cpu, Play } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { PipelineStage } from '@/types/pipeline'

interface Step {
  id: PipelineStage
  label: string
  icon: ElementType
}

const steps: Step[] = [
  { id: 'idle', label: 'Code Input', icon: Code },
  { id: 'analyzing', label: 'Analysis', icon: Brain },
  { id: 'deciding', label: 'Decision', icon: Cpu },
  { id: 'complete', label: 'Results', icon: Play },
]

function getStepState(stepIndex: number, currentStage: PipelineStage): 'pending' | 'active' | 'complete' {
  const stageOrder: PipelineStage[] = ['idle', 'processing', 'analyzing', 'deciding', 'complete', 'error']
  const currentIndex = stageOrder.indexOf(currentStage)

  const thresholds = [0, 2, 3, 4]

  if (currentStage === 'error') {
    return stepIndex === 0 ? 'complete' : 'pending'
  }

  if (currentIndex >= thresholds[stepIndex] + 1) return 'complete'
  if (currentIndex >= thresholds[stepIndex]) return 'active'
  return 'pending'
}

interface PipelineStepperProps {
  currentStage: PipelineStage
}

export function PipelineStepper({ currentStage }: PipelineStepperProps) {
  return (
    <div className="flex items-center justify-between">
      {steps.map((step, index) => {
        const state = getStepState(index, currentStage)
        const Icon = step.icon

        return (
          <div key={step.id} className="flex flex-1 items-center">
            <div className="flex flex-col items-center gap-1.5">
              <div
                className={cn(
                  'flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors',
                  state === 'complete' && 'border-primary bg-primary text-on-primary',
                  state === 'active' && 'border-primary bg-surface-1 text-primary animate-pulse',
                  state === 'pending' && 'border-hairline bg-surface-1 text-ink-subtle'
                )}
              >
                {state === 'complete' ? <Check className="h-5 w-5" /> : <Icon className="h-5 w-5" />}
              </div>
              <span
                className={cn(
                  'text-xs font-medium whitespace-nowrap',
                  state === 'active' && 'text-primary',
                  state === 'complete' && 'text-primary',
                  state === 'pending' && 'text-ink-subtle'
                )}
              >
                {step.label}
              </span>
            </div>

            {index < steps.length - 1 && (
              <div className={cn('mx-2 h-0.5 flex-1 transition-colors', state === 'complete' ? 'bg-primary' : 'bg-hairline')} />
            )}
          </div>
        )
      })}
    </div>
  )
}
