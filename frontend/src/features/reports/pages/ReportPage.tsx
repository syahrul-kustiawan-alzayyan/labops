import { useQuery, useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { api, endpoints } from "../../../api/client";
import { Card, CardHeader, Button } from "../../../components/ui";

export function ReportPage() {
  const { data: inv } = useQuery({ queryKey: ["rep-inventory"], queryFn: async () => (await api.get(endpoints.reports.inventory)).data });
  const { data: rep } = useQuery({ queryKey: ["rep-repairs"], queryFn: async () => (await api.get(endpoints.reports.repairs)).data });
  const { data: usage } = useQuery({ queryKey: ["rep-usage"], queryFn: async () => (await api.get(endpoints.reports.usage)).data });
  const { data: social } = useQuery({ queryKey: ["rep-social"], queryFn: async () => (await api.get(endpoints.reports.social)).data });

  const [periodStart, setPeriodStart] = useState(new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0, 10));
  const [periodEnd, setPeriodEnd] = useState(new Date().toISOString().slice(0, 10));
  const [monthlyResult, setMonthlyResult] = useState<any>(null);
  const exportCSV = (name: string, data: any) => {
    const rows = Array.isArray(data) ? data : [data];
    if (rows.length === 0) return;
    const headers = Object.keys(rows[0]);
    const csv = [headers.join(","), ...rows.map((r: any) => headers.map((h) => JSON.stringify(r[h] ?? "")).join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `${name}.csv`; a.click();
    URL.revokeObjectURL(url);
  };

  const monthlyMut = useMutation({
    mutationFn: async () => (await api.post("/reports/monthly", { period_start: periodStart, period_end: periodEnd })).data,
    onSuccess: (d) => setMonthlyResult(d),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Laporan</h1>
        <p className="text-slate-500 mt-1">Rekap operasional laboratorium</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader title="Inventaris" action={<Button size="sm" variant="secondary" onClick={() => exportCSV("inventaris", inv?.by_status ? Object.entries(inv.by_status).map(([k,v])=>({status:k,jumlah:v})) : [])}>Ekspor CSV</Button>} />
          <div className="p-5 text-sm">
            <div className="text-2xl font-bold text-blue-600">{inv?.total_unit ?? 0}</div>
            <div className="text-slate-500 text-xs mb-3">Total unit tercatat</div>
            <div className="space-y-1">
              {Object.entries(inv?.by_status || {}).map(([k, v]) => (
                <div key={k} className="flex justify-between text-xs"><span>{k}</span><span className="font-medium">{String(v)}</span></div>
              ))}
            </div>
          </div>
        </Card>
        <Card>
          <CardHeader title="Kerusakan" />
          <div className="p-5 text-sm">
            <div className="text-2xl font-bold text-red-600">{rep?.total ?? 0}</div>
            <div className="text-slate-500 text-xs mb-3">Total tiket</div>
            <div className="space-y-1">
              {Object.entries(rep?.by_priority || {}).map(([k, v]) => (
                <div key={k} className="flex justify-between text-xs"><span>{k}</span><span className="font-medium">{String(v)}</span></div>
              ))}
            </div>
          </div>
        </Card>
        <Card>
          <CardHeader title="Penggunaan Lab" />
          <div className="p-5 text-sm">
            <div className="text-2xl font-bold text-green-600">{usage?.total_sessions ?? 0}</div>
            <div className="text-slate-500 text-xs mb-3">Total sesi ({usage?.total_minutes ?? 0} menit)</div>
          </div>
        </Card>
        <Card>
          <CardHeader title="Media Sosial" />
          <div className="p-5 text-sm">
            <div className="text-2xl font-bold text-purple-600">{social?.total ?? 0}</div>
            <div className="text-slate-500 text-xs mb-3">Total konten</div>
            <div className="space-y-1">
              {Object.entries(social?.by_status || {}).map(([k, v]) => (
                <div key={k} className="flex justify-between text-xs"><span>{k}</span><span className="font-medium">{String(v)}</span></div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-5">
        <h3 className="font-semibold mb-3">Laporan Bulanan (1 klik)</h3>
        <div className="flex flex-wrap gap-3 items-end">
          <div><label className="text-xs text-slate-500">Periode mulai</label><input type="date" className="border rounded px-2 py-1 text-sm" value={periodStart} onChange={(e) => setPeriodStart(e.target.value)} /></div>
          <div><label className="text-xs text-slate-500">Periode selesai</label><input type="date" className="border rounded px-2 py-1 text-sm" value={periodEnd} onChange={(e) => setPeriodEnd(e.target.value)} /></div>
          <Button onClick={() => monthlyMut.mutate()} disabled={monthlyMut.isPending}>Generate Laporan</Button>
        </div>
        {monthlyResult && (
          <div className="mt-4 bg-slate-50 rounded-lg p-3 text-xs">
            <div className="font-medium mb-1">Laporan dihasilkan: {monthlyResult.generated_at}</div>
            <pre className="whitespace-pre-wrap text-[10px]">{JSON.stringify(monthlyResult, null, 2).slice(0, 800)}</pre>
          </div>
        )}
      </Card>
    </div>
  );
}