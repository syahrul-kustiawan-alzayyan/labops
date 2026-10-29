import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api, endpoints } from "../../../api/client";
import { Card, CardHeader, Button, Badge, EmptyState, Select, Textarea, Input } from "../../../components/ui";

const PRIORITY_COLOR: Record<string, string> = { "PRI-1": "red", "PRI-2": "amber", "PRI-3": "blue", "PRI-4": "slate" };

export function TicketListPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [selected, setSelected] = useState<any>(null);
  const [form, setForm] = useState({ unit_id: "", severity: "Ringan", impact: false, kronologi: "", reporter: "" });
  const [actionForm, setActionForm] = useState({ type: "internal", diagnosis: "", action: "", sparepart: "", cost: "", vendor_id: "" });
  const [verifyForm, setVerifyForm] = useState({ result: "pass", test_notes: "" });
  const [triageNote, setTriageNote] = useState("");

  const { data: tickets, isLoading } = useQuery({ queryKey: ["tickets"], queryFn: async () => (await api.get(endpoints.repairs.tickets)).data });
  const { data: ticketDetail } = useQuery({ queryKey: ["ticket", selected?.id], queryFn: async () => (await api.get(endpoints.repairs.ticket(selected.id))).data, enabled: !!selected });
  const { data: vendors } = useQuery({ queryKey: ["vendors"], queryFn: async () => (await api.get(endpoints.repairs.vendors)).data });

  const createMut = useMutation({ mutationFn: async (d: any) => (await api.post(endpoints.repairs.tickets, d)).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["tickets"] }); setShowForm(false); } });
  const triageMut = useMutation({ mutationFn: async ({ id, result, note }: any) => (await api.post(endpoints.repairs.triage(id), { result, note })).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["tickets"] }); qc.invalidateQueries({ queryKey: ["ticket"] }); } });
  const actionMut = useMutation({ mutationFn: async ({ id, data }: any) => (await api.post(endpoints.repairs.actions(id), data)).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["ticket"] }); setActionForm({ type: "internal", diagnosis: "", action: "", sparepart: "", cost: "", vendor_id: "" }); } });
  const verifyMut = useMutation({ mutationFn: async ({ id, result, test_notes }: any) => (await api.post(endpoints.repairs.verify(id), { result, test_notes })).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["tickets"] }); qc.invalidateQueries({ queryKey: ["ticket"] }); } });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Tiket Kerusakan</h1>
          <p className="text-slate-500 mt-1">Laporan kerusakan hingga verifikasi perbaikan</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <img src="https://img.icons8.com/color/20/maintenance.png" alt="" className="w-4 h-4" /> Lapor Kerusakan
        </Button>
      </div>

      {showForm && (
        <Card className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Input label="Unit ID (opsional)" value={form.unit_id} onChange={(e) => setForm({ ...form, unit_id: e.target.value })} placeholder="UUID unit" />
            <Select label="Keparahan" value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}><option>Ringan</option><option>Sedang</option><option>Berat</option><option>Kritis</option></Select>
            <Select label="Menghambat praktikum?" value={String(form.impact)} onChange={(e) => setForm({ ...form, impact: e.target.value === "true" })}><option value="false">Tidak</option><option value="true">Ya</option></Select>
            <Input label="Pelapor" value={form.reporter} onChange={(e) => setForm({ ...form, reporter: e.target.value })} />
            <div className="md:col-span-2"><Textarea label="Kronologi" value={form.kronologi} onChange={(e: any) => setForm({ ...form, kronologi: e.target.value })} rows={2} /></div>
          </div>
          <div className="mt-3 flex gap-2">
            <Button onClick={() => createMut.mutate({ ...form, unit_id: form.unit_id || null })} disabled={createMut.isPending}>Simpan Tiket</Button>
            <Button variant="secondary" onClick={() => setShowForm(false)}>Batal</Button>
          </div>
        </Card>
      )}

      <Card>
        <CardHeader title="Daftar Tiket" />
        {isLoading ? <div className="p-8 text-center text-slate-400">Memuat...</div> : (
          (tickets || []).length === 0
            ? <EmptyState icon="https://img.icons8.com/color/48/maintenance.png" title="Belum ada tiket" desc="Laporkan kerusakan untuk memulai" />
            : <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 text-slate-500">
                    <tr><th className="text-left px-5 py-3">Nomor</th><th className="text-left px-5 py-3">Keparahan</th><th className="text-left px-5 py-3">Prioritas</th><th className="text-left px-5 py-3">Status</th><th className="text-left px-5 py-3">Tenggat</th><th className="text-left px-5 py-3">Aksi</th></tr>
                  </thead>
                  <tbody>
                    {(tickets || []).map((t: any) => (
                      <tr key={t.id} className="border-t border-slate-100 hover:bg-slate-50 cursor-pointer" onClick={() => setSelected(t)}>
                        <td className="px-5 py-3 font-mono text-xs">{t.number}</td>
                        <td className="px-5 py-3">{t.severity}</td>
                        <td className="px-5 py-3"><Badge color={PRIORITY_COLOR[t.priority] || "slate"}>{t.priority}</Badge></td>
                        <td className="px-5 py-3"><Badge color={t.status === "Terverifikasi" ? "green" : t.status === "Tidak Dapat Diperbaiki" ? "red" : "amber"}>{t.status}</Badge></td>
                        <td className="px-5 py-3 text-slate-500 text-xs">{t.due_remediation_at ? new Date(t.due_remediation_at).toLocaleDateString("id-ID") : "-"}</td>
                        <td className="px-5 py-3" onClick={(e) => e.stopPropagation()}>
                          {t.status === "Dilaporkan" && <button className="text-blue-600 text-xs" onClick={() => triageMut.mutate({ id: t.id, result: "valid", note: "valid" })}>Triase</button>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
        )}
      </Card>

      {/* Detail drawer */}
      {selected && (
        <div className="fixed inset-0 z-40 flex justify-end" onClick={() => setSelected(null)}>
          <div className="absolute inset-0 bg-black/30" />
          <div className="relative w-full max-w-lg bg-white h-full overflow-y-auto p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">{ticketDetail?.number || selected.number}</h2>
              <button onClick={() => setSelected(null)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>
            <div className="space-y-2 text-sm mb-4">
              <div><span className="text-slate-500">Keparahan:</span> {ticketDetail?.severity}</div>
              <div><span className="text-slate-500">Prioritas:</span> <Badge color={PRIORITY_COLOR[ticketDetail?.priority]}>{ticketDetail?.priority}</Badge></div>
              <div><span className="text-slate-500">Status:</span> {ticketDetail?.status}</div>
              <div><span className="text-slate-500">Kronologi:</span> {ticketDetail?.kronologi || "-"}</div>
            </div>

            {/* Tindakan */}
            {ticketDetail && !["Terverifikasi", "Tidak Dapat Diperbaiki", "Duplikat", "Tidak Valid"].includes(ticketDetail.status) && (
              <div className="border-t pt-4 space-y-3">
                <h3 className="font-semibold text-sm">Tambah Tindakan</h3>
                <Select label="Jenis" value={actionForm.type} onChange={(e) => setActionForm({ ...actionForm, type: e.target.value })}>
                  <option value="internal">Internal</option><option value="vendor">Vendor</option>
                </Select>
                {actionForm.type === "vendor" && (
                  <Select label="Vendor" value={actionForm.vendor_id} onChange={(e) => setActionForm({ ...actionForm, vendor_id: e.target.value })}>
                    <option value="">Pilih vendor</option>
                    {(vendors || []).map((v: any) => <option key={v.id} value={v.id}>{v.name}</option>)}
                  </Select>
                )}
                <Input label="Diagnosa" value={actionForm.diagnosis} onChange={(e) => setActionForm({ ...actionForm, diagnosis: e.target.value })} />
                <Input label="Tindakan" value={actionForm.action} onChange={(e) => setActionForm({ ...actionForm, action: e.target.value })} />
                <Input label="Suku Cadang" value={actionForm.sparepart} onChange={(e) => setActionForm({ ...actionForm, sparepart: e.target.value })} />
                <Input label="Biaya (Rp)" type="number" value={actionForm.cost} onChange={(e) => setActionForm({ ...actionForm, cost: e.target.value })} />
                <Button size="sm" onClick={() => actionMut.mutate({ id: selected.id, data: { ...actionForm, cost: actionForm.cost ? parseFloat(actionForm.cost) : null, vendor_id: actionForm.vendor_id || null } })} disabled={actionMut.isPending}>Simpan Tindakan</Button>
              </div>
            )}

            {/* Verifikasi */}
            {ticketDetail && ["Ditriase", "Dalam Perbaikan", "Selesai Diperbaiki", "Menunggu Suku Cadang/Vendor"].includes(ticketDetail.status) && (
              <div className="border-t pt-4 space-y-3 mt-4">
                <h3 className="font-semibold text-sm">Verifikasi Akhir</h3>
                <Select label="Hasil" value={verifyForm.result} onChange={(e) => setVerifyForm({ ...verifyForm, result: e.target.value })}>
                  <option value="pass">Lulus (unit Siap Pakai)</option>
                  <option value="fail">Gagal (unit Dinonaktifkan)</option>
                </Select>
                <Textarea label="Catatan uji fungsi (wajib)" value={verifyForm.test_notes} onChange={(e: any) => setVerifyForm({ ...verifyForm, test_notes: e.target.value })} rows={2} />
                <Button size="sm" onClick={() => verifyMut.mutate({ id: selected.id, result: verifyForm.result, test_notes: verifyForm.test_notes })} disabled={!verifyForm.test_notes || verifyMut.isPending}>Verifikasi</Button>
              </div>
            )}

            {/* Triase (jika Dilaporkan) */}
            {ticketDetail?.status === "Dilaporkan" && (
              <div className="border-t pt-4 space-y-3 mt-4">
                <h3 className="font-semibold text-sm">Triase</h3>
                <Textarea label="Catatan triase" value={triageNote} onChange={(e: any) => setTriageNote(e.target.value)} rows={2} />
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => triageMut.mutate({ id: selected.id, result: "valid", note: triageNote })}>Valid</Button>
                  <Button size="sm" variant="secondary" onClick={() => triageMut.mutate({ id: selected.id, result: "duplikat", note: triageNote })}>Duplikat</Button>
                  <Button size="sm" variant="danger" onClick={() => triageMut.mutate({ id: selected.id, result: "tidak_valid", note: triageNote })}>Tidak Valid</Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}