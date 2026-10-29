import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api, endpoints } from "../../../api/client";
import { Card, CardHeader, Button, Badge, EmptyState, Select, Input } from "../../../components/ui";

export function ChecklistPage() {
  const qc = useQueryClient();
  const [labId, setLabId] = useState("");
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [items, setItems] = useState<{ item: string; required: boolean; result: string }[]>([
    { item: "PC menyala & boot", required: true, result: "pass" },
    { item: "Monitor berfungsi", required: true, result: "pass" },
    { item: "Proyektor menyala", required: true, result: "pass" },
    { item: "AC berfungsi", required: true, result: "pass" },
    { item: "Jaringan internet", required: true, result: "pass" },
    { item: "Keyboard & mouse", required: false, result: "pass" },
  ]);

  const { data: labs } = useQuery({ queryKey: ["labs"], queryFn: async () => (await api.get(endpoints.inventory.labs)).data });
  const { data: checklists } = useQuery({ queryKey: ["checklists", labId], queryFn: async () => (await api.get(endpoints.inventory.checklists, { params: labId ? { lab_id: labId } : {} })).data });

  const createMut = useMutation({
    mutationFn: async () => (await api.post(endpoints.inventory.checklists, { lab_id: labId, date, items })).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["checklists"] }),
  });

  const toggleItem = (idx: number) => {
    const next = [...items];
    next[idx].result = next[idx].result === "pass" ? "fail" : "pass";
    setItems(next);
  };

  const score = items.length ? Math.round((items.filter((i) => i.result === "pass").length / items.length) * 100) : 0;
  const criticalOk = items.filter((i) => i.required).every((i) => i.result === "pass");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Checklist Kesiapan Lab</h1>
        <p className="text-slate-500 mt-1">Pemeriksaan pra-praktikum per ruang + tanggal</p>
      </div>

      <Card className="p-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
          <Select label="Lab" value={labId} onChange={(e) => setLabId(e.target.value)}>
            <option value="">Pilih lab</option>
            {(labs || []).map((l: any) => <option key={l.id} value={l.id}>{l.canonical_name}</option>)}
          </Select>
          <Input label="Tanggal" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>

        <div className="space-y-2">
          {items.map((it, idx) => (
            <div key={idx} className="flex items-center justify-between border border-slate-100 rounded-lg px-3 py-2">
              <div className="flex items-center gap-2">
                <input type="checkbox" checked={it.result === "pass"} onChange={() => toggleItem(idx)} className="w-4 h-4" />
                <span className={it.result === "pass" ? "" : "text-red-600"}>{it.item}</span>
                {it.required && <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">wajib</span>}
              </div>
              <span className={`text-xs font-medium ${it.result === "pass" ? "text-green-600" : "text-red-600"}`}>
                {it.result === "pass" ? "Lulus" : "Gagal"}
              </span>
            </div>
          ))}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm">
            Skor: <span className="font-bold">{score}%</span> · Item wajib: {criticalOk ? <span className="text-green-600 font-semibold">semua lulus</span> : <span className="text-red-600 font-semibold">ada yang gagal</span>}
            <div className="text-xs text-slate-500 mt-1">Kesiapan = {score >= 90 && criticalOk ? "SIAP" : "TIDAK SIAP"} (BR-02)</div>
          </div>
          <Button onClick={() => createMut.mutate()} disabled={!labId || createMut.isPending}>Simpan Checklist</Button>
        </div>
      </Card>

      <Card>
        <CardHeader title="Riwayat Checklist" />
        {(checklists || []).length === 0 ? (
          <EmptyState icon="https://img.icons8.com/color/48/checklist.png" title="Belum ada checklist" desc="Buat checklist pertama di atas" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500">
                <tr><th className="text-left px-5 py-3">Tanggal</th><th className="text-left px-5 py-3">Skor</th><th className="text-left px-5 py-3">Kesimpulan</th></tr>
              </thead>
              <tbody>
                {(checklists || []).map((c: any) => (
                  <tr key={c.id} className="border-t border-slate-100">
                    <td className="px-5 py-3">{c.date}</td>
                    <td className="px-5 py-3">{c.score}%</td>
                    <td className="px-5 py-3"><Badge color={c.conclusion === "siap" ? "green" : "red"}>{c.conclusion}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}