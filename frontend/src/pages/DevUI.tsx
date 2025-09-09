import React, { useState } from 'react'
import { Button } from '../components/ui/Button'
import { Card, CardBody, CardHeader } from '../components/ui/Card'
import { KpiCard } from '../components/ui/KpiCard'
import { FormField } from '../components/ui/FormField'
import { Input } from '../components/ui/Input'
import { Select } from '../components/ui/Select'
import { Textarea } from '../components/ui/Textarea'
import { Checkbox } from '../components/ui/Checkbox'
import { RadioGroup } from '../components/ui/RadioGroup'
import { DateInput } from '../components/ui/DateInput'
import { Toggle } from '../components/ui/Toggle'
import { ProgressBar } from '../components/ui/ProgressBar'
import { Skeleton } from '../components/ui/Skeleton'
import { EmptyState } from '../components/ui/EmptyState'
import { ConfirmDialog } from '../components/ui/ConfirmDialog'
import { ToastProvider, useToast } from '../components/ui/Toast'

function DemoInner(){
  const [sex, setSex] = useState('')
  const [notes, setNotes] = useState('')
  const [toggle, setToggle] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const { show } = useToast()

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <KpiCard label="Total pigs" value={123} help="Count of active pigs" />
        <KpiCard label="ADG" value="0.72 kg/day" />
        <KpiCard label="Tasks due" value={5} />
      </div>

      <Card>
        <CardHeader title="Buttons" />
        <CardBody className="space-x-2">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger">Danger</Button>
          <Button isLoading>Loading</Button>
          <Button disabled>Disabled</Button>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Form Fields" subtitle="Labels, helper, error, 48px inputs" />
        <CardBody className="grid md:grid-cols-2 gap-4">
          <FormField label="Ear tag" required helpText="Unique ID on the ear tag.">
            {({ id, ariaDescribedBy }) => (
              <Input id={id} aria-describedby={ariaDescribedBy} placeholder="e.g., 1234" />
            )}
          </FormField>
          <FormField label="Sex">
            {({ id, ariaDescribedBy }) => (
              <Select id={id} aria-describedby={ariaDescribedBy} value={sex} onChange={(e: React.ChangeEvent<HTMLSelectElement>)=>setSex(e.target.value)}>
                <option value="">Select...</option>
                <option value="F">Female</option>
                <option value="M">Male</option>
              </Select>
            )}
          </FormField>
          <FormField label="Birth date">
            {({ id, ariaDescribedBy }) => (
              <DateInput id={id} aria-describedby={ariaDescribedBy} />
            )}
          </FormField>
          <FormField label="Notes" helpText="Optional.">
            {({ id, ariaDescribedBy }) => (
              <Textarea id={id} aria-describedby={ariaDescribedBy} value={notes} onChange={(e: React.ChangeEvent<HTMLTextAreaElement>)=>setNotes(e.target.value)} />
            )}
          </FormField>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2">
              <Checkbox /> <span>Keep</span>
            </label>
            <RadioGroup name="class" options={[{label:'Sow', value:'sow'},{label:'Boar', value:'boar'}]} />
            <Toggle checked={toggle} onChange={setToggle} onLabel="On" offLabel="Off" />
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Feedback" />
        <CardBody className="space-x-2">
          <ProgressBar value={65} label="Uploading..." />
          <div className="h-6" />
          <div className="space-x-2">
            <Button onClick={() => show('success', 'Saved.')}>Show success</Button>
            <Button variant="secondary" onClick={() => show('info', 'Info message')}>Show info</Button>
            <Button variant="danger" onClick={() => show('error', 'Something failed')}>Show error</Button>
            <Button onClick={() => setShowConfirm(true)}>Confirm dialog</Button>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Empty and loading" />
        <CardBody className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <Skeleton className="h-6 w-1/2" />
            <Skeleton className="h-32 mt-2" />
          </div>
          <EmptyState message="No results" actionLabel="Reset filters" onAction={() => show('info', 'Filters reset')} />
        </CardBody>
      </Card>

      <ConfirmDialog
        open={showConfirm}
        title="Mark pig as Sold?"
        description="You can undo from activity."
        confirmLabel="Mark Sold"
        onConfirm={() => { setShowConfirm(false); show('success', 'Saved.') }}
        onCancel={() => setShowConfirm(false)}
      />
    </div>
  )
}

export default function DevUI(){
  return (
    <ToastProvider>
      <DemoInner />
    </ToastProvider>
  )
}

