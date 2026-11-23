import { Star } from 'lucide-react'
import { useState } from 'react'

const STARS = [1, 2, 3, 4, 5]

export function Stars({ value, size = 'size-5' }: { value: number; size?: string }) {
  return (
    <span aria-hidden="true" className="inline-flex gap-0.5">
      {STARS.map((star) => {
        const fill = Math.max(0, Math.min(1, value - (star - 1)))
        return (
          <span key={star} className={`relative inline-block ${size}`}>
            <Star className={`absolute inset-0 ${size} text-cream-300`} fill="currentColor" />
            <span className="absolute inset-0 overflow-hidden" style={{ width: `${fill * 100}%` }}>
              <Star className={`${size} text-star`} fill="currentColor" />
            </span>
          </span>
        )
      })}
    </span>
  )
}

export function RatingInput({
  value,
  onChange,
  label = 'Sua nota',
}: {
  value: number
  onChange: (value: number) => void
  label?: string
}) {
  const [hover, setHover] = useState(0)
  const shown = hover || value

  return (
    <div role="radiogroup" aria-label={label} className="flex items-center gap-1">
      {STARS.map((star) => (
        <button
          key={star}
          type="button"
          role="radio"
          aria-checked={value === star}
          aria-label={`${star} ${star === 1 ? 'estrela' : 'estrelas'}`}
          onClick={() => onChange(star)}
          onMouseEnter={() => setHover(star)}
          onMouseLeave={() => setHover(0)}
          onFocus={() => setHover(star)}
          onBlur={() => setHover(0)}
          className="rounded p-0.5 transition-transform hover:scale-110"
        >
          <Star
            aria-hidden="true"
            className={`size-7 ${star <= shown ? 'text-star' : 'text-cream-300'}`}
            fill="currentColor"
          />
        </button>
      ))}
    </div>
  )
}
