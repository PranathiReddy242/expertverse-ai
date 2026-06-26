export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <div className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-3xl font-semibold">Dashboard</h1>
        <p className="mt-3 text-slate-600">Your personalized space for recent chats, bookings, and action plan tracking.</p>
        <div className="mt-8 grid gap-6 sm:grid-cols-3">
          <div className="rounded-3xl bg-slate-50 p-6">
            <h2 className="font-semibold">Upcoming Bookings</h2>
            <p className="mt-3 text-sm text-slate-600">View the booked sessions and e-meet links.</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-6">
            <h2 className="font-semibold">Action Plans</h2>
            <p className="mt-3 text-sm text-slate-600">Track goals, milestones, and next steps from AI planning.</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-6">
            <h2 className="font-semibold">Recent Chats</h2>
            <p className="mt-3 text-sm text-slate-600">Review AI recommendations from your latest problems.</p>
          </div>
        </div>
      </div>
    </main>
  )
}
