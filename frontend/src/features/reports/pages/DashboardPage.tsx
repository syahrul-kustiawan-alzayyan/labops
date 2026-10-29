import { useQuery } from "@tanstack/react-query";
import { api, endpoints } from "../../../api/client";
import { Card, CardHeader, Spinner, EmptyState } from "../../../components/ui";

const ICONS = {
  box: "https://img.icons8.com/color/48/box.png",
  ticket: "https://img.icons8.com/color/48/maintenance.png",
  calendar: "https://img.icons8.com/color/48/calendar.png",
  social: "https://img.icons8.com/color/48/instagram-new.png",
};

export function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => (await api.get(endpoints.reports.dashboard)).data,
  });

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-slate-500 mt-1">Ringkasan operasional laboratorium hari ini</p>
      </div>

      {/* Kesiapan lab */}
      <Card>
        <CardHeader title="Kesiapan Lab" />
        <div className="p-5 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {(data?.kesiapan_lab || []).map((lab: any) => (
            <div key={lab.lab} className={`rounded-xl p-3 border-l-4 ${
              lab.kesimpulan === "siap" ? "border-green-500 bg-green-50" :
              lab.kesimpulan === "tidak_siap" ? "border-red-500 bg-red-50" : "border-amber-500 bg-amber-50"
            }`}>
              <div className="text-xs text-slate-500">{lab.lab}</div>
              <div className={`text-lg font-bold ${
                lab.kesimpulan === "siap" ? "text-green-600" :
                lab.kesimpulan === "tidak_siap" ? "text-red-600" : "text-amber-600"
              }`}>{lab.persen}%</div>
              <div className="text-xs text-slate-500">{lab.siap}/{lab.total_unit} unit siap</div>
              {lab.tiket_kritis > 0 && <div className="text-xs text-red-600 mt-1">{lab.tiket_kritis} tiket Kritis</div>}
            </div>
          ))}
          {(!data?.kesiapan_lab || data.kesiapan_lab.length === 0) && (
            <div className="col-span-full"><EmptyState icon={ICONS.box} title="Belum ada data lab" desc="Tambahkan lab dan unit terlebih dahulu" /></div>
          )}
        </div>
      </Card>

      {/* 3 kolom */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader title={`Tiket Terbuka (${data?.tiket_terbuka ?? 0})`} />
          <div className="p-4 space-y-2">
            {(data?.tiket_terbuka ?? 0) === 0 && <EmptyState icon={ICONS.ticket} title="Tidak ada tiket terbuka" desc="Semua tiket sudah tertangani" />}
          </div>
        </Card>
        <Card>
          <CardHeader title={`Sesi Hari Ini (${data?.sesi_hari_ini?.length ?? 0})`} />
          <div className="p-4 space-y-2">
            {(data?.sesi_hari_ini || []).map((s: any) => (
              <div key={s.id} className="border-b border-slate-100 pb-2">
                <div className="text-sm font-medium">{s.start} - {s.end}</div>
                <div className="text-xs text-slate-500">Lab {s.lab_id?.slice(0, 8)}</div>
              </div>
            ))}
            {(!data?.sesi_hari_ini || data.sesi_hari_ini.length === 0) && (
              <EmptyState icon={ICONS.calendar} title="Tidak ada sesi hari ini" desc="" />
            )}
          </div>
        </Card>
        <Card>
          <CardHeader title={`Konten Jatuh Tempo (${data?.konten_jatuh_tempo?.length ?? 0})`} />
          <div className="p-4 space-y-2">
            {(data?.konten_jatuh_tempo || []).map((c: any) => (
              <div key={c.id} className="border-b border-slate-100 pb-2">
                <div className="text-sm font-medium">{c.title}</div>
                <div className="text-xs text-slate-500">{c.date}</div>
              </div>
            ))}
            {(!data?.konten_jatuh_tempo || data.konten_jatuh_tempo.length === 0) && (
              <EmptyState icon={ICONS.social} title="Tidak ada konten jatuh tempo" desc="" />
            )}
          </div>
        </Card>
      </div>

      {data?.tiket_terlambat > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
          ⚠ {data.tiket_terlambat} tiket lewat tenggat remediasi — perlu eskalasi.
        </div>
      )}
    </div>
  );
}