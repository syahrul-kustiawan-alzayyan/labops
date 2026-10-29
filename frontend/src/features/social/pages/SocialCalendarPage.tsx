import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api, endpoints } from "../../../api/client";
import { Card, CardHeader, Button, Badge, EmptyState, Input, Select, Textarea } from "../../../components/ui";

const STATUS_COLOR: Record<string, string> = { Ide: "slate", Draf: "slate", Disetujui: "purple", Terjadwal: "blue", Terposting: "green", Ditunda: "amber", Dibatalkan: "red" };

export function SocialCalendarPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [showMigrate, setShowMigrate] = useState(false);
  const [migrateJson, setMigrateJson] = useState("");

  const migrateMut = useMutation({
    mutationFn: async (rows: any[]) => (await api.post(endpoints.social.migrate, { rows })).data,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["contents"] }); setShowMigrate(false); setMigrateJson(""); },
  });
  const [selected, setSelected] = useState<any>(null);
  const [checklistItems, setChecklistItems] = useState<{ label: string; checked: boolean }[]>([
    { label: "Caption final", checked: false },
    { label: "Aset sesuai rasio platform", checked: false },
    { label: "Hashtag & tag akun", checked: false },
    { label: "Ajakan bertindak", checked: false },
    { label: "Tautan", checked: false },
    { label: "Disclaimer", checked: false },
  ]);
  const [scheduleDate, setScheduleDate] = useState("");
  const [scheduleTime, setScheduleTime] = useState("10:00");
  const [form, setForm] = useState({ title: "", account_id: "", caption: "" });

  const { data: accounts } = useQuery({ queryKey: ["social-accounts"], queryFn: async () => (await api.get(endpoints.social.accounts)).data });
  const { data: contents, isLoading } = useQuery({ queryKey: ["contents"], queryFn: async () => (await api.get(endpoints.social.contents)).data });
  const { data: checklist } = useQuery({ queryKey: ["checklist", selected?.id], queryFn: async () => (await api.get(endpoints.social.checklist(selected.id))).data, enabled: !!selected });
  const { data: dueList } = useQuery({ queryKey: ["due"], queryFn: async () => (await api.get(endpoints.social.due)).data });

  const createMut = useMutation({ mutationFn: async (d: any) => (await api.post(endpoints.social.contents, d)).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["contents"] }); setShowForm(false); setForm({ title: "", account_id: "", caption: "" }); } });
  const approveMut = useMutation({ mutationFn: async (id: string) => (await api.post(endpoints.social.approve(id), {})).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["contents"] }); qc.invalidateQueries({ queryKey: ["checklist"] }); } });
  const scheduleMut = useMutation({ mutationFn: async ({ id, date, time }: any) => (await api.post(endpoints.social.schedule(id), { date, time })).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["contents"] }); } });
  const markPostedMut = useMutation({ mutationFn: async (id: string) => (await api.post(endpoints.social.markPosted(id), {})).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["contents"] }); } });
  const reopenMut = useMutation({ mutationFn: async (id: string) => (await api.post(endpoints.social.reopen(id), {})).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["contents"] }); setSelected(null); } });
  const cancelMut = useMutation({ mutationFn: async ({ id, reason }: any) => (await api.post(endpoints.social.cancel(id), { reason })).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["contents"] }); setSelected(null); } });
  const checklistMut = useMutation({ mutationFn: async ({ id, items }: any) => (await api.put(endpoints.social.checklist(id), { items })).data, onSuccess: () => qc.invalidateQueries({ queryKey: ["checklist"] }) });

  // sync checklist from server
  const items = checklist?.items?.length ? checklist.items.map((i: any) => ({ label: i.label || i.item, checked: !!i.checked })) : checklistItems;

  const allChecked = items.length > 0 && items.every((i: any) => i.checked);

  const handleCheck = (idx: number) => {
    const next = items.map((it: any, i: number) => i === idx ? { ...it, checked: !it.checked } : it);
    setChecklistItems(next);
    if (selected) checklistMut.mutate({ id: selected.id, items: next });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Media Sosial — 4 Akun Resmi</h1>
          <p className="text-slate-500 mt-1">Perencanaan, penjadwalan, dan arsip konten</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <img src="https://img.icons8.com/color/20/plus.png" alt="" className="w-4 h-4" /> Ide Konten
        </Button>
        <Button variant="secondary" onClick={() => setShowMigrate(true)}>Migrasi dari Excel</Button>
      </div>

      {showForm && (
        <Card className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Input label="Judul" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <Select label="Akun" value={form.account_id} onChange={(e) => setForm({ ...form, account_id: e.target.value })}>
              <option value="">Pilih akun</option>
              {(accounts || []).map((a: any) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </Select>
            <div className="md:col-span-2">
              <Textarea label="Caption (draf)" value={form.caption} onChange={(e: any) => setForm({ ...form, caption: e.target.value })} rows={3} />
            </div>
          </div>
          <div className="mt-3 flex gap-2">
            <Button onClick={() => createMut.mutate({ ...form, status: "Draf" })} disabled={createMut.isPending}>Simpan Draf</Button>
            <Button variant="secondary" onClick={() => setShowForm(false)}>Batal</Button>
          </div>
        </Card>
      )}

      {/* Konten terlambat */}
      {(dueList || []).length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
          ⚠ {(dueList || []).length} konten terlambat — perlu ditindaklanjuti.
        </div>
      )}

      <Card>
        <CardHeader title="Daftar Konten" />
        {isLoading ? <div className="p-8 text-center text-slate-400">Memuat...</div> : (
          (contents || []).length === 0
            ? <EmptyState icon="https://img.icons8.com/color/48/instagram-new.png" title="Belum ada konten" desc="Buat ide konten untuk memulai" />
            : <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 text-slate-500">
                    <tr><th className="text-left px-5 py-3">Judul</th><th className="text-left px-5 py-3">Status</th><th className="text-left px-5 py-3">Jadwal</th><th className="text-left px-5 py-3">Aksi</th></tr>
                  </thead>
                  <tbody>
                    {(contents || []).map((c: any) => (
                      <tr key={c.id} className="border-t border-slate-100 hover:bg-slate-50 cursor-pointer" onClick={() => setSelected(c)}>
                        <td className="px-5 py-3 font-medium">{c.title}</td>
                        <td className="px-5 py-3"><Badge color={STATUS_COLOR[c.status] || "slate"}>{c.status}</Badge></td>
                        <td className="px-5 py-3 text-slate-500 text-xs">{c.scheduled_date ? new Date(c.scheduled_date).toLocaleDateString("id-ID") : "Belum dijadwalkan"}</td>
                        <td className="px-5 py-3" onClick={(e) => e.stopPropagation()}>
                          {c.status === "Draf" && <button className="text-blue-600 text-xs mr-2" onClick={() => approveMut.mutate(c.id)}>Setujui</button>}
                          {c.status === "Disetujui" && <button className="text-blue-600 text-xs mr-2" onClick={() => { const d = prompt("Tanggal (YYYY-MM-DD)"); const t = prompt("Jam (HH:MM)"); if (d && t) scheduleMut.mutate({ id: c.id, date: d, time: t }); }}>Jadwalkan</button>}
                          {c.status === "Terjadwal" && <button className="text-green-600 text-xs mr-2" onClick={() => markPostedMut.mutate(c.id)}>Sudah Diposting</button>}
                          {c.status === "Terposting" && <button className="text-purple-600 text-xs mr-2" onClick={() => reopenMut.mutate(c.id)}>Buka Kembali (revisi)</button>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
        )}
      </Card>

      {/* Migrasi modal */}
      {showMigrate && (
        <Card className="p-5">
          <h3 className="font-semibold mb-2">Migrasi Kalender Konten Lama</h3>
          <p className="text-xs text-slate-500 mb-3">Tempel JSON array baris dari kalender Excel lama (kolom: Konten/Kegiatan, Tanggal, Status, Target, Keterangan). Migrasi deterministik (PRD 6.7.2).</p>
          <textarea className="w-full border rounded-lg px-3 py-2 text-xs font-mono" rows={6} value={migrateJson} onChange={(e) => setMigrateJson(e.target.value)} placeholder='[{"Konten/Kegiatan":"Ucapan wisuda","Tanggal":"15/12/2021","Status":"Menunggu Konfirmasi","Keterangan":"Menunggu"}]' />
          <div className="mt-3 flex gap-2">
            <Button onClick={() => { try { const rows = JSON.parse(migrateJson); migrateMut.mutate(rows); } catch { alert("JSON tidak valid"); } }} disabled={migrateMut.isPending}>Migrasi</Button>
            <Button variant="secondary" onClick={() => { setShowMigrate(false); setMigrateJson(""); }}>Batal</Button>
          </div>
        </Card>
      )}

      {/* Detail drawer */}
      {selected && (
        <div className="fixed inset-0 z-40 flex justify-end" onClick={() => setSelected(null)}>
          <div className="absolute inset-0 bg-black/30" />
          <div className="relative w-full max-w-lg bg-white h-full overflow-y-auto p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">{selected.title}</h2>
              <button onClick={() => setSelected(null)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>
            <div className="space-y-2 text-sm mb-4">
              <div><span className="text-slate-500">Status:</span> <Badge color={STATUS_COLOR[selected.status]}>{selected.status}</Badge></div>
              <div><span className="text-slate-500">Jadwal:</span> {selected.scheduled_date ? new Date(selected.scheduled_date).toLocaleDateString("id-ID") : "Belum"}</div>
            </div>

            <h3 className="font-semibold text-sm mb-2">Checklist Kelengkapan</h3>
            <div className="space-y-1 mb-3">
              {items.map((it: any, idx: number) => (
                <label key={idx} className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={it.checked} onChange={() => handleCheck(idx)} className="w-4 h-4" />
                  {it.label}
                </label>
              ))}
            </div>
            <div className="text-xs text-slate-500 mb-3">Progres: {items.filter((i: any) => i.checked).length}/{items.length} {allChecked ? "✓ siap disetujui" : ""}</div>

            <div className="flex flex-wrap gap-2">
              {selected.status === "Draf" && (
                <Button size="sm" onClick={() => approveMut.mutate(selected.id)} disabled={!allChecked || approveMut.isPending}>Setujui (self-approval)</Button>
              )}
              {selected.status === "Disetujui" && (
                <>
                  <Input type="date" value={scheduleDate} onChange={(e) => setScheduleDate(e.target.value)} />
                  <Input type="time" value={scheduleTime} onChange={(e) => setScheduleTime(e.target.value)} />
                  <Button size="sm" onClick={() => scheduleMut.mutate({ id: selected.id, date: scheduleDate, time: scheduleTime })} disabled={!scheduleDate || scheduleMut.isPending}>Jadwalkan</Button>
                </>
              )}
              {selected.status === "Terjadwal" && (
                <Button size="sm" onClick={() => markPostedMut.mutate(selected.id)} disabled={markPostedMut.isPending}>Sudah Diposting</Button>
              )}
              {selected.status === "Terposting" && (
                <Button size="sm" variant="secondary" onClick={() => reopenMut.mutate(selected.id)}>Buka Kembali (revisi baru)</Button>
              )}
              {!["Terposting", "Dibatalkan"].includes(selected.status) && (
                <Button size="sm" variant="danger" onClick={() => { const r = prompt("Alasan batal"); if (r) cancelMut.mutate({ id: selected.id, reason: r }); }}>Batalkan</Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}