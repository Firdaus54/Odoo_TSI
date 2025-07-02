from odoo import models, fields, api

class WorkflowTracker(models.Model):
    _name = 'workflow.tracker'
    _description = 'Workflow Tracker'

    name = fields.Char(string="Nama Proses", required=True)
    current_step = fields.Selection([
        ("pendaftaran_akreditasi", "Pendaftaran Akreditasi"),
        ("submit_dokumen_permohonan", "Submit Dokumen Permohonan"),
        ("audit_kelayakan", "Audit Kelayakan"),
        ("kaji_ulang_permohonan", "Kaji Ulang Permohonan Asesmen (KUPA)"),
        ("pembayaran_biaya_permohonan", "Pembayaran Biaya Permohonan"),
        ("persetujuan_tim_kontrak", "Persetujuan Tim dan Kontrak"),
        ("audit_kecukupan", "Audit Kecukupan"),
        ("surat_info_tagihan", "Surat Info dan Tagihan Asesmen"),
        ("registrasi_pembayaran", "Registrasi Pembayaran Asesmen"),
        ("surat_tugas_asesmen", "Surat Tugas Asesmen"),
        ("input_tim", "Input Tim"),
        ("pelaksanaan_asesmen", "Pelaksanaan Asesmen"),
        ("tindakan_perbaikan", "Tindakan Perbaikan dan Verifikasi Tindakan Perbaikan"),
        ("laporan_asesmen", "Laporan Asesmen"),
        ("rekomendasi_ruang_lingkup", "Rekomendasi Ruang Lingkup oleh Asesor"),
        ("evaluasi_hasil_asesmen", "Evaluasi Hasil Asesmen"),
        ("rapat_kajian_panitia_teknis", "Rapat Kajian Panitia Teknis"),
        ("rapat_kan_council", "Rapat KAN Council"),
        ("surat_keputusan_akreditasi", "Surat Keputusan Akreditasi"),
        ("penerbitan_sertifikat", "Penerbitan Sertifikat Akreditasi"),
        ("penerbitan_lampiran", "Penerbitan Lampiran Akreditasi"),
    ], string="Tahapan Saat Ini", default="pendaftaran_akreditasi")

    def next_step(self):
        """Pindah ke tahapan berikutnya."""
        step_keys = [step[0] for step in self._fields['current_step'].selection]
        for record in self:
            if record.current_step:
                current_index = step_keys.index(record.current_step)
                if current_index < len(step_keys) - 1:
                    record.current_step = step_keys[current_index + 1]

    def previous_step(self):
        """Kembali ke tahapan sebelumnya."""
        step_keys = [step[0] for step in self._fields['current_step'].selection]
        for record in self:
            if record.current_step:
                current_index = step_keys.index(record.current_step)
                if current_index > 0:
                    record.current_step = step_keys[current_index - 1]