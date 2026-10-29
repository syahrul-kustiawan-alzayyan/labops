import axios from "axios";

export const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const endpoints = {
  auth: { login: "/auth/login", refresh: "/auth/refresh" },
  inventory: {
    labs: "/inventory/labs",
    components: "/inventory/components",
    units: "/inventory/units",
    unit: (id: string) => `/inventory/units/${id}`,
    unitStatus: (id: string) => `/inventory/units/${id}/status`,
    unitArchive: (id: string) => `/inventory/units/${id}/archive`,
    unitVerify: (id: string) => `/inventory/units/${id}/verify`,
    checklists: "/inventory/checklists",
    consumables: "/inventory/consumables",
  },
  repairs: {
    tickets: "/repairs/tickets",
    ticket: (id: string) => `/repairs/tickets/${id}`,
    triage: (id: string) => `/repairs/tickets/${id}/triage`,
    actions: (id: string) => `/repairs/tickets/${id}/actions`,
    verify: (id: string) => `/repairs/tickets/${id}/verify`,
    vendors: "/repairs/vendors",
  },
  scheduling: {
    labs: "/scheduling/labs",
    semesters: "/scheduling/semesters",
    lecturers: "/scheduling/lecturers",
    courses: "/scheduling/courses",
    classes: "/scheduling/classes",
    sessions: "/scheduling/sessions",
    validate: "/scheduling/sessions/validate",
    publish: "/scheduling/versions/publish",
    calendar: "/scheduling/calendar",
  },
  social: {
    accounts: "/social/accounts",
    contents: "/social/contents",
    content: (id: string) => `/social/contents/${id}`,
    checklist: (id: string) => `/social/contents/${id}/checklist`,
    approve: (id: string) => `/social/contents/${id}/approve`,
    schedule: (id: string) => `/social/contents/${id}/schedule`,
    markPosted: (id: string) => `/social/contents/${id}/mark-posted`,
    reopen: (id: string) => `/social/contents/${id}/reopen`,
    cancel: (id: string) => `/social/contents/${id}/cancel`,
    calendar: "/social/calendar",
    due: "/social/due",
    migrate: "/social/migrate",
  },
  reports: {
    dashboard: "/reports/dashboard",
    inventory: "/reports/inventory",
    repairs: "/reports/repairs",
    usage: "/reports/usage",
    social: "/reports/social",
  },
  core: {
    activityLogs: "/core/activity-logs",
    settings: "/core/settings",
    notifications: "/core/notifications",
  },
};