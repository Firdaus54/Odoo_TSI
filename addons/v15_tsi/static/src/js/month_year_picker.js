odoo.define('v15_tsi.month_year_picker', function(require) {
    "use strict";

    var FieldDate = require('web.basic_fields').FieldDate;
    var field_registry = require('web.field_registry');
    var core = require('web.core');

    var FieldMonthYear = FieldDate.extend({
        _renderEdit: function () {
            this._super.apply(this, arguments);

            var self = this;
            setTimeout(function () {
                var $input = self.$input;

                if ($input && $input.length) {
                    // Hapus datepicker lama jika ada untuk menghindari duplikasi
                    if ($input.hasClass("hasDatepicker")) {
                        $input.datepicker("destroy");
                    }

                    // Inisialisasi datepicker hanya dengan Bulan & Tahun
                    $input.datepicker({
                        format: "mm-yyyy",
                        viewMode: "months",
                        minViewMode: "months",
                        autoclose: true,
                        startView: "months",
                        maxViewMode: "years",
                        todayHighlight: true,
                        defaultViewDate: {
                            year: new Date().getFullYear(),
                            month: new Date().getMonth()
                        }
                    });

                    // Set nilai awal agar hanya MM-YYYY yang tampil
                    var currentValue = self.value;
                    if (currentValue) {
                        var formattedDate = moment(currentValue, "YYYY-MM-DD").format("MM-YYYY");
                        $input.val(formattedDate);
                    } else {
                        $input.val(moment().format("MM-YYYY"));
                    }
                } else {
                    console.error('Input element tidak ditemukan.');
                }
            }, 200); // Delay untuk memastikan elemen tersedia
        },

        _setValue: function (value) {
            if (value) {
                var parsedDate = moment(value, "DD-MM-YYYY");
                value = parsedDate.isValid() ? parsedDate.format("YYYY-MM") : value;
            }
            this._super(value);
        }
    });

    field_registry.add('month_year', FieldMonthYear);
});
