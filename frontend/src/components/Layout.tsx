import { NavLink, Outlet } from "react-router-dom";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: "https://img.icons8.com/color/48/dashboard-layout.png" },
  { to: "/inventory/units", label: "Inventaris", icon: "https://img.icons8.com/color/48/box.png" },
  { to: "/inventory/checklists", label: "Checklist", icon: "https://img.icons8.com/color/48/checklist.png" },
  { to: "/repairs/tickets", label: "Kerusakan", icon: "https://img.icons8.com/color/48/maintenance.png" },
  { to: "/scheduling/calendar", label: "Penjadwalan", icon: "https://img.icons8.com/color/48/calendar.png" },
  { to: "/social/calendar", label: "Media Sosial", icon: "https://img.icons8.com/color/48/instagram-new.png" },
  { to: "/reports", label: "Laporan", icon: "https://img.icons8.com/color/48/combo-chart.png" },
];

export function Layout() {
  return (
    <div className="min-h-screen bg-slate-50 flex">
      <aside className="w-60 bg-white border-r border-slate-200 flex flex-col">
        <div className="px-5 py-6 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-lg">L</div>
            <div>
              <div className="font-bold text-slate-800">LabOps ITG</div>
              <div className="text-xs text-slate-500">Koordinator Lab</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                  isActive ? "bg-blue-50 text-blue-700" : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <img src={n.icon} alt="" className="w-5 h-5" />
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-4 py-3 border-t border-slate-100 text-xs text-slate-400">
          v1.0 &middot; Single admin
        </div>
      </aside>
      <main className="flex-1 overflow-x-hidden">
        <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
          <input
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm w-72 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Cari unit, tiket, sesi, konten..."
          />
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-600">Koordinator Lab</span>
            <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold">K</div>
          </div>
        </header>
        <div className="p-6 max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}