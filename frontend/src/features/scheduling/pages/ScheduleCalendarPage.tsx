import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api, endpoints } from "../../../api/client";
import { Card, CardHeader, Button, EmptyState, Select, Input } from "../../../components/ui";

const DAYS = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab"];

function parseCSV(text: string): Record<string, string>[] {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const header = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""));
  const rows: Record<string, string>[] = [];
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    const cols: string[] = [];
    let cur = "", inQ = false;
    for (const ch of lines[i]) {
      if (ch === '"') inQ = !inQ;
      else if (ch === "," && !inQ) { cols.push(cur); cur = ""; }
      else cur += ch;
    }
    cols.push(cur);
    const row: Record<string, string> = {};
    header.forEach((h, idx) => { row[h] = (cols[idx] || "").trim(); });
    rows.push(row);
  }
  return rows;
}

export function ScheduleCalendarPage() {
  const qc = useQueryClient();
  const [labId, setLabId] = useState("");
  const [prodi, setProdi] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [importRows, setImportRows] = useState<Record<string, string>[]>([]);
  const [importResult, setImportResult] = useState<any>(null);
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [warnings, setWarnings] = useState<any[]>([]);
  const [editSession, setEditSession] = useState<any>(null);
  const [cancelSession, setCancelSession] = useState<any>(null);
  const [cancelReason, setCancelReason] = useState("");
  const [editForm, setEditForm] = useState<any>({});
  const [form, setForm] = useState({ lab_id: "", course_id: "", class_id: "", lecturer_ids: "", day_of_week: "0", start_time: "08.00", end_time: "10.30", week_start: "1", week_end: "16", student_count: "30", override_reason: "" });

  const { data: labs } = useQuery({ queryKey: ["labs"], queryFn: async () => (await api.get(endpoints.inventory.labs)).data });
  const { data: courses } = useQuery({ queryKey: ["courses"], queryFn: async () => (await api.get(endpoints.scheduling.courses)).data });
  const { data: classes } = useQuery({ queryKey: ["classes"], queryFn: async () => (await api.get(endpoints.scheduling.classes)).data });
  const { data: sessions, isLoading } = useQuery({
    queryKey: ["sessions", labId, prodi],
    queryFn: async () => (await api.get(endpoints.scheduling.sessions, { params: { ...(labId ? { lab_id: labId } : {}), ...(prodi ? { prodi } : {}) } })).data,
  });

  const validateMut = useMutation({ mutationFn: async (d: any) => (await api.post(endpoints.scheduling.validate, d)).data, onSuccess: (d) => { setConflicts(d.conflicts || []); setWarnings(d.warnings || []); } });
  const createMut = useMutation({ mutationFn: async (d: any) => (await api.post(endpoints.scheduling.sessions, d)).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["sessions"] }); setShowForm(false); setConflicts([]); setWarnings([]); } });
  const updateMut = useMutation({ mutationFn: async ({ id, data }: any) => (await api.put(`/scheduling/sessions/${id}`, data)).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["sessions"] }); setEditSession(null); } });
  const cancelMut = useMutation({ mutationFn: async ({ id, reason }: any) => (await api.post(`/scheduling/sessions/${id}/cancel`, { reason })).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["sessions"] }); setCancelSession(null); setCancelReason(""); } });
  const publishMut = useMutation({ mutationFn: async (sid: string) => (await api.post(endpoints.scheduling.publish, { semester_id: sid })).data, onSuccess: () => alert("Jadwal diterbitkan") });
  const importMut = useMutation({ mutationFn: async (rows: any[]) => (await api.post("/scheduling/sessions/import", { rows })).data, onSuccess: (d) => setImportResult(d) });

  const buildPayload = (f: any) => ({
    lab_id: f.lab_id, course_id: f.course_id || null, class_id: f.class_id || null,
    lecturer_ids: f.lecturer_ids ? f.lecturer_ids.split(",").map((s: string) => s.trim()) : [],
    day_of_week: parseInt(f.day_of_week), start_time: f.start_time.replace(".", ":"),
    end_time: f.end_time.replace(".", ":"), week_start: parseInt(f.week_start), week_end: parseInt(f.week_end),
    student_count: parseInt(f.student_count) || 0, override_reason: f.override_reason || null,
  });

  const grouped: Record<number, any[]> = { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [] };
  (sessions || []).forEach((s: any) => { if (grouped[s.day_of_week] !== undefined) grouped[s.day_of_week].push(s); });

  const openEdit = (s: any) => {
    setEditSession(s);
    setEditForm({ lab_id: s.lab_id, course_id: s.course_id || "", class_id: s.class_id || "", day_of_week: String(s.day_of_week), start_time: s.start?.slice(0, 5).replace(":", ".") || "08.00", end_time: s.end?.slice(0, 5).replace(":", ".") || "10.30", week_start: s.week_start, week_end: s.week_end, student_count: s.student_count, override_reason: "", reason: "" });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Kalender Penjadwalan Lab</h1>
          <p className="text-slate-500 mt-1">Sesi penggunaan lab per ruang dan hari</p>
        </div>
        <div className="flex gap-2">
          <Select value={labId} onChange={(e) => setLabId(e.target.value)}>
            <option value="">Semua ruang</option>
            {(labs || []).map((l: any) => <option key={l.id} value={l.id}>{l.canonical_name}</option>)}
          </Select>
          <Select value={prodi} onChange={(e) => setProdi(e.target.value)}>
            <option value="">Semua prodi</option>
            <option value="TI">Teknik Informatika</option>
            <option value="SI">Sistem Informasi</option>
            <option value="PS">Pascasarjana</option>
          </Select>
          <Button variant="secondary" onClick={() => setShowImport(true)}>Impor CSV</Button>
          <Button variant="secondary" onClick={() => window.open("/api/v1/scheduling/export/schedule")}>Ekspor CSV</Button>
          <Button variant="secondary" onClick={() => window.open("/api/v1/scheduling/export/schedule/pdf")}>Ekspor PDF</Button>
          <Button onClick={() => setShowForm(!showForm)}>
            <img src="https://img.icons8.com/color/20/plus.png" alt="" className="w-4 h-4" /> Tambah Sesi
          </Button>
        </div>
      </div>

      {showForm && (
        <Card className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <Select label="Ruang" value={form.lab_id} onChange={(e) => setForm({ ...form, lab_id: e.target.value })}>
              <option value="">Pilih ruang</option>
              {(labs || []).map((l: any) => <option key={l.id} value={l.id}>{l.canonical_name}</option>)}
            </Select>
            <Select label="Hari" value={form.day_of_week} onChange={(e) => setForm({ ...form, day_of_week: e.target.value })}>
              {DAYS.map((d, i) => <option key={i} value={i}>{d}</option>)}
            </Select>
            <Input label="Jam mulai (HH.MM)" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} />
            <Input label="Jam selesai (HH.MM)" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} />
            <Select label="Mata Kuliah" value={form.course_id} onChange={(e) => setForm({ ...form, course_id: e.target.value })}>
              <option value="">Pilih MK</option>
              {(courses || []).map((c: any) => <option key={c.id} value={c.id}>{c.code} - {c.name}</option>)}
            </Select>
            <Select label="Kelas" value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })}>
              <option value="">Pilih kelas</option>
              {(classes || []).map((c: any) => <option key={c.id} value={c.id}>{c.code}</option>)}
            </Select>
            <Input label="ID Dosen (pisah koma)" value={form.lecturer_ids} onChange={(e) => setForm({ ...form, lecturer_ids: e.target.value })} placeholder="uuid1,uuid2" />
            <Input label="Jumlah mahasiswa" type="number" value={form.student_count} onChange={(e) => setForm({ ...form, student_count: e.target.value })} />
            <Input label="Rentang minggu (mulai)" type="number" value={form.week_start} onChange={(e) => setForm({ ...form, week_start: e.target.value })} />
            <Input label="Rentang minggu (selesai)" type="number" value={form.week_end} onChange={(e) => setForm({ ...form, week_end: e.target.value })} />
          </div>
          <div className="mt-3 flex gap-2">
            <Button variant="secondary" onClick={() => validateMut.mutate(buildPayload(form))} disabled={validateMut.isPending}>Cek Konflik</Button>
            <Button onClick={() => createMut.mutate(buildPayload(form))} disabled={createMut.isPending || conflicts.length > 0}>Simpan Sesi</Button>
            <Button variant="ghost" onClick={() => { setShowForm(false); setConflicts([]); setWarnings([]); }}>Batal</Button>
          </div>
          {conflicts.length > 0 && (
            <div className="mt-3 bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
              <div className="font-semibold mb-1">Bentrok terdeteksi — tidak dapat disimpan:</div>
              <ul className="text-xs space-y-1">{conflicts.map((c, i) => <li key={i}>{c.reason}: {c.detail || c.session_id}</li>)}</ul>
            </div>
          )}
          {warnings.length > 0 && conflicts.length === 0 && (
            <div className="mt-3 bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-700">
              <div className="font-semibold mb-1">Peringatan (dapat di-override dengan alasan):</div>
              <ul className="text-xs space-y-1">{warnings.map((w, i) => <li key={i}>{w.reason} (jeda {w.gap} menit)</li>)}</ul>
              <Input label="Alasan override" value={form.override_reason} onChange={(e) => setForm({ ...form, override_reason: e.target.value })} className="mt-2" />
            </div>
          )}
        </Card>
      )}

      {/* Impor modal */}
      {showImport && (
        <Card className="p-5">
          <h3 className="font-semibold mb-2">Impor Jadwal dari CSV</h3>
          <p className="text-xs text-slate-500 mb-3">Kolom: lab_alias, day, start_time, end_time, week_start, week_end, course_code, class_code, lecturer, student_count, type. Lihat template: workflow/templates/schedule_import.csv</p>
          <textarea className="w-full border rounded-lg px-3 py-2 text-xs font-mono" rows={6} placeholder="lab_alias,day,start_time,end_time,week_start,week_end,course_code,class_code,lecturer,student_count,type" onChange={(e) => {
            const rows = parseCSV(e.target.value);
            setImportRows(rows);
          }} />
          {importRows.length > 0 && <div className="text-sm mt-2">{importRows.length} baris terbaca</div>}
          <div className="mt-3 flex gap-2">
            <Button onClick={() => importMut.mutate(importRows)} disabled={importMut.isPending || importRows.length === 0}>Commit Impor</Button>
            <Button variant="secondary" onClick={() => { setShowImport(false); setImportRows([]); setImportResult(null); }}>Batal</Button>
          </div>
          {importResult && (
            <div className="mt-3 bg-slate-50 rounded-lg p-3 text-sm">
              <div className="font-medium">Hasil: {importResult.success} sukses, {importResult.failed} gagal dari {importResult.total}</div>
              {importResult.errors?.length > 0 && (
                <ul className="mt-2 text-xs text-red-600 space-y-1 max-h-40 overflow-auto">
                  {importResult.errors.map((e: any, i: number) => <li key={i}>Baris {e.row}: {e.message}</li>)}
                </ul>
              )}
            </div>
          )}
        </Card>
      )}

      {/* Edit session modal */}
      {editSession && (
        <Card className="p-5">
          <h3 className="font-semibold mb-3">Ubah Sesi</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <Select label="Ruang" value={editForm.lab_id} onChange={(e) => setEditForm({ ...editForm, lab_id: e.target.value })}>
              {(labs || []).map((l: any) => <option key={l.id} value={l.id}>{l.canonical_name}</option>)}
            </Select>
            <Select label="Hari" value={editForm.day_of_week} onChange={(e) => setEditForm({ ...editForm, day_of_week: e.target.value })}>
              {DAYS.map((d, i) => <option key={i} value={i}>{d}</option>)}
            </Select>
            <Input label="Jam mulai" value={editForm.start_time} onChange={(e) => setEditForm({ ...editForm, start_time: e.target.value })} />
            <Input label="Jam selesai" value={editForm.end_time} onChange={(e) => setEditForm({ ...editForm, end_time: e.target.value })} />
            <Input label="Rentang minggu (mulai)" type="number" value={editForm.week_start} onChange={(e) => setEditForm({ ...editForm, week_start: e.target.value })} />
            <Input label="Rentang minggu (selesai)" type="number" value={editForm.week_end} onChange={(e) => setEditForm({ ...editForm, week_end: e.target.value })} />
            <Input label="Jumlah mahasiswa" type="number" value={editForm.student_count} onChange={(e) => setEditForm({ ...editForm, student_count: e.target.value })} />
            <Input label="Alasan perubahan (wajib)" value={editForm.reason} onChange={(e) => setEditForm({ ...editForm, reason: e.target.value })} />
          </div>
          <div className="mt-3 flex gap-2">
            <Button onClick={() => updateMut.mutate({ id: editSession.id, data: editForm })} disabled={!editForm.reason || updateMut.isPending}>Simpan Perubahan</Button>
            <Button variant="secondary" onClick={() => setEditSession(null)}>Batal</Button>
          </div>
        </Card>
      )}

      {/* Cancel modal */}
      {cancelSession && (
        <Card className="p-5">
          <h3 className="font-semibold mb-2">Batalkan Sesi</h3>
          <p className="text-sm text-slate-500 mb-3">Sesi akan dibatalkan dengan alasan (wajib).</p>
          <Input label="Alasan pembatalan" value={cancelReason} onChange={(e) => setCancelReason(e.target.value)} />
          <div className="mt-3 flex gap-2">
            <Button variant="danger" onClick={() => cancelMut.mutate({ id: cancelSession.id, reason: cancelReason })} disabled={!cancelReason || cancelMut.isPending}>Batalkan Sesi</Button>
            <Button variant="secondary" onClick={() => { setCancelSession(null); setCancelReason(""); }}>Batal</Button>
          </div>
        </Card>
      )}

      <Card>
        <CardHeader title="Kalender Mingguan" action={
          <div className="flex gap-2">
            <Button size="sm" variant="secondary" onClick={() => { const sid = prompt("Semester ID untuk diterbitkan"); if (sid) publishMut.mutate(sid); }}>Terbitkan Jadwal</Button>
          </div>
        } />
        {isLoading ? <div className="p-8 text-center text-slate-400">Memuat...</div> : (
          <div className="overflow-x-auto p-4">
            <div className="grid grid-cols-7 gap-2 min-w-[700px]">
              <div className="text-xs font-semibold text-slate-500">Jam</div>
              {DAYS.map((d) => <div key={d} className="text-xs font-semibold text-slate-500 text-center">{d}</div>)}
              {DAYS.map((_, day) => (
                <div key={day} className="space-y-1">
                  {grouped[day].length === 0
                    ? <div className="text-xs text-slate-300 text-center py-4">—</div>
                    : grouped[day].map((s: any) => (
                      <div key={s.id} className={`rounded-lg p-2 text-xs ${s.type === "maintenance" ? "bg-amber-100 text-amber-800" : "bg-blue-100 text-blue-800"}`}>
                        <div className="font-semibold">{s.start?.slice(0, 5)}–{s.end?.slice(0, 5)}</div>
                        <div className="text-[10px] opacity-80">{s.status}</div>
                        <div className="flex gap-1 mt-1">
                          <button className="text-[10px] text-blue-700" onClick={() => openEdit(s)}>Ubah</button>
                          <button className="text-[10px] text-red-700" onClick={() => setCancelSession(s)}>Batal</button>
                        </div>
                      </div>
                    ))}
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      {(!sessions || sessions.length === 0) && !isLoading && (
        <EmptyState icon="https://img.icons8.com/color/48/calendar.png" title="Belum ada sesi" desc="Tambahkan sesi atau impor jadwal dari Excel" />
      )}
    </div>
  );
}