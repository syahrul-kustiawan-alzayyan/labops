import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./features/reports/pages/DashboardPage";
import { UnitListPage } from "./features/inventory/pages/UnitListPage";
import { ChecklistPage } from "./features/inventory/pages/ChecklistPage";
import { TicketListPage } from "./features/repairs/pages/TicketListPage";
import { ScheduleCalendarPage } from "./features/scheduling/pages/ScheduleCalendarPage";
import { SocialCalendarPage } from "./features/social/pages/SocialCalendarPage";
import { ReportPage } from "./features/reports/pages/ReportPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/inventory/units" element={<UnitListPage />} />
        <Route path="/inventory/checklists" element={<ChecklistPage />} />
        <Route path="/repairs/tickets" element={<TicketListPage />} />
        <Route path="/scheduling/calendar" element={<ScheduleCalendarPage />} />
        <Route path="/social/calendar" element={<SocialCalendarPage />} />
        <Route path="/reports" element={<ReportPage />} />
      </Route>
    </Routes>
  );
}