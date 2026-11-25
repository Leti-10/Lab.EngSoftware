import { useState } from 'react'

export function UserAvatar({
  username,
  url,
  className = '',
}: {
  username: string
  url?: string | null
  className?: string
}) {
  const [failedUrl, setFailedUrl] = useState<string | null>(null)
  const showImage = Boolean(url) && failedUrl !== url

  return (
    <span
      aria-hidden="true"
      className={`relative grid place-items-center overflow-hidden bg-blue-warm-100 font-serif font-semibold text-blue-warm-700 uppercase ${className}`}
    >
      {username.charAt(0)}
      {showImage && (
        <img
          src={url ?? undefined}
          alt=""
          onError={() => setFailedUrl(url ?? null)}
          className="absolute inset-0 size-full object-cover"
        />
      )}
    </span>
  )
}
