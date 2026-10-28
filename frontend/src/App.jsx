
import { useEffect, useState } from 'react'
import {
  ShieldAlert,
  LayoutDashboard,
  ClipboardList,
  Search,
  Bell,
  ChevronDown,
  MapPin,
  Clock3,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Plus,
  X,
  RefreshCw,
  Send,
  ArrowRight,
  ArrowLeft,
  ClipboardCheck,
  Globe,
  LockKeyhole,
} from 'lucide-react'

const API_URL = 'http://127.0.0.1:8000/api'

const navigation = [
  { label: 'Report an Incident', icon: Plus },
  { label: 'Staff Dashboard', icon: LayoutDashboard },
]

function formatDate(value) {
  if (!value) return 'Unknown'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleString(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function getLocation(location) {
  if (Array.isArray(location)) {
    return location.length ? location.join(', ') : 'Location not identified'
  }

  if (typeof location === 'string' && location.trim()) {
    return location
  }

  return 'Location not identified'
}

function getReference(incident) {
  return (
    incident.reference ||
    `CS-${String(incident.id).padStart(5, '0')}`
  )
}

function StatusBadge({ status }) {
  const styles = {
    New: 'bg-blue-500/15 text-blue-400 ring-blue-500/20',
    'Under Review': 'bg-amber-500/15 text-amber-400 ring-amber-500/20',
    Resolved: 'bg-emerald-500/15 text-emerald-400 ring-emerald-500/20',
  }

  return (
    <span
      className={`inline-flex whitespace-nowrap rounded-full px-3 py-1 text-xs font-bold ring-1 ring-inset ${
        styles[status] || 'bg-zinc-500/15 text-zinc-400 ring-zinc-500/20'
      }`}
    >
      {status || 'Unknown'}
    </span>
  )
}

function SeverityBadge({ severity }) {
  const styles = {
    High: 'text-red-400 bg-red-500/10',
    Medium: 'text-amber-400 bg-amber-500/10',
    Low: 'text-emerald-400 bg-emerald-500/10',
  }

  return (
    <span
      className={`inline-flex rounded-md px-2.5 py-1 text-xs font-bold ${
        styles[severity] || 'text-zinc-400 bg-zinc-500/10'
      }`}
    >
      {severity || 'Unknown'}
    </span>
  )
}

function SummaryCard({ title, value, description, icon: Icon, accent }) {
  const accents = {
    blue: 'bg-blue-500/15 text-blue-400',
    amber: 'bg-amber-500/15 text-amber-400',
    emerald: 'bg-emerald-500/15 text-emerald-400',
    red: 'bg-red-500/15 text-red-400',
    purple: 'bg-purple-500/15 text-purple-400',
  }

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 transition hover:border-zinc-700">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-zinc-400">{title}</p>
          <p className="mt-3 text-3xl font-black text-white">{value}</p>
        </div>
        <div className={`rounded-xl p-3 ${accents[accent]}`}>
          <Icon size={22} />
        </div>
      </div>
      <p className="mt-4 text-xs text-zinc-500">{description}</p>
    </div>
  )
}

function ReportPage({ onSubmitted }) {
  const [reportText, setReportText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()

    const text = reportText.trim()

    if (text.length < 5) {
      setError('Please describe the incident in at least 5 characters.')
      return
    }

    setSubmitting(true)
    setError('')
    setSuccess(null)

    try {
      const response = await fetch(`${API_URL}/incidents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ report_text: text }),
      })

      const result = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          result.detail || 'Your report could not be submitted. Please try again.'
        )
      }

      setSuccess({
        reference: result.reference,
        message:
          result.message || 'Your incident report was submitted successfully.',
      })
      setReportText('')

      if (onSubmitted) onSubmitted()
    } catch (err) {
      setError(
        err.message ||
          'Could not connect to CampusSentry. Please check your connection and try again.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-8">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-sky-500/20 bg-sky-500/10 px-3 py-1.5 text-xs font-bold text-sky-400">
          <ShieldAlert size={15} />
          CAMPUS SAFETY REPORTING
        </div>

        <h2 className="text-3xl font-black tracking-tight sm:text-4xl">
          Report an Incident
        </h2>

        <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-400">
          Help keep our campus safe. Describe what happened and where it
          occurred. CampusSentry will analyse your report automatically.
        </p>
      </div>

      {success && (
        <div
          role="status"
          className="mb-6 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-5 sm:p-6"
        >
          <div className="flex items-start gap-3">
            <div className="rounded-full bg-emerald-500/15 p-2 text-emerald-400">
              <CheckCircle2 size={24} />
            </div>

            <div className="min-w-0 flex-1">
              <h3 className="text-lg font-bold text-emerald-300">
                Report submitted successfully
              </h3>

              <p className="mt-2 text-sm leading-6 text-zinc-300">
                {success.message} Keep your reference number so you can
                identify your report if you need to follow up.
              </p>

              <div className="mt-4 rounded-lg border border-emerald-500/20 bg-zinc-950/60 p-4">
                <p className="text-xs text-zinc-500">Your reference number</p>
                <p className="mt-1 break-all text-2xl font-black tracking-wider text-emerald-400">
                  {success.reference}
                </p>
              </div>

              <button
                type="button"
                onClick={() => setSuccess(null)}
                className="mt-4 text-sm font-bold text-emerald-300 hover:text-white"
              >
                Submit another report
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div
          role="alert"
          className="mb-6 flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300"
        >
          <AlertTriangle size={19} className="mt-0.5 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/80">
        <div className="border-b border-zinc-800 bg-zinc-900 px-5 py-5 sm:px-8">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-sky-500/15 p-3 text-sky-400">
              <FileText size={22} />
            </div>
            <div>
              <h3 className="font-bold">Incident details</h3>
              <p className="mt-1 text-xs text-zinc-500">
                Fields marked required must be completed.
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 p-5 sm:p-8">
          <div>
            <label
              htmlFor="incident-report"
              className="mb-2 block text-sm font-bold text-zinc-200"
            >
              Describe the incident
              <span className="ml-1 text-red-400">*</span>
            </label>

            <p className="mb-3 text-xs leading-5 text-zinc-500">
              Explain what happened and include the location, people or
              facilities affected, and any immediate danger. English, Shona,
              or a mixture of both can be used.
            </p>

            <textarea
              id="incident-report"
              value={reportText}
              onChange={(event) => {
                setReportText(event.target.value)
                if (error) setError('')
              }}
              required
              minLength={5}
              maxLength={5000}
              rows={7}
              placeholder="Example: There is a burst pipe flooding the library, and water is getting close to the server room..."
              className="w-full resize-y rounded-xl border border-zinc-700 bg-zinc-950 p-4 text-sm leading-6 text-white outline-none transition placeholder:text-zinc-600 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/10"
            />

            <div className="mt-2 flex justify-between gap-3 text-xs text-zinc-500">
              <span>Be as specific as possible.</span>
              <span>{reportText.length}/5000</span>
            </div>
          </div>

          <div className="rounded-xl border border-sky-500/20 bg-sky-500/5 p-4">
            <div className="flex items-start gap-3">
              <ShieldAlert size={20} className="mt-0.5 shrink-0 text-sky-400" />
              <div>
                <p className="text-sm font-bold text-sky-300">
                  Automatic report analysis
                </p>
                <p className="mt-1 text-xs leading-5 text-zinc-400">
                  Your report will be analysed for incident category, severity,
                  language, location and relevant entities. A reference number
                  will be generated after successful submission.
                </p>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting || reportText.trim().length < 5}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-sky-500 px-5 py-3.5 text-sm font-black text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto sm:min-w-48"
          >
            {submitting ? (
              <>
                <RefreshCw size={17} className="animate-spin" />
                Analysing report...
              </>
            ) : (
              <>
                <Send size={17} />
                Submit Incident
              </>
            )}
          </button>
        </form>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="flex items-start gap-3 rounded-xl border border-zinc-800 bg-zinc-900/60 p-4">
          <LockKeyhole size={19} className="mt-0.5 shrink-0 text-sky-400" />
          <div>
            <p className="text-sm font-bold">No reporter account required</p>
            <p className="mt-1 text-xs leading-5 text-zinc-500">
              You can submit an incident without signing in.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3 rounded-xl border border-zinc-800 bg-zinc-900/60 p-4">
          <ClipboardCheck size={19} className="mt-0.5 shrink-0 text-sky-400" />
          <div>
            <p className="text-sm font-bold">Keep your reference number</p>
            <p className="mt-1 text-xs leading-5 text-zinc-500">
              Use it to identify your report when following up with campus staff.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function DashboardPage({
  incidents,
  loading,
  refreshing,
  apiError,
  onRefresh,
  onUpdateStatus,
  updatingIds,
}) {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All statuses')
  const [severityFilter, setSeverityFilter] = useState('All severities')

  const filteredIncidents = incidents.filter((incident) => {
    const query = search.trim().toLowerCase()
    const location = getLocation(incident.location)

    const matchesSearch =
      !query ||
      String(incident.report_text || '').toLowerCase().includes(query) ||
      getReference(incident).toLowerCase().includes(query) ||
      String(incident.category || '').toLowerCase().includes(query) ||
      location.toLowerCase().includes(query) ||
      String(incident.language || '').toLowerCase().includes(query)

    return (
      matchesSearch &&
      (statusFilter === 'All statuses' ||
        incident.status === statusFilter) &&
      (severityFilter === 'All severities' ||
        incident.severity === severityFilter)
    )
  })

  const total = incidents.length
  const newCount = incidents.filter((i) => i.status === 'New').length
  const resolvedCount = incidents.filter((i) => i.status === 'Resolved').length
  const highCount = incidents.filter((i) => i.severity === 'High').length
  const reviewCount = incidents.filter(
    (i) => i.status === 'Under Review'
  ).length

  return (
    <>
      {loading && (
        <p className="mb-5 rounded-lg border border-sky-500/20 bg-sky-500/5 p-4 text-sm text-sky-400">
          Loading incidents from your database...
        </p>
      )}

      {apiError && (
        <div
          role="alert"
          className="mb-5 flex flex-col gap-3 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300 sm:flex-row sm:items-center sm:justify-between"
        >
          <span>{apiError}</span>
          <button
            onClick={onRefresh}
            className="shrink-0 rounded-lg border border-red-400/30 px-3 py-2 font-bold hover:bg-red-500/10"
          >
            Try again
          </button>
        </div>
      )}

      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm text-sky-400">Campus safety overview</p>
          <h2 className="mt-2 text-2xl font-black sm:text-3xl">
            Incident Dashboard
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
            Monitor campus reports, review incident severity and track
            resolution progress.
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={refreshing || loading}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-sky-500 px-4 py-3 text-sm font-bold text-white transition hover:bg-sky-400 disabled:opacity-50"
        >
          <RefreshCw size={17} className={refreshing ? 'animate-spin' : ''} />
          Refresh incidents
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <SummaryCard
          title="Total Incidents"
          value={total}
          description="Reports in your database"
          icon={FileText}
          accent="blue"
        />
        <SummaryCard
          title="New Reports"
          value={newCount}
          description="Awaiting initial review"
          icon={AlertTriangle}
          accent="amber"
        />
        <SummaryCard
          title="Resolved"
          value={resolvedCount}
          description="Marked as resolved"
          icon={CheckCircle2}
          accent="emerald"
        />
        <SummaryCard
          title="High Severity"
          value={highCount}
          description="Requires close attention"
          icon={ShieldAlert}
          accent="red"
        />
        <SummaryCard
          title="Under Review"
          value={reviewCount}
          description="Being investigated"
          icon={Clock3}
          accent="purple"
        />
      </div>

      <section className="mt-8 overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/70">
        <div className="flex flex-col justify-between gap-4 border-b border-zinc-800 p-5 sm:flex-row sm:items-center sm:p-6">
          <div>
            <h3 className="text-lg font-bold">Recent incidents</h3>
            <p className="mt-1 text-xs text-zinc-500">
              Reports retrieved from your SQLite database.
            </p>
          </div>

          <div className="relative w-full sm:max-w-xs">
            <Search
              size={17}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
            />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search reports, locations..."
              className="w-full rounded-lg border border-zinc-700 bg-zinc-950 py-2.5 pl-10 pr-3 text-sm outline-none placeholder:text-zinc-600 focus:border-sky-500"
            />
          </div>
        </div>

        <div className="flex flex-col gap-3 border-b border-zinc-800 px-5 py-4 sm:flex-row sm:flex-wrap sm:items-center sm:px-6">
          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            className="rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2.5 text-sm text-zinc-300 outline-none focus:border-sky-500"
          >
            <option>All statuses</option>
            <option>New</option>
            <option>Under Review</option>
            <option>Resolved</option>
          </select>

          <select
            value={severityFilter}
            onChange={(event) => setSeverityFilter(event.target.value)}
            className="rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2.5 text-sm text-zinc-300 outline-none focus:border-sky-500"
          >
            <option>All severities</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>

          <p className="text-xs text-zinc-500 sm:ml-auto">
            Showing {filteredIncidents.length} of {total} incidents
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[1000px] text-left">
            <thead className="bg-zinc-950/70 text-[10px] uppercase tracking-[0.15em] text-zinc-500">
              <tr>
                <th className="px-6 py-4 font-bold">Incident report</th>
                <th className="px-6 py-4 font-bold">Category</th>
                <th className="px-6 py-4 font-bold">Language</th>
                <th className="px-6 py-4 font-bold">Severity</th>
                <th className="px-6 py-4 font-bold">Status</th>
                <th className="px-6 py-4 font-bold">Reported</th>
                <th className="px-6 py-4 font-bold">Update status</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-zinc-800">
              {filteredIncidents.map((incident) => (
                <tr
                  key={incident.id}
                  className="transition hover:bg-zinc-800/40"
                >
                  <td className="max-w-sm px-6 py-5">
                    <p className="text-sm font-bold leading-6 text-zinc-100">
                      {incident.report_text || 'No report text available'}
                    </p>

                    <p className="mt-2 flex items-center gap-1.5 text-xs text-zinc-500">
                      <MapPin size={13} className="shrink-0" />
                      {getLocation(incident.location)}
                    </p>

                    <p className="mt-1 text-[10px] font-bold tracking-wider text-sky-400">
                      {getReference(incident)}
                    </p>

                    {Array.isArray(incident.entities) &&
                      incident.entities.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {incident.entities.map((entity, index) => (
                            <span
                              key={`${entity.text}-${index}`}
                              className="rounded-md border border-zinc-700 bg-zinc-800 px-2 py-1 text-[10px] text-zinc-400"
                              title={entity.label}
                            >
                              {entity.text}
                              {entity.label ? ` · ${entity.label}` : ''}
                            </span>
                          ))}
                        </div>
                      )}
                  </td>

                  <td className="px-6 py-5 text-sm text-zinc-300">
                    {incident.category || 'Unclassified'}
                  </td>

                  <td className="px-6 py-5 text-sm text-zinc-400">
                    {incident.language || 'Unknown'}
                  </td>

                  <td className="px-6 py-5">
                    <SeverityBadge severity={incident.severity} />
                  </td>

                  <td className="px-6 py-5">
                    <StatusBadge status={incident.status} />
                  </td>

                  <td className="whitespace-nowrap px-6 py-5 text-xs text-zinc-400">
                    {formatDate(incident.created_at)}
                  </td>

                  <td className="px-6 py-5">
                    <select
                      value={incident.status}
                      disabled={updatingIds.includes(incident.id)}
                      onChange={(event) =>
                        onUpdateStatus(incident.id, event.target.value)
                      }
                      aria-label={`Update status for ${getReference(incident)}`}
                      className="rounded-md border border-zinc-700 bg-zinc-950 px-2 py-2 text-xs text-zinc-300 outline-none focus:border-sky-500 disabled:cursor-wait disabled:opacity-50"
                    >
                      <option>New</option>
                      <option>Under Review</option>
                      <option>Resolved</option>
                    </select>

                    {updatingIds.includes(incident.id) && (
                      <p className="mt-1 text-[10px] text-sky-400">
                        Saving...
                      </p>
                    )}
                  </td>
                </tr>
              ))}

              {!loading && filteredIncidents.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-6 py-12 text-center text-sm text-zinc-500"
                  >
                    {incidents.length === 0
                      ? 'No incidents are available in the database.'
                      : 'No incidents match your search or filters.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="flex flex-col gap-2 border-t border-zinc-800 px-6 py-4 text-xs text-zinc-500 sm:flex-row sm:items-center sm:justify-between">
          <span>CampusSentry · Live incident monitoring</span>
          <span>
            {loading
              ? 'Connecting to database...'
              : apiError
                ? 'Connection needs attention'
                : 'Connected to the Python API'}
          </span>
        </div>
      </section>

      <div className="mt-6 flex items-start gap-3 rounded-xl border border-sky-500/20 bg-sky-500/5 p-4">
        <ShieldAlert size={20} className="mt-0.5 shrink-0 text-sky-400" />
        <div>
          <p className="text-sm font-bold text-sky-300">
            NLP-powered campus safety
          </p>
          <p className="mt-1 text-xs leading-5 text-zinc-400">
            Incident category, severity, language, locations and extracted
            entities are loaded from your Python backend. Status updates are
            saved to the SQLite database.
          </p>
        </div>
      </div>
    </>
  )
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activePage, setActivePage] = useState('Report an Incident')
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [apiError, setApiError] = useState('')
  const [updatingIds, setUpdatingIds] = useState([])

  async function loadIncidents(showLoading = true) {
    if (showLoading) {
      setLoading(true)
    } else {
      setRefreshing(true)
    }

    try {
      const response = await fetch(`${API_URL}/incidents`)

      if (!response.ok) {
        throw new Error(`The API returned an error (${response.status}).`)
      }

      const data = await response.json()

      if (!Array.isArray(data)) {
        throw new Error('The API returned an unexpected response.')
      }

      setIncidents(data)
      setApiError('')
    } catch (error) {
      setApiError(
        error.message ||
          'Could not connect to the Python API. Check that it is running.'
      )
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    if (activePage === 'Staff Dashboard') {
      loadIncidents()
    }
  }, [activePage])

  function handleReportSubmitted() {
    // Refresh the data when staff open the dashboard.
    // This also updates the incident count in the navigation.
    loadIncidents(false)
  }

  async function updateStatus(id, status) {
    const previousIncidents = incidents

    setUpdatingIds((current) => [...current, id])
    setApiError('')

    setIncidents((current) =>
      current.map((incident) =>
        incident.id === id ? { ...incident, status } : incident
      )
    )

    try {
      const response = await fetch(
        `${API_URL}/incidents/${id}/status`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status }),
        }
      )

      const result = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          result.detail || 'Could not save the incident status.'
        )
      }

      setIncidents((current) =>
        current.map((incident) =>
          incident.id === id ? result : incident
        )
      )
    } catch (error) {
      setIncidents(previousIncidents)
      setApiError(
        `${error.message || 'Failed to save the status.'} Your change was not confirmed.`
      )
    } finally {
      setUpdatingIds((current) =>
        current.filter((incidentId) => incidentId !== id)
      )
    }
  }

  const isDashboard = activePage === 'Staff Dashboard'

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-white">
      {sidebarOpen && (
        <button
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-zinc-800 bg-zinc-950 transition-transform duration-200 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-20 items-center justify-between border-b border-zinc-800 px-6">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-sky-500/15 p-2.5 text-sky-400">
              <ShieldAlert size={25} />
            </div>
            <div>
              <h1 className="text-base font-black tracking-wide">
                CampusSentry
              </h1>
              <p className="mt-1 text-[10px] uppercase tracking-[0.2em] text-zinc-500">
                Campus safety NLP
              </p>
            </div>
          </div>

          <button
            onClick={() => setSidebarOpen(false)}
            className="text-zinc-500 lg:hidden"
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>

        <div className="px-4 pt-7">
          <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-600">
            Workspace
          </p>

          <nav className="space-y-1">
            {navigation.map(({ label, icon: Icon }) => (
              <button
                key={label}
                onClick={() => {
                  setActivePage(label)
                  setSidebarOpen(false)
                }}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-sm transition ${
                  activePage === label
                    ? 'bg-sky-500/10 font-bold text-sky-400'
                    : 'text-zinc-400 hover:bg-zinc-900 hover:text-white'
                }`}
              >
                <Icon size={18} />
                {label}

                {label === 'Staff Dashboard' && incidents.length > 0 && (
                  <span className="ml-auto rounded-md bg-zinc-800 px-2 py-0.5 text-xs">
                    {incidents.length}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        <div className="mt-auto border-t border-zinc-800 p-4">
          <div className="rounded-xl bg-zinc-900 p-4">
            <div className="flex items-center gap-2 text-sky-400">
              <ShieldAlert size={17} />
              <span className="text-xs font-bold">CampusSentry NLP</span>
            </div>
            <p className="mt-2 text-xs leading-5 text-zinc-500">
              Incident classification, location extraction and severity
              assessment.
            </p>
          </div>

          <div className="mt-4 flex items-center gap-3 px-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-sky-500/15 text-sm font-black text-sky-400">
              {isDashboard ? 'S' : 'C'}
            </div>
            <div>
              <p className="text-sm font-bold">
                {isDashboard ? 'Staff Dashboard' : 'Campus Reporter'}
              </p>
              <p className="mt-1 text-xs text-zinc-500">
                {isDashboard ? 'Campus safety team' : 'Public reporting'}
              </p>
            </div>
          </div>
        </div>
      </aside>

      <div className="min-h-screen lg:pl-64">
        <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-zinc-800 bg-[#1a1a1a]/95 px-4 backdrop-blur sm:px-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded-lg p-2 text-zinc-400 hover:bg-zinc-800 lg:hidden"
              aria-label="Open navigation"
            >
              <span className="inline-flex">
                <ArrowLeft size={20} />
              </span>
            </button>

            <div>
              <p className="text-xs text-zinc-500">
                CampusSentry / {activePage}
              </p>
              <h2 className="mt-1 text-lg font-bold">{activePage}</h2>
            </div>
          </div>

          <div className="flex items-center gap-3 sm:gap-5">
            <span className="hidden text-xs text-zinc-500 sm:block">
              Campus incident monitoring
            </span>

            {isDashboard && (
              <button
                onClick={() => loadIncidents(false)}
                disabled={refreshing || loading}
                className="rounded-lg border border-zinc-800 p-2.5 text-zinc-400 transition hover:bg-zinc-900 disabled:opacity-50"
                aria-label="Refresh incidents"
                title="Refresh incidents"
              >
                <RefreshCw
                  size={18}
                  className={refreshing ? 'animate-spin' : ''}
                />
              </button>
            )}

            {isDashboard && (
              <button
                className="relative rounded-lg border border-zinc-800 p-2.5 text-zinc-400 hover:bg-zinc-900"
                aria-label="Notifications"
              >
                <Bell size={18} />
                {incidents.some((i) => i.status === 'New') && (
                  <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-sky-400" />
                )}
              </button>
            )}

            <div className="hidden items-center gap-2 rounded-lg border border-zinc-800 p-2 text-sm sm:flex">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-zinc-700 font-bold">
                {isDashboard ? 'S' : 'C'}
              </span>
              <span className="text-zinc-300">
                {isDashboard ? 'Staff' : 'Reporter'}
              </span>
              <ChevronDown size={15} className="text-zinc-500" />
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[1600px] p-4 sm:p-8">
          {isDashboard ? (
            <DashboardPage
              incidents={incidents}
              loading={loading}
              refreshing={refreshing}
              apiError={apiError}
              onRefresh={() => loadIncidents(false)}
              onUpdateStatus={updateStatus}
              updatingIds={updatingIds}
            />
          ) : (
            <ReportPage onSubmitted={handleReportSubmitted} />
          )}

          <footer className="mt-10 border-t border-zinc-800 py-5 text-center text-xs text-zinc-600">
            CampusSentry NLP · Campus incident reporting and monitoring
          </footer>
        </main>
      </div>
    </div>
  )
}
