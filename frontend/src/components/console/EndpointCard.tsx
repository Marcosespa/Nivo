import type { FormEventHandler, ReactNode } from 'react'
import Card from '../common/Card'

interface EndpointCardProps {
  title: string
  endpoint: string
  description: string
  children: ReactNode
  onSubmit?: FormEventHandler<HTMLFormElement>
  footer?: ReactNode
}

export default function EndpointCard({
  title,
  endpoint,
  description,
  children,
  onSubmit,
  footer,
}: EndpointCardProps) {
  const content = (
    <>
      <div className="mb-4 space-y-1">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          <span className="rounded-lg border border-teal-500/30 bg-teal-500/10 px-2 py-1 text-xs font-medium text-teal-300">
            {endpoint}
          </span>
        </div>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
      <div className="space-y-4">{children}</div>
      {footer ? <div className="mt-4">{footer}</div> : null}
    </>
  )

  if (!onSubmit) {
    return <Card className="!rounded-xl !p-5">{content}</Card>
  }

  return (
    <Card className="!rounded-xl !p-5">
      <form className="space-y-4" onSubmit={onSubmit}>
        {content}
      </form>
    </Card>
  )
}
