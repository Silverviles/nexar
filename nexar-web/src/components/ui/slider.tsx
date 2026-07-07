import { useState } from 'react'
import { cn } from '@/lib/utils'

export interface SliderProps {
  value?: number[]
  defaultValue?: number[]
  onValueChange?: (value: number[]) => void
  min?: number
  max?: number
  step?: number
  className?: string
  disabled?: boolean
}

function Slider({ value: valueProp, defaultValue, onValueChange, min = 0, max = 100, step = 1, className, disabled }: SliderProps) {
  const [internal, setInternal] = useState(defaultValue ?? [min])
  const value = valueProp ?? internal

  return (
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      disabled={disabled}
      value={value[0] ?? min}
      onChange={(e) => {
        const next = [Number(e.target.value)]
        setInternal(next)
        onValueChange?.(next)
      }}
      className={cn(
        'h-1 w-full cursor-pointer appearance-none rounded-none bg-surface-2 accent-primary carbon-focus',
        className
      )}
    />
  )
}

export { Slider }
