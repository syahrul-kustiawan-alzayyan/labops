import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useRef } from "react";
import { api, endpoints } from "../../../api/client";
import { Card, CardHeader, Button, Badge, EmptyState, Input, Select, Textarea } from "../../../components/ui";

const STATUS_COLOR: Record<string, string> = { "Siap Pakai": "green", "Perlu Perhatian": "amber", "Rusak": "red", "Dalam Perbaikan": "amber", "Dinonaktifkan": "slate", "Hilang": "red" };
const STATUSES = ["Siap Pakai", "Perlu Perhatian", "Rusak", "Dalam Perbaikan", "Dinonaktifkan", "Hilang"];

function parseCSV(text: string): Record<string, string>[] {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const header = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""));
  const rows: Record<string, string>[] = [];
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    // simple CSV parse (handle quoted fields)
    const cols: string[] = [];
    let cur = "";
    let inQ = false;
    for (const ch of lines[i]) {
      if (ch === '"') { inQ = !inQ; }
      else if (ch === "," && !inQ) { cols.push(cur); cur = ""; }
      else { cur += ch; }
    }
    cols.push(cur);
    const row: Record<string, string> = {};
    header.forEach((h, idx) => { row[h] = (cols[idx] || "").trim(); });
    rows.push(row);
  }
  return rows;
}

export function UnitListPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [filterLab, setFilterLab] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [importRows, setImportRows] = useState<Record<string, string>[]>([]);
  const [importPreview, setImportPreview] = useState<any>(null);
  const [selectedUnit, setSelectedUnit] = useState<any>(null);
  const [statusChange, setStatusChange] = useState<{ unit: any; newStatus: string; reason: string } | null>(null);
  const [archiveUnit, setArchiveUnit] = useState<{ unit: any; reason: string } | null>(null);
  const [verifyUnit, setVerifyUnit] = useState<{ unit: any; result: string; failed: string } | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const { data: units, isLoading } = useQuery({
    queryKey: ["units", search, filterLab, filterStatus],
    queryFn: async () => (await api.get(endpoints.inventory.units, { params: { search: search || undefined, lab_id: filterLab || undefined, status: filterStatus || undefined } })).data,
  });
  const { data: labs } = useQuery({ queryKey: ["labs"], queryFn: async () => (await api.get(endpoints.inventory.labs)).data });
  const { data: components } = useQuery({ queryKey: ["components"], queryFn: async () => (await api.get(endpoints.inventory.components)).data });
  const { data: unitHistory } = useQuery({
    queryKey: ["unit-history", selectedUnit?.id],
    queryFn: async () => (await api.get(`${endpoints.inventory.unit(selectedUnit.id)}/history`)).data,
    enabled: !!selectedUnit,
  });
  const { data: unitTickets } = useQuery({
    queryKey: ["unit-tickets", selectedUnit?.id],
    queryFn: async () => (await api.get(`${endpoints.inventory.unit(selectedUnit.id)}/tickets`)).data,
    enabled: !!selectedUnit,
  });

  const [form, setForm] = useState({ code: "", component_id: "", lab_id: "", brand_model: "", serial_no: "", placement: "", status: "Siap Pakai" });
  const createMut = useMutation({
    mutationFn: async (d: any) => (await api.post(endpoints.inventory.units, d)).data,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["units"] }); setShowForm(false); setForm({ code: "", component_id: "", lab_id: "", brand_model: "", serial_no: "", placement: "", status: "Siap Pakai" }); },
  });
  const statusMut = useMutation({
    mutationFn: async ({ id, status, reason }: any) => (await api.put(endpoints.inventory.unitStatus(id), { status, reason })).data,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["units"] }); setStatusChange(null); },
  });
  const archiveMut = useMutation({
    mutationFn: async ({ id, reason }: any) => (await api.post(endpoints.inventory.unitArchive(id), { reason })).data,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["units"] }); setArchiveUnit(null); },
  });
  const verifyMut = useMutation({
    mutationFn: async ({ id, result, failed_items }: any) => (await api.post(endpoints.inventory.unitVerify(id), { result, failed_items })).data,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["units"] }); setVerifyUnit(null); },
  });
  const importMut = useMutation({
    mutationFn: async (mode: string) => (await api.post(endpoints.inventory.units + "/import", { mode, rows: importRows })).data,
    onSuccess: (d) => { setImportPreview(d); if (d.batch_id) { qc.invalidateQueries({ queryKey: ["units"] }); setShowImport(false); setImportRows([]); setImportPreview(null); } },
  });

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      setImportRows(parseCSV(text));
    };
    reader.readAsText(file);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Inventaris Unit</h1>
          <p className="text-slate-500 mt-1">Daftar unit komponen lab, kondisi, dan riwayat</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => setShowImport(true)}>
            <img src="https://img.icons8.com/color/20/import.png" alt="" className="w-4 h-4" /> Impor CSV
          </Button>
          <Button onClick={() => setShowForm(!showForm)}>
            <img src="https://img.icons8.com/color/20/plus.png" alt="" className="w-4 h-4" /> Tambah Unit
          </Button>
        </div>
      </div>

      {/* Filter */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <Input placeholder="Cari kode unit..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <Select value={filterLab} onChange={(e) => setFilterLab(e.target.value)}>
            <option value="">Semua lab</option>
            {(labs || []).map((l: any) => <option key={l.id} value={l.id}>{l.canonical_name}</option>)}
          </Select>
          <Select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="">Semua status</option>
            {STATUSES.map((s) => <option key={s}>{s}</option>)}
          </Select>
          <Button variant="ghost" onClick={() => { setSearch(""); setFilterLab(""); setFilterStatus(""); }}>Reset filter</Button>
        </div>
      </Card>

      {/* Form tambah */}
      {showForm && (
        <Card className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Input label="Kode Unit" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} placeholder="C-I-01-PC-01" />
            <Select label="Komponen" value={form.component_id} onChange={(e) => setForm({ ...form, component_id: e.target.value })}>
              <option value="">Pilih komponen</option>
              {(components || []).map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </Select>
            <Select label="Lab" value={form.lab_id} onChange={(e) => setForm({ ...form, lab_id: e.target.value })}>
              <option value="">Pilih lab</option>
              {(labs || []).map((l: any) => <option key={l.id} value={l.id}>{l.canonical_name}</option>)}
            </Select>
            <Input label="Merek/Model" value={form.brand_model} onChange={(e) => setForm({ ...form, brand_model: e.target.value })} />
            <Input label="Nomor Seri" value={form.serial_no} onChange={(e) => setForm({ ...form, serial_no: e.target.value })} />
            <Input label="Titik Penempatan" value={form.placement} onChange={(e) => setForm({ ...form, placement: e.target.value })} />
            <Select label="Status Awal" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              {STATUSES.map((s) => <option key={s}>{s}</option>)}
            </Select>
          </div>
          <div className="mt-3 flex gap-2">
            <Button onClick={() => createMut.mutate(form)} disabled={createMut.isPending || !form.code || !form.component_id || !form.lab_id}>Simpan</Button>
            <Button variant="secondary" onClick={() => setShowForm(false)}>Batal</Button>
          </div>
        </Card>
      )}

      {/* Impor modal */}
      {showImport && (
        <Card className="p-5">
          <h3 className="font-semibold mb-2">Impor Unit dari CSV</h3>
          <p className="text-xs text-slate-500 mb-3">Kolom wajib: code, component, lab, condition. Lihat template di workflow/templates/units_stock_opname.csv</p>
          <input ref={fileRef} type="file" accept=".csv" onChange={handleFile} className="mb-3" />
          {importRows.length > 0 && (
            <>
              <div className="text-sm mb-2">{importRows.length} baris terbaca</div>
              <div className="flex gap-2 mb-3">
                <Button variant="secondary" onClick={() => importMut.mutate("preview")} disabled={importMut.isPending}>Preview</Button>
                <Button onClick={() => importMut.mutate("commit")} disabled={importMut.isPending || importRows.length === 0}>Commit</Button>
                <Button variant="ghost" onClick={() => { setShowImport(false); setImportRows([]); setImportPreview(null); }}>Batal</Button>
              </div>
            </>
          )}
          {importPreview && (
            <div className="bg-slate-50 rounded-lg p-3 text-sm">
              <div className="font-medium">Hasil Preview: {importPreview.valid} valid, {importPreview.invalid} gagal, {importPreview.duplicate} duplikat dari {importPreview.total} baris</div>
              {importPreview.errors?.length > 0 && (
                <ul className="mt-2 text-xs text-red-600 space-y-1 max-h-40 overflow-auto">
                  {importPreview.errors.map((e: any, i: number) => <li key={i}>Baris {e.row}: {e.field} — {e.message}</li>)}
                </ul>
              )}
            </div>
          )}
        </Card>
      )}

      {/* Daftar unit */}
      <Card>
        <CardHeader title={`Daftar Unit (${(units || []).length})`} />
        {isLoading ? <div className="p-8 text-center text-slate-400">Memuat...</div> : (
          (units || []).length === 0
            ? <EmptyState icon="https://img.icons8.com/color/48/box.png" title="Belum ada unit" desc="Tambahkan unit atau impor dari CSV" />
            : <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 text-slate-500">
                    <tr><th className="text-left px-5 py-3">Kode</th><th className="text-left px-5 py-3">Merek/Model</th><th className="text-left px-5 py-3">Status</th><th className="text-left px-5 py-3">Verifikasi</th><th className="text-left px-5 py-3">Aksi</th></tr>
                  </thead>
                  <tbody>
                    {(units || []).map((u: any) => (
                      <tr key={u.id} className="border-t border-slate-100 hover:bg-slate-50 cursor-pointer" onClick={() => setSelectedUnit(u)}>
                        <td className="px-5 py-3 font-mono text-xs">{u.code}</td>
                        <td className="px-5 py-3">{u.brand_model || "-"}</td>
                        <td className="px-5 py-3"><Badge color={STATUS_COLOR[u.status] || "slate"}>{u.status}</Badge></td>
                        <td className="px-5 py-3 text-slate-500 text-xs">{u.verified_at ? new Date(u.verified_at).toLocaleDateString("id-ID") : "Belum"}</td>
                        <td className="px-5 py-3" onClick={(e) => e.stopPropagation()}>
                          <button className="text-blue-600 text-xs mr-2" onClick={() => setStatusChange({ unit: u, newStatus: u.status, reason: "" })}>Ubah Status</button>
                          <button className="text-green-600 text-xs mr-2" onClick={() => setVerifyUnit({ unit: u, result: "pass", failed: "" })}>Verifikasi</button>
                          <button className="text-red-600 text-xs" onClick={() => setArchiveUnit({ unit: u, reason: "" })}>Arsip</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
        )}
      </Card>

      {/* Detail drawer */}
      {selectedUnit && (
        <div className="fixed inset-0 z-40 flex justify-end" onClick={() => setSelectedUnit(null)}>
          <div className="absolute inset-0 bg-black/30" />
          <div className="relative w-full max-w-md bg-white h-full overflow-y-auto p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">{selectedUnit.code}</h2>
              <button onClick={() => setSelectedUnit(null)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>
            <div className="space-y-3 text-sm">
              <div><span className="text-slate-500">Status:</span> <Badge color={STATUS_COLOR[selectedUnit.status]}>{selectedUnit.status}</Badge></div>
              <div><span className="text-slate-500">Merek/Model:</span> {selectedUnit.brand_model || "-"}</div>
              <div><span className="text-slate-500">Verifikasi terakhir:</span> {selectedUnit.verified_at ? new Date(selectedUnit.verified_at).toLocaleDateString("id-ID") : "Belum"}</div>
            </div>
            <h3 className="font-semibold mt-6 mb-2">Riwayat Kondisi</h3>
            <div className="space-y-2 text-xs">
              {(unitHistory || []).length === 0 && <div className="text-slate-400">Belum ada riwayat</div>}
              {(unitHistory || []).map((h: any) => (
                <div key={h.id} className="border-l-2 border-slate-200 pl-3 py-1">
                  <div>{h.old_status} → {h.new_status}</div>
                  <div className="text-slate-500">{h.reason || "-"} · {new Date(h.changed_at).toLocaleString("id-ID")}</div>
                </div>
              ))}
            </div>
            <h3 className="font-semibold mt-6 mb-2">Tiket Terkait</h3>
            <div className="space-y-2 text-xs">
              {(unitTickets || []).length === 0 && <div className="text-slate-400">Belum ada tiket</div>}
              {(unitTickets || []).map((t: any) => (
                <div key={t.id} className="border border-slate-100 rounded p-2">
                  <div className="font-mono">{t.number}</div>
                  <div>{t.severity} · {t.status} · {t.priority}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Ubah status modal */}
      {statusChange && (
        <div className="fixed inset-0 z-40 flex items-center justify-center" onClick={() => setStatusChange(null)}>
          <div className="absolute inset-0 bg-black/30" />
          <div className="relative bg-white rounded-xl p-6 w-full max-w-md shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-bold mb-3">Ubah Status — {statusChange.unit.code}</h3>
            <Select label="Status baru" value={statusChange.newStatus} onChange={(e) => setStatusChange({ ...statusChange, newStatus: e.target.value })}>
              {STATUSES.map((s) => <option key={s}>{s}</option>)}
            </Select>
            <div className="mt-3">
              <Textarea label="Alasan (wajib)" value={statusChange.reason} onChange={(e: any) => setStatusChange({ ...statusChange, reason: e.target.value })} rows={2} />
            </div>
            <div className="mt-4 flex gap-2">
              <Button onClick={() => statusMut.mutate({ id: statusChange.unit.id, status: statusChange.newStatus, reason: statusChange.reason })} disabled={!statusChange.reason || statusMut.isPending}>Simpan</Button>
              <Button variant="secondary" onClick={() => setStatusChange(null)}>Batal</Button>
            </div>
          </div>
        </div>
      )}

      {/* Arsip modal */}
      {archiveUnit && (
        <div className="fixed inset-0 z-40 flex items-center justify-center" onClick={() => setArchiveUnit(null)}>
          <div className="absolute inset-0 bg-black/30" />
          <div className="relative bg-white rounded-xl p-6 w-full max-w-md shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-bold mb-3">Arsipkan Unit — {archiveUnit.unit.code}</h3>
            <p className="text-sm text-slate-500 mb-3">Unit akan disembunyikan dari daftar aktif, riwayat tetap tersimpan.</p>
            <Textarea label="Alasan arsip (wajib)" value={archiveUnit.reason} onChange={(e: any) => setArchiveUnit({ ...archiveUnit, reason: e.target.value })} rows={2} />
            <div className="mt-4 flex gap-2">
              <Button variant="danger" onClick={() => archiveMut.mutate({ id: archiveUnit.unit.id, reason: archiveUnit.reason })} disabled={!archiveUnit.reason || archiveMut.isPending}>Arsipkan</Button>
              <Button variant="secondary" onClick={() => setArchiveUnit(null)}>Batal</Button>
            </div>
          </div>
        </div>
      )}

      {/* Verifikasi modal */}
      {verifyUnit && (
        <div className="fixed inset-0 z-40 flex items-center justify-center" onClick={() => setVerifyUnit(null)}>
          <div className="absolute inset-0 bg-black/30" />
          <div className="relative bg-white rounded-xl p-6 w-full max-w-md shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-bold mb-3">Verifikasi Unit — {verifyUnit.unit.code}</h3>
            <Select label="Hasil" value={verifyUnit.result} onChange={(e) => setVerifyUnit({ ...verifyUnit, result: e.target.value })}>
              <option value="pass">Lulus (Siap Pakai)</option>
              <option value="fail">Gagal (buat tiket)</option>
            </Select>
            {verifyUnit.result === "fail" && (
              <div className="mt-3">
                <Textarea label="Item yang gagal (wajib)" value={verifyUnit.failed} onChange={(e: any) => setVerifyUnit({ ...verifyUnit, failed: e.target.value })} rows={2} />
              </div>
            )}
            <div className="mt-4 flex gap-2">
              <Button onClick={() => verifyMut.mutate({ id: verifyUnit.unit.id, result: verifyUnit.result, failed_items: verifyUnit.result === "fail" ? [{ item: verifyUnit.failed }] : [] })} disabled={verifyMut.isPending}>Simpan</Button>
              <Button variant="secondary" onClick={() => setVerifyUnit(null)}>Batal</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}